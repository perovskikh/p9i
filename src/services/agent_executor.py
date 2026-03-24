# src/services/agent_executor.py
"""
Agent Executor - Handles prompt execution for agents.

Part of Clean Architecture - Infrastructure layer.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from src.services.executor import PromptExecutor

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Result of agent execution."""
    agent: str
    status: str
    output: str = ""
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentExecutor:
    """Handles execution of agent prompts."""

    def __init__(self):
        self.executor = PromptExecutor()

    async def execute(
        self,
        agent_name: str,
        prompt_name: str,
        prompt_content: str,
        request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """
        Execute an agent with given prompt.

        Args:
            agent_name: Agent name
            prompt_name: Prompt to use
            prompt_content: Prompt content
            request: User request
            context: Additional context

        Returns:
            AgentResult with execution output
        """
        try:
            # Build execution context
            exec_context = context or {}
            exec_context["agent"] = agent_name
            exec_context["task"] = request

            # Execute prompt
            result = await self.executor.execute(prompt_content, exec_context)

            return AgentResult(
                agent=agent_name,
                status="success",
                output=result.get("content", ""),
                metadata={
                    "prompt": prompt_name,
                }
            )

        except Exception as e:
            logger.error(f"Agent {agent_name} error: {e}")
            return AgentResult(
                agent=agent_name,
                status="error",
                error=str(e)
            )
