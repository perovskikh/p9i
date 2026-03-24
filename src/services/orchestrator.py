# src/services/orchestrator.py
"""
Agent Orchestrator - Central Router for Multi-Agent System

Manages interactions between specialized AI agents through shared memory.
Siri-like interface for p9i.

Now uses Clean Architecture:
- AgentRouter (application layer): Agent detection and prompt selection
- AgentExecutor (services layer): Prompt execution
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from src.services.executor import PromptExecutor
from src.application.agent_router import AgentRouter, AGENTS

logger = logging.getLogger(__name__)

# Prompts directory
PROMPTS_DIR = Path("/app/prompts")


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
    subdirs = ["architect", "developer", "reviewer", "designer", "devops"]

    for search_dir in search_dirs:
        # Direct file check
        prompt_file = search_dir / f"{prompt_name}.md"
        if prompt_file.exists():
            return prompt_file.read_text()

        # Check subdirectories
        for subdir in subdirs:
            prompt_file = search_dir / subdir / f"{prompt_name}.md"
            if prompt_file.exists():
                return prompt_file.read_text()

    return ""


class AgentOrchestrator:
    """
    Central router (Siri-like) for multi-agent system.

    Now delegates routing to AgentRouter and execution to PromptExecutor.
    """

    def __init__(self):
        self.router = AgentRouter()
        self.executor = PromptExecutor()
        self.memory: Dict[str, Any] = {}

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
        context: Optional[Dict[str, Any]] = None
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

            # Execute prompt with content
            result = await self.executor.execute(prompt_content, exec_context)

            # Save to memory
            self.save_agent_context(agent_name, {
                "last_request": request,
                "output": result.get("content", ""),
                "prompt": prompt_name
            })

            return AgentResult(
                agent=agent_name,
                status="success",
                output=result.get("content", ""),
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
        Main routing method - Siri-like interface.

        Detects needed agents and orchestrates their execution.
        """
        # Detect which agents are needed
        needed_agents = self._detect_agents(request)

        logger.info(f"Routing request to agents: {needed_agents}")

        results = []

        # Execute each agent sequentially
        for agent_name in needed_agents:
            result = await self.execute_agent(agent_name, request)
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
