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

# Optional asyncio import for lock
try:
    import asyncio
    HAS_ASYNCIO = True
except ImportError:
    HAS_ASYNCIO = False

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


class PhaseStatus(Enum):
    """Workflow phase status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TaskPhase:
    """Single phase in the 4-phase workflow."""
    name: str  # research, synthesis, implementation, verification
    status: PhaseStatus = PhaseStatus.PENDING
    agent_type: str = ""  # explorer, architect, developer, reviewer
    directive: str = ""
    output: str = ""
    error: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowTask:
    """Represents a 4-phase workflow task (Claude Code pattern)."""
    task_id: str
    name: str
    target: str  # Target module/file
    project_path: str
    status: str = "pending"  # pending, in_progress, completed, failed
    current_phase: int = 0  # 0=Research, 1=Synthesis, 2=Implementation, 3=Verification
    phases: List[TaskPhase] = field(default_factory=list)
    team_name: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    result: Dict[str, Any] = field(default_factory=dict)
    error: str = ""


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
        # Workflow task tracking for 4-phase coordinator pattern
        self._workflows: Dict[str, WorkflowTask] = {}
        # Thread-safety lock for shared state
        self._lock = asyncio.Lock() if HAS_ASYNCIO else None

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

        except ValueError as e:
            # Validation errors - should not retry
            logger.warning(f"Agent {agent_name} validation error: {e}")
            return AgentResult(
                agent=agent_name,
                status="validation_error",
                error=str(e)
            )
        except TimeoutError as e:
            # Timeout errors - could retry
            logger.error(f"Agent {agent_name} timeout after {self.executor.timeout}s: {e}")
            return AgentResult(
                agent=agent_name,
                status="timeout",
                error=f"Timeout after {self.executor.timeout}s: {str(e)}"
            )
        except Exception as e:
            # Unexpected errors - log with full traceback
            logger.exception(f"Agent {agent_name} unexpected error: {e}")
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

    async def execute_parallel_research(
        self,
        target: str,
        project_path: str = ".",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute 3-phase parallel research: Tech Stack + Code Patterns + Best Practices.

        ADR-019 Pattern:
        ┌─────────────────────────────────────────────────────────────┐
        │              PARALLEL RESEARCH PHASE                        │
        │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
        │  │  Explorer 1     │  │  Explorer 2     │  │ Explorer 3  │  │
        │  │  Tech Stack     │  │  Code Patterns  │  │ Best        │  │
        │  │  Analysis       │  │  & Structure    │  │ Practices   │  │
        │  └────────┬────────┘  └────────┬────────┘  └──────┬──────┘  │
        │           └────────────────────┼───────────────────┘         │
        │                                ▼                              │
        │                    ┌───────────────────┐                      │
        │                    │  SYNTHESIS PHASE │                      │
        │                    └─────────┬─────────┘                      │
        └──────────────────────────────┼───────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────┐
                        │   Architecture      │
                        │   Recommendation    │
                        └─────────────────────┘

        Args:
            target: Target module/path to analyze (e.g., "src/services")
            project_path: Path to the project
            context: Optional shared context

        Returns:
            Dict with research results and synthesis
        """
        import asyncio

        # Phase 1: Parallel Research (3 explorers simultaneously)
        logger.info(f"Starting parallel research for target: {target}")

        # Define the 3 research streams
        research_tasks = [
            ("explorer", f"Analyze tech stack for {target}. Use explorer-1-tech-stack.md pattern."),
            ("explorer", f"Analyze code patterns and structure in {target}. Use explorer-2-code-patterns.md pattern."),
            ("explorer", f"Assess best practices and quality for {target}. Use explorer-3-best-practices.md pattern."),
        ]

        # Execute all 3 explorers in parallel
        async def execute_explorer(task_desc: str, idx: int) -> Dict[str, Any]:
            """Execute single explorer with context."""
            exec_context = context.copy() if context else {}
            exec_context["target"] = target
            exec_context["project_path"] = project_path
            exec_context["research_stream"] = idx  # 0=Tech, 1=Patterns, 2=Quality

            result = await self.execute_agent(
                agent_name="explorer",
                request=task_desc,
                context=exec_context,
                use_checkpoint=False,
            )
            return {
                "stream": idx,
                "agent": result.agent,
                "status": result.status,
                "output": result.output,
                "error": result.error,
                "metadata": result.metadata
            }

        # Launch all 3 explorers in parallel
        explorer_tasks = [
            execute_explorer(desc, idx)
            for idx, (_, desc) in enumerate(research_tasks)
        ]

        logger.info("Executing 3 explorer agents in parallel...")
        explorer_results = await asyncio.gather(*explorer_tasks, return_exceptions=True)

        # Process results
        processed_results = []
        for i, result in enumerate(explorer_results):
            if isinstance(result, Exception):
                processed_results.append({
                    "stream": i,
                    "agent": "explorer",
                    "status": "error",
                    "output": "",
                    "error": str(result),
                    "metadata": None
                })
            else:
                processed_results.append(result)

        # Sort by stream order
        processed_results.sort(key=lambda x: x.get("stream", 0))

        # Extract outputs for synthesis
        tech_stack_output = processed_results[0].get("output", "") if len(processed_results) > 0 else ""
        code_patterns_output = processed_results[1].get("output", "") if len(processed_results) > 1 else ""
        best_practices_output = processed_results[2].get("output", "") if len(processed_results) > 2 else ""

        # Phase 2: Synthesis (combine all findings)
        synthesis_context = context.copy() if context else {}
        synthesis_context["target"] = target
        synthesis_context["project_path"] = project_path
        synthesis_context["tech_stack_output"] = tech_stack_output
        synthesis_context["code_patterns_output"] = code_patterns_output
        synthesis_context["best_practices_output"] = best_practices_output

        # Execute architect agent for synthesis
        synthesis_request = f"""Synthesize findings for {target}:

## Tech Stack Findings:
{tech_stack_output[:5000] if tech_stack_output else 'No data'}

## Code Patterns Findings:
{code_patterns_output[:5000] if code_patterns_output else 'No data'}

## Best Practices Findings:
{best_practices_output[:5000] if best_practices_output else 'No data'}

Produce a unified research report with:
1. Tech Stack Summary
2. Code Patterns Found
3. Quality Assessment
4. Risks & Recommendations (3-5 actionable items)
5. Next Steps
"""
        synthesis_result = await self.execute_agent(
            agent_name="architect",
            request=synthesis_request,
            context=synthesis_context,
            use_checkpoint=True,
        )

        # Phase 3: Output is embedded in synthesis_result
        # CheckpointExecutor handles file creation if needed

        return {
            "status": "success",
            "target": target,
            "research_results": processed_results,
            "synthesis": {
                "agent": synthesis_result.agent,
                "status": synthesis_result.status,
                "output": synthesis_result.output,
                "error": synthesis_result.error,
                "metadata": synthesis_result.metadata,
            },
            "phase": "completed",
            "research_time": "parallel (3 streams)",
        }

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

    # ==========================================
    # COORDINATOR PATTERN: 4-Phase Workflow
    # ==========================================

    def create_workflow(
        self,
        name: str,
        target: str,
        project_path: str = ".",
        team_name: str = None,
    ) -> Dict[str, Any]:
        """
        Create a new 4-phase workflow task.

        Graph TD pattern:
            A[Фаза 1: Исследование] -->|Отчёты| B[Фаза 2: Синтез]
            B -->|Спецификация| C[Фаза 3: Реализация]
            C -->|Изменения + Коммиты| D[Фаза 4: Верификация]
            D -- Успех --> E[Задача завершена]
            D -- Ошибки --> C

        Args:
            name: Workflow task name
            target: Target module/file to work on
            project_path: Path to project
            team_name: Optional team name for worker grouping

        Returns:
            Dict with workflow_id and initial state
        """
        import uuid
        from datetime import datetime

        workflow_id = str(uuid.uuid4())[:8]
        team = team_name or f"team-{workflow_id}"

        # Create 4 phases
        phases = [
            TaskPhase(name="research", agent_type="explorer", directive=f"Analyze {target}"),
            TaskPhase(name="synthesis", agent_type="architect", directive=f"Synthesize findings for {target}"),
            TaskPhase(name="implementation", agent_type="developer", directive=f"Implement changes for {target}"),
            TaskPhase(name="verification", agent_type="reviewer", directive=f"Verify implementation for {target}"),
        ]

        workflow = WorkflowTask(
            task_id=workflow_id,
            name=name,
            target=target,
            project_path=project_path,
            team_name=team,
            phases=phases,
        )

        self._workflows[workflow_id] = workflow

        return {
            "workflow_id": workflow_id,
            "name": name,
            "target": target,
            "team_name": team,
            "phases": [p.name for p in phases],
            "status": "created",
        }

    async def execute_workflow(
        self,
        workflow_id: str,
        directive: str = None,
        auto_continue: bool = True,
        max_iterations: int = 3,
    ) -> Dict[str, Any]:
        """
        Execute a 4-phase workflow with feedback loop.

        Phase transitions:
            Research → Synthesis → Implementation → Verification → Complete
              ↑___________|___________|____________|                    |
              (on error, retry Implementation)  ←________________________|

        Feedback Loop (when verification fails and auto_continue=True):
            Verification → Research → Synthesis → Implementation → Verification
              ↑                                                    |
              └──────────────── New Iteration ─────────────────────┘

        Args:
            workflow_id: ID of workflow to execute
            directive: Optional override for the main directive
            auto_continue: If True, automatically retry on failure and follow feedback loop
            max_iterations: Maximum number of iterations (default 3)

        Returns:
            Dict with workflow execution results
        """
        import uuid
        from datetime import datetime

        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return {"error": f"Workflow {workflow_id} not found", "status": "not_found"}

        workflow.status = "in_progress"
        workflow.updated_at = datetime.now()

        # Execute each phase sequentially
        for phase_idx, phase in enumerate(workflow.phases):
            workflow.current_phase = phase_idx
            phase.status = PhaseStatus.IN_PROGRESS
            phase.started_at = datetime.now()

            logger.info(f"Workflow {workflow_id}: Starting phase {phase_idx} ({phase.name})")

            # Build context from previous phases
            context = {
                "task_id": workflow.task_id,
                "workflow_name": workflow.name,
                "target": workflow.target,
                "project_path": workflow.project_path,
                "team_name": workflow.team_name,
                "phase_index": phase_idx,
                "phase_name": phase.name,
            }

            # Add previous phase outputs to context
            if phase_idx > 0:
                prev_phase = workflow.phases[phase_idx - 1]
                context["previous_phase_output"] = prev_phase.output
                context["previous_phase_errors"] = prev_phase.error

            # Build directive
            task_directive = directive or phase.directive

            # Execute the appropriate agent
            try:
                if phase.name == "research":
                    # Phase 1: Parallel research (3 explorers)
                    result = await self.execute_parallel_research(
                        target=workflow.target,
                        project_path=workflow.project_path,
                        context=context,
                    )
                    phase.output = result.get("synthesis", {}).get("output", "")
                    if result.get("status") == "success":
                        phase.status = PhaseStatus.COMPLETED
                    else:
                        phase.status = PhaseStatus.FAILED
                        phase.error = result.get("error", "Unknown error")

                elif phase.name == "synthesis":
                    # Phase 2: Architecture synthesis
                    synthesis_directive = f"""Based on research findings for {workflow.target}:

{directive or 'Create a detailed architectural specification with:'}
1. Component breakdown
2. Data flow
3. API contracts
4. Implementation roadmap

Focus on actionable, concrete specifications.
"""
                    result = await self.execute_agent(
                        agent_name="architect",
                        request=synthesis_directive,
                        context=context,
                        use_checkpoint=True,
                    )
                    phase.output = result.output if hasattr(result, 'output') else str(result)
                    phase.status = PhaseStatus.COMPLETED if result.status == "success" else PhaseStatus.FAILED
                    phase.error = result.error if hasattr(result, 'error') and result.error else ""

                elif phase.name == "implementation":
                    # Phase 3: Code implementation
                    impl_directive = f"""Implement the following specification for {workflow.target}:

{directive or 'Write production-ready code based on the architectural specification.'}

Requirements:
- Follow existing code patterns
- Include tests
- Update documentation if needed
"""
                    result = await self.execute_agent(
                        agent_name="developer",
                        request=impl_directive,
                        context=context,
                        use_checkpoint=True,
                    )
                    phase.output = result.output if hasattr(result, 'output') else str(result)
                    phase.status = PhaseStatus.COMPLETED if result.status == "success" else PhaseStatus.FAILED
                    phase.error = result.error if hasattr(result, 'error') and result.error else ""

                elif phase.name == "verification":
                    # Phase 4: Verification
                    verify_directive = f"""Verify the implementation for {workflow.target}:

{directive or 'Run verification checks including:'}
1. Code quality
2. Test coverage
3. Security audit
4. Integration testing

Provide a detailed verification report.
"""
                    result = await self.execute_agent(
                        agent_name="reviewer",
                        request=verify_directive,
                        context=context,
                        use_checkpoint=False,
                    )
                    phase.output = result.output if hasattr(result, 'output') else str(result)
                    phase.status = PhaseStatus.COMPLETED if result.status == "success" else PhaseStatus.FAILED
                    phase.error = result.error if hasattr(result, 'error') and result.error else ""

            except Exception as e:
                logger.exception(f"Workflow {workflow_id} phase {phase.name} error: {e}")
                phase.status = PhaseStatus.FAILED
                phase.error = str(e)

            phase.completed_at = datetime.now()
            workflow.updated_at = datetime.now()

            # Check if we should stop on failure
            if phase.status == PhaseStatus.FAILED:
                if phase.name == "implementation" and auto_continue:
                    # Retry implementation once
                    logger.warning(f"Workflow {workflow_id}: Implementation failed, retrying...")
                    phase.status = PhaseStatus.IN_PROGRESS
                    continue
                elif phase.name == "verification" and auto_continue:
                    # FEEDBACK LOOP: Verification failed → New iteration starting from Research
                    current_iteration = getattr(workflow, 'phase_iteration', 1)
                    if current_iteration >= max_iterations:
                        logger.warning(f"Workflow {workflow_id}: Max iterations ({max_iterations}) reached, stopping...")
                        workflow.status = "failed"
                        workflow.error = f"Max iterations ({max_iterations}) reached. Last error: {phase.error}"
                        break
                    logger.warning(f"Workflow {workflow_id}: Verification failed, starting new iteration from Research...")
                    # Reset phases for new iteration
                    for p in workflow.phases:
                        p.status = PhaseStatus.PENDING
                        p.output = ""
                        p.error = ""
                    workflow.current_phase = 0  # Back to Research
                    workflow.phase_iteration = current_iteration + 1
                    logger.info(f"Workflow {workflow_id}: Starting iteration {workflow.phase_iteration}/{max_iterations}")
                    continue
                else:
                    workflow.status = "failed"
                    workflow.error = phase.error
                    break

        # Finalize workflow
        if workflow.status == "in_progress":
            failed_count = sum(1 for p in workflow.phases if p.status == PhaseStatus.FAILED)
            if failed_count > 0:
                workflow.status = "failed"
            else:
                workflow.status = "completed"

        # Build result
        workflow.result = {
            "workflow_id": workflow.task_id,
            "name": workflow.name,
            "target": workflow.target,
            "status": workflow.status,
            "phases": [
                {
                    "name": p.name,
                    "status": p.status.value,
                    "output": p.output[:1000] if p.output else "",
                    "error": p.error,
                    "started_at": p.started_at.isoformat() if p.started_at else None,
                    "completed_at": p.completed_at.isoformat() if p.completed_at else None,
                }
                for p in workflow.phases
            ],
        }

        return workflow.result

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return {"error": f"Workflow {workflow_id} not found"}

        return {
            "workflow_id": workflow.task_id,
            "name": workflow.name,
            "target": workflow.target,
            "status": workflow.status,
            "current_phase": workflow.current_phase,
            "phase_names": [p.name for p in workflow.phases],
            "phases": [
                {
                    "name": p.name,
                    "status": p.status.value,
                    "output_preview": p.output[:200] if p.output else "",
                }
                for p in workflow.phases
            ],
        }

    def list_workflows(self, status: str = None) -> List[Dict[str, Any]]:
        """List all workflows, optionally filtered by status."""
        workflows = self._workflows.values()
        if status:
            workflows = [w for w in workflows if w.status == status]

        return [
            {
                "workflow_id": w.task_id,
                "name": w.name,
                "target": w.target,
                "status": w.status,
                "current_phase": w.current_phase,
                "phase_names": [p.name for p in w.phases],
            }
            for w in workflows
        ]

    def delete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Delete a workflow."""
        if workflow_id not in self._workflows:
            return {"error": f"Workflow {workflow_id} not found", "status": "not_found"}

        del self._workflows[workflow_id]
        return {"workflow_id": workflow_id, "status": "deleted"}

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
