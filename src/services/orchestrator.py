# src/services/orchestrator.py
"""
Agent Orchestrator - Central Router for Multi-Agent System

Manages interactions between specialized AI agents through shared memory.
Natural Language interface for p9i.

Now uses Clean Architecture:
- AgentRouter (application layer): Agent detection and prompt selection
- AgentExecutor (services layer): Prompt execution
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.services.executor import PromptExecutor
from src.services.checkpoint_executor import get_checkpoint_executor, CheckpointExecutor
from src.application.agent_router import AgentRouter, AGENTS

logger = logging.getLogger(__name__)

# Prompts directory - use relative path from current file for flexibility
PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"


def load_prompt(prompt_name: str) -> str:
    """Load prompt content from file."""
    # Direct search locations
    search_dirs = [
        PROMPTS_DIR,
        PROMPTS_DIR / "universal",
        PROMPTS_DIR / "agents",
        PROMPTS_DIR / "universal" / "ai_agent_prompts",
        PROMPTS_DIR / "universal" / "mpv_stages",
        PROMPTS_DIR / "packs",
    ]

    # Subdirectories to check
    subdirs = ["architect", "developer", "reviewer", "designer", "devops", "migration", "explorer"]

    # First try with exact name as provided
    for search_dir in search_dirs:
        prompt_file = search_dir / f"{prompt_name}.md"
        if prompt_file.exists():
            return prompt_file.read_text()

        # Check subdirectories
        for subdir in subdirs:
            prompt_file = search_dir / subdir / f"{prompt_name}.md"
            if prompt_file.exists():
                return prompt_file.read_text()

    # Try stripping "promt-" prefix if not found
    if prompt_name.startswith("promt-"):
        alt_name = prompt_name[6:]  # Remove "promt-" prefix
        for search_dir in search_dirs:
            prompt_file = search_dir / f"{alt_name}.md"
            if prompt_file.exists():
                return prompt_file.read_text()

            # Check subdirectories
            for subdir in subdirs:
                prompt_file = search_dir / subdir / f"{alt_name}.md"
                if prompt_file.exists():
                    return prompt_file.read_text()

            # Also check inside pack subdirectories (e.g. prompts/packs/pinescript-v6/)
            if search_dir.name == "packs":
                for subpack in search_dir.iterdir():
                    if subpack.is_dir():
                        prompt_file = subpack / f"{alt_name}.md"
                        if prompt_file.exists():
                            return prompt_file.read_text()
                        # Check deeper subdirectories within pack
                        for deeper in subpack.iterdir():
                            if deeper.is_dir():
                                prompt_file = deeper / f"{alt_name}.md"
                                if prompt_file.exists():
                                    return prompt_file.read_text()

    return ""


class WorkerStatus(Enum):
    """Worker lifecycle status."""
    PENDING = "pending"
    RUNNING = "running"
    WAITING = "waiting"  # Waiting for more input
    STOPPED = "stopped"
    ABORTED = "aborted"


@dataclass
class WorkerState:
    """State of a worker agent."""
    worker_id: str
    team_name: str
    agent_type: str
    directive: str
    status: WorkerStatus = WorkerStatus.PENDING
    session_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    messages: List[Dict[str, str]] = field(default_factory=list)  # inbox messages
    context: Dict[str, Any] = field(default_factory=dict)


class AgentOrchestrator:
    """
    Central router (Natural Language) for multi-agent system.

    Now delegates routing to AgentRouter and execution to PromptExecutor.
    """

    def __init__(self, use_checkpoint: bool = True):
        self.router = AgentRouter()
        self.executor = PromptExecutor()
        self.memory: Dict[str, Any] = {}
        self._checkpoint_executor: Optional[CheckpointExecutor] = None
        self._use_checkpoint = use_checkpoint
        # Worker state tracking for coordinator pattern
        self._workers: Dict[str, WorkerState] = {}

    def _detect_agents(self, request: str, intent_agent: Optional[str] = None) -> list[str]:
        """Detect which agents are needed based on request.

        Args:
            request: User request
            intent_agent: Optional agent from P9iRouter to avoid duplication
        """
        return self.router.detect_agents(request, intent_agent)

    def _select_prompt(self, agent_name: str, request: str) -> str:
        """Select appropriate prompt for agent based on request."""
        return self.router.select_prompt(agent_name, request)

    def get_agent_context(self, agent_name: str) -> Dict[str, Any]:
        """Get context from memory for agent."""
        agent = AGENTS.get(agent_name)
        if not agent:
            return {}
        return self.memory.get(agent.memory_key, {})

    def save_agent_context(self, agent_name: str, context: Dict[str, Any]):
        """Save context to memory for agent."""
        agent = AGENTS.get(agent_name)
        if not agent:
            return
        self.memory[agent.memory_key] = context

    async def execute_agent(
        self,
        agent_name: str,
        request: str,
        context: Optional[Dict[str, Any]] = None,
        use_checkpoint: bool = None,
        prompt_entry: Any = None  # PromptEntry passed through orchestration
    ):
        """Execute a single agent with optional PromptEntry metadata."""
        from dataclasses import dataclass

        @dataclass
        class AgentResult:
            agent: str
            status: str
            output: str = ""
            error: str = None
            metadata: dict = None

        # Use instance default if not specified
        if use_checkpoint is None:
            use_checkpoint = self._use_checkpoint

        agent = AGENTS.get(agent_name)
        if not agent:
            return AgentResult(
                agent=agent_name,
                status="error",
                error=f"Agent {agent_name} not found"
            )

        try:
            # Use provided PromptEntry or fetch it
            if prompt_entry is None:
                prompt_entry = self.router.select_prompt_entry(agent_name, request)

            # Select appropriate prompt name
            if prompt_entry:
                prompt_name = prompt_entry.name
            else:
                prompt_name = self._select_prompt(agent_name, request)

            # Load prompt content from file
            prompt_content = load_prompt(prompt_name)

            logger.info(f"Agent {agent_name} selected prompt: {prompt_name}, content length: {len(prompt_content)}")

            if not prompt_content:
                return AgentResult(
                    agent=agent_name,
                    status="error",
                    error=f"Prompt {prompt_name} not found"
                )

            # Build context with PromptEntry metadata
            exec_context = context or {}
            exec_context["agent"] = agent.name
            exec_context["task"] = request
            exec_context["memory"] = self.get_agent_context(agent_name)
            # Propagate PromptEntry metadata through orchestration
            if prompt_entry:
                exec_context["prompt_entry"] = {
                    "name": prompt_entry.name,
                    "category": str(prompt_entry.metadata.category) if prompt_entry.metadata else None,
                    "tags": list(prompt_entry.metadata.tags) if prompt_entry.metadata and prompt_entry.metadata.tags else [],
                }

            # Use checkpoint executor for write-heavy tasks
            agent = AGENTS.get(agent_name)
            if use_checkpoint and agent and agent.use_checkpoint:
                checkpoint_exec = get_checkpoint_executor()
                result = await checkpoint_exec.execute_with_checkpoint(
                    prompt=prompt_content,
                    request=request,
                    context=exec_context,
                    write_to_disk=True,
                )

                # Map checkpoint result to AgentResult
                exec_status = result.get("status", "error")
                exec_output = result.get("content", "")

                # Add file and bash info to metadata
                files_result = result.get("files", {})
                bash_results = result.get("bash_results", [])
                metadata = {
                    "prompt": prompt_name,
                    "prompt_entry": prompt_entry,
                    "agent_description": agent.description,
                    "execution_id": result.get("execution_id"),
                    "files_written": files_result.get("written", []),
                    "files_failed": files_result.get("failed", {}),
                    "bash_results": bash_results,
                }

                # Append bash results to output so user can see them
                if bash_results:
                    bash_output = "\n\n## Bash Results:\n"
                    for br in bash_results:
                        bash_output += f"```\n$ {br['command']}\nExit: {br['returncode']}\n"
                        if br.get("stdout"):
                            bash_output += f"stdout: {br['stdout'][:500]}"
                        if br.get("stderr"):
                            bash_output += f"stderr: {br['stderr'][:500]}"
                        bash_output += "```\n"
                    exec_output += bash_output

                if files_result.get("written"):
                    logger.info(f"Checkpoint executor wrote {len(files_result['written'])} files")
                if files_result.get("failed"):
                    logger.error(f"Checkpoint executor failed to write: {files_result['failed']}")
                if bash_results:
                    logger.info(f"Checkpoint executor ran {len(bash_results)} bash commands")

                # Save to memory
                self.save_agent_context(agent_name, {
                    "last_request": request,
                    "output": exec_output,
                    "prompt": prompt_name,
                    "execution_id": result.get("execution_id"),
                })

                return AgentResult(
                    agent=agent_name,
                    status=exec_status,
                    output=exec_output,
                    error=result.get("error"),
                    metadata=metadata,
                )

            # Original execution path
            result = await self.executor.execute(prompt_content, exec_context)

            logger.info(f"Agent {agent_name} executor result: status={result.get('status')}, content_len={len(result.get('content', ''))}, error={result.get('error')}")

            # Check if execution was successful
            exec_status = result.get("status", "success")
            exec_output = result.get("content", "")
            exec_error = result.get("error")

            # Save to memory
            self.save_agent_context(agent_name, {
                "last_request": request,
                "output": exec_output,
                "prompt": prompt_name
            })

            return AgentResult(
                agent=agent_name,
                status=exec_status,
                output=exec_output,
                error=exec_error,
                metadata={
                    "prompt": prompt_name,
                    "prompt_entry": prompt_entry,
                    "agent_description": agent.description
                }
            )

        except Exception as e:
            logger.error(f"Agent {agent_name} error: {e}")
            return AgentResult(
                agent=agent_name,
                status="error",
                error=str(e)
            )

    async def execute_parallel_agents(
        self,
        agent_requests: list[tuple[str, str]],  # [(agent_name, request), ...]
        context: Optional[Dict[str, Any]] = None,
    ) -> list[Dict[str, Any]]:
        """
        Execute multiple agents in parallel.

        Claude Code pattern: spawn multiple workers simultaneously,
        collect results, then synthesize.

        Args:
            agent_requests: List of (agent_name, request) tuples
            context: Optional shared context

        Returns:
            List of result dicts (one per agent)
        """
        import asyncio

        async def execute_one(agent_name: str, request: str) -> Dict[str, Any]:
            result = await self.execute_agent(agent_name, request, context=context)
            return {
                "agent": result.agent,
                "status": result.status,
                "output": result.output,
                "error": result.error,
                "metadata": result.metadata
            }

        # Execute all agents in parallel
        tasks = [execute_one(agent, request) for agent, request in agent_requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                agent_name = agent_requests[i][0]
                processed_results.append({
                    "agent": agent_name,
                    "status": "error",
                    "output": "",
                    "error": str(result),
                    "metadata": None
                })
            else:
                processed_results.append(result)

        return processed_results

    # ==========================================
    # COORDINATOR PATTERN: Worker Lifecycle
    # ==========================================

    async def spawn_worker(
        self,
        team_name: str,
        directive: str,
        agent_type: str = "worker",
    ) -> Dict[str, Any]:
        """
        Spawn a persistent worker agent with directive.

        Claude Code pattern: creates a worker that can be continued
        with additional messages, simulating sub-agent behavior.

        Args:
            team_name: Name of the team (for grouping workers)
            directive: Task description for the worker
            agent_type: Type of agent to spawn (default: "worker")

        Returns:
            Dict with worker_id, team_name, status
        """
        import uuid
        from datetime import datetime

        worker_id = str(uuid.uuid4())[:8]

        # Create worker state
        worker = WorkerState(
            worker_id=worker_id,
            team_name=team_name,
            agent_type=agent_type,
            directive=directive,
            status=WorkerStatus.RUNNING,
            session_id=str(uuid.uuid4()),
            created_at=datetime.now(),
            last_active=datetime.now(),
        )

        self._workers[worker_id] = worker

        # Execute the worker with its directive
        try:
            result = await self.execute_agent(
                agent_name=agent_type if agent_type != "worker" else "developer",
                request=directive,
            )

            # Update worker state
            worker.last_active = datetime.now()
            worker.status = WorkerStatus.WAITING

            return {
                "worker_id": worker_id,
                "team_name": team_name,
                "status": "spawned",
                "agent": result.agent if hasattr(result, 'agent') else agent_type,
                "output": result.output if hasattr(result, 'output') else str(result),
            }
        except Exception as e:
            worker.status = WorkerStatus.STOPPED
            logger.error(f"Worker {worker_id} spawn failed: {e}")
            return {
                "worker_id": worker_id,
                "team_name": team_name,
                "status": "error",
                "error": str(e),
            }

    async def continue_worker(
        self,
        worker_id: str,
        message: str,
    ) -> Dict[str, Any]:
        """
        Send message to worker and get response.

        Workers maintain context between calls, enabling
        multi-turn conversations with persistent state.

        Args:
            worker_id: ID of worker to continue
            message: Message to send to worker

        Returns:
            Dict with worker_id, response, status
        """
        from datetime import datetime

        worker = self._workers.get(worker_id)
        if not worker:
            return {"error": f"Worker {worker_id} not found", "worker_id": worker_id}

        # Append message to inbox
        worker.messages.append({"role": "user", "content": message})
        worker.status = WorkerStatus.RUNNING
        worker.last_active = datetime.now()

        try:
            # Continue execution - build context from previous messages
            context = worker.context.copy() if worker.context else {}
            context["worker_messages"] = worker.messages[:-1]  # Exclude current message

            result = await self.execute_agent(
                agent_name=worker.agent_type,
                request=message,
                context=context,
            )

            # Store response in inbox
            worker.messages.append({"role": "assistant", "content": result.output if hasattr(result, 'output') else str(result)})
            worker.last_active = datetime.now()
            worker.status = WorkerStatus.WAITING

            return {
                "worker_id": worker_id,
                "response": result.output if hasattr(result, 'output') else str(result),
                "status": "success",
            }
        except Exception as e:
            worker.status = WorkerStatus.STOPPED
            logger.error(f"Worker {worker_id} continue failed: {e}")
            return {
                "worker_id": worker_id,
                "status": "error",
                "error": str(e),
            }

    async def abort_worker(self, worker_id: str) -> Dict[str, Any]:
        """
        Gracefully terminate a worker.

        Args:
            worker_id: ID of worker to abort

        Returns:
            Dict with success status
        """
        worker = self._workers.get(worker_id)
        if not worker:
            return {"error": f"Worker {worker_id} not found", "worker_id": worker_id}

        worker.status = WorkerStatus.ABORTED
        del self._workers[worker_id]

        logger.info(f"Worker {worker_id} aborted")
        return {
            "worker_id": worker_id,
            "status": "aborted",
            "success": True,
        }

    async def create_team(self, team_name: str, description: str = None) -> Dict[str, Any]:
        """
        Create a team for coordinator pattern.

        Teams group related workers together.

        Args:
            team_name: Name of the team
            description: Optional team description

        Returns:
            Dict with team_name, worker_ids
        """
        team_workers = [
            w.worker_id for w in self._workers.values()
            if w.team_name == team_name
        ]
        return {
            "team_name": team_name,
            "description": description,
            "worker_ids": team_workers,
            "status": "created",
        }

    async def delete_team(self, team_name: str) -> Dict[str, Any]:
        """
        Clean up team and all its workers.

        Args:
            team_name: Name of team to delete

        Returns:
            Dict with cleanup status
        """
        workers_to_delete = [
            w.worker_id for w in self._workers.values()
            if w.team_name == team_name
        ]

        for worker_id in workers_to_delete:
            del self._workers[worker_id]

        logger.info(f"Team {team_name} deleted, {len(workers_to_delete)} workers cleaned up")
        return {
            "team_name": team_name,
            "workers_deleted": len(workers_to_delete),
            "status": "deleted",
        }

    def list_workers(self, team_name: str = None) -> List[Dict[str, Any]]:
        """
        List workers, optionally filtered by team.

        Args:
            team_name: Optional team name to filter by

        Returns:
            List of worker info dicts
        """
        workers = self._workers.values()
        if team_name:
            workers = [w for w in workers if w.team_name == team_name]

        return [
            {
                "worker_id": w.worker_id,
                "team_name": w.team_name,
                "agent_type": w.agent_type,
                "status": w.status.value,
                "created_at": w.created_at.isoformat(),
                "last_active": w.last_active.isoformat(),
            }
            for w in workers
        ]

    async def route(self, request: str) -> Dict[str, Any]:
        """
        Main routing method - Natural Language interface.

        Detects needed agents and orchestrates their execution.
        """
        # Detect which agents are needed
        needed_agents = self._detect_agents(request)

        logger.info(f"Routing request to agents: {needed_agents}")

        results = []

        # Execute agents - parallel if multiple, sequential if single
        if len(needed_agents) > 1:
            # Parallel execution for multiple independent agents (Claude Code pattern)
            agent_requests = [(agent, request) for agent in needed_agents]
            results = await self.execute_parallel_agents(agent_requests)
            for r in results:
                logger.info(f"Agent {r['agent']} result: status={r['status']}, output_len={len(r['output']) if r['output'] else 0}")
        else:
            # Single agent - direct sequential execution
            for agent_name in needed_agents:
                result = await self.execute_agent(agent_name, request)
                logger.info(f"Agent {agent_name} result: status={result.status}, output_len={len(result.output) if result.output else 0}")
                results.append({
                    "agent": result.agent,
                    "status": result.status,
                    "output": result.output,
                    "error": result.error,
                    "metadata": result.metadata
                })

                # If agent failed, stop the chain
                if result.status == "error":
                    break

        # Compile final response
        all_outputs = [r["output"] for r in results if r["output"]]
        errors = [r["error"] for r in results if r["error"]]

        logger.info(f"Orchestrator results: outputs_count={len(all_outputs)}, errors_count={len(errors)}")

        return {
            "status": "success" if not errors else "partial" if all_outputs else "error",
            "request": request,
            "agents_used": needed_agents,
            "results": results,
            "output": "\n\n---\n\n".join(all_outputs) if all_outputs else "",
            "errors": errors
        }

    async def route_with_entry(
        self,
        request: str,
        prompt_entry: Any = None,
        intent_agent: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        use_checkpoint: bool = None
    ) -> Dict[str, Any]:
        """
        Route request with PromptEntry propagation.

        This method ensures PromptEntry metadata flows through the orchestration chain,
        enabling better context for downstream agents.

        Args:
            request: User request
            prompt_entry: Optional initial PromptEntry to propagate
            intent_agent: Optional agent from P9iRouter to skip detection
            use_checkpoint: Optional checkpoint flag for file writing

        Returns:
            Dict with status, agents_used, results, output, errors
        """
        # Detect which agents are needed
        needed_agents = self._detect_agents(request, intent_agent)

        logger.info(f"Routing request to agents (with entry): {needed_agents}")

        results = []
        current_entry = prompt_entry

        # Execute each agent sequentially, propagating PromptEntry
        for agent_name in needed_agents:
            result = await self.execute_agent(
                agent_name,
                request,
                context=context,
                use_checkpoint=use_checkpoint,
                prompt_entry=current_entry
            )
            logger.info(f"Agent {agent_name} result: status={result.status}, output_len={len(result.output) if result.output else 0}")

            results.append({
                "agent": result.agent,
                "status": result.status,
                "output": result.output,
                "error": result.error,
                "metadata": result.metadata
            })

            # Chain: next agent gets PromptEntry from previous result
            if result.metadata and result.metadata.get("prompt_entry"):
                current_entry = result.metadata.get("prompt_entry")

            # If agent failed, stop the chain
            if result.status == "error":
                break

        # Compile final response
        all_outputs = [r["output"] for r in results if r["output"]]
        errors = [r["error"] for r in results if r["error"]]

        logger.info(f"Orchestrator (with entry) results: outputs_count={len(all_outputs)}, errors_count={len(errors)}")

        return {
            "status": "success" if not errors else "partial" if all_outputs else "error",
            "request": request,
            "agents_used": needed_agents,
            "results": results,
            "output": "\n\n---\n\n".join(all_outputs) if all_outputs else "",
            "errors": errors,
            "prompt_entry": prompt_entry
        }

    def list_agents(self) -> list[Dict[str, Any]]:
        """List all available agents."""
        return self.router.list_agents()


# Global orchestrator instance
_orchestrator_instance: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create global orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = AgentOrchestrator()
    return _orchestrator_instance
