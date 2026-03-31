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
from typing import Dict, Any, Optional

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
    subdirs = ["architect", "developer", "reviewer", "designer", "devops", "migration"]

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

    def _detect_agents(self, request: str) -> list[str]:
        """Detect which agents are needed based on request."""
        return self.router.detect_agents(request)

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
        use_checkpoint: bool = None
    ):
        """Execute a single agent."""
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
            # Select appropriate prompt name
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

            # Build context
            exec_context = context or {}
            exec_context["agent"] = agent.name
            exec_context["task"] = request
            exec_context["memory"] = self.get_agent_context(agent_name)

            # Use checkpoint executor for write-heavy tasks
            if use_checkpoint and agent_name in ("developer", "full_cycle"):
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

                # Add file info to metadata
                files_result = result.get("files", {})
                metadata = {
                    "prompt": prompt_name,
                    "agent_description": agent.description,
                    "execution_id": result.get("execution_id"),
                    "files_written": files_result.get("written", []),
                    "files_failed": files_result.get("failed", {}),
                }

                if files_result.get("written"):
                    logger.info(f"Checkpoint executor wrote {len(files_result['written'])} files")
                if files_result.get("failed"):
                    logger.error(f"Checkpoint executor failed to write: {files_result['failed']}")

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

    async def route(self, request: str) -> Dict[str, Any]:
        """
        Main routing method - Natural Language interface.

        Detects needed agents and orchestrates their execution.
        """
        # Detect which agents are needed
        needed_agents = self._detect_agents(request)

        logger.info(f"Routing request to agents: {needed_agents}")

        results = []

        # Execute each agent sequentially
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
