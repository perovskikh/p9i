# src/services/orchestrator.py
"""
Agent Orchestrator - Central Router for Multi-Agent System

Manages interactions between specialized AI agents through shared memory.
Siri-like interface for p9i.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from src.services.executor import PromptExecutor

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


@dataclass
class Agent:
    """Represents an AI agent with its own prompts"""
    name: str
    prompts: List[str]
    memory_key: str
    description: str = ""


@dataclass
class AgentResult:
    """Result from agent execution"""
    agent: str
    status: str
    output: str = ""
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentOrchestrator:
    """
    Central router (Siri-like) for multi-agent system.

    Manages agent interactions through shared memory.
    """

    # Define available agents - uses prompts from universal/ai_agent_prompts/
    AGENTS = {
        "architect": Agent(
            name="Architect",
            prompts=[
                "promt-project-adaptation",  # Adapts to project stack
                "promt-adr-implementation-planner",  # ADR planning
                "create_adr"
            ],
            memory_key="architecture",
            description="System design, ADRs, architecture decisions"
        ),
        "developer": Agent(
            name="Developer",
            prompts=[
                "promt-feature-add",  # Add new features
                "promt-bug-fix",     # Fix bugs
                "promt-refactoring",  # Refactor code
                "promt-implementation"  # General implementation
            ],
            memory_key="code",
            description="Code generation, features, bug fixes"
        ),
        "reviewer": Agent(
            name="Reviewer",
            prompts=[
                "promt-llm-review",     # Code review
                "promt-security-audit",  # Security check
                "promt-quality-test"    # Quality testing
            ],
            memory_key="reviews",
            description="Code review, security, quality checks"
        ),
        "designer": Agent(
            name="Designer",
            prompts=[
                "promt-ui-generator",  # UI generation (covers Tailwind + shadcn)
            ],
            memory_key="design",
            description="UI/UX design and generation"
        ),
        "devops": Agent(
            name="DevOps",
            prompts=[
                "promt-ci-cd-pipeline",
                "promt-onboarding"
            ],
            memory_key="devops",
            description="CI/CD, deployment, infrastructure"
        )
    }

    # Keywords for agent detection
    AGENT_KEYWORDS = {
        "architect": ["спроектируй", "архитектура", "adr", "design", "architect", "проектирование"],
        "developer": ["создай", "добавь", "напиши", "код", "feature", "create", "add", "code"],
        "reviewer": ["ревью", "проверь", "аудит", "тест", "review", "check", "audit", "test"],
        "designer": ["дизайн", "ui", "ux", "интерфейс", "button", "card", "design", "interface"],
        "devops": ["ci", "cd", "deploy", "docker", "kubernetes", "pipeline", "деплой"]
    }

    def __init__(self):
        self.executor = PromptExecutor()
        self.memory: Dict[str, Any] = {}

    def _detect_agents(self, request: str) -> List[str]:
        """Detect which agents are needed based on request"""
        request_lower = request.lower()
        needed = []

        for agent_name, keywords in self.AGENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in request_lower:
                    if agent_name not in needed:
                        needed.append(agent_name)
                    break

        # Default to developer if no specific agent detected
        if not needed:
            needed = ["developer"]

        return needed

    def _select_prompt(self, agent_name: str, request: str) -> str:
        """Select appropriate prompt for agent based on request"""
        agent = self.AGENTS.get(agent_name)
        if not agent:
            return agent.prompts[0]

        request_lower = request.lower()

        # Try to match prompt based on keywords
        prompt_keywords = {
            "promt-architect-design": ["спроектируй", "проектирование", "design"],
            "promt-architect-review": ["ревью", "review", "анализ"],
            "create_adr": ["adr", "документация"],
            "promt-feature-add": ["добавь", "новая", "feature", "new"],
            "promt-bug-fix": ["баг", "исправь", "bug", "fix"],
            "promt-refactoring": ["рефакторинг", "refactor"],
            "promt-llm-review": ["ревью", "review"],
            "promt-security-audit": ["безопасность", "security"],
            "promt-quality-test": ["тест", "test", "quality"],
            "promt-ui-generator": ["дизайн", "ui", "design"],
            "generate_tailwind": ["tailwind", "css"],
            "generate_shadcn": ["shadcn", "react", "component"],
            "promt-ci-cd-pipeline": ["ci", "cd", "pipeline", "деплой"],
            "promt-onboarding": ["онбординг", "onboard", "адаптация"]
        }

        for prompt in agent.prompts:
            keywords = prompt_keywords.get(prompt, [])
            for keyword in keywords:
                if keyword in request_lower:
                    return prompt

        # Default to first prompt
        return agent.prompts[0]

    def get_agent_context(self, agent_name: str) -> Dict[str, Any]:
        """Get context from memory for agent"""
        agent = self.AGENTS.get(agent_name)
        if not agent:
            return {}

        return self.memory.get(agent.memory_key, {})

    def save_agent_context(self, agent_name: str, context: Dict[str, Any]):
        """Save context to memory for agent"""
        agent = self.AGENTS.get(agent_name)
        if not agent:
            return

        self.memory[agent.memory_key] = context

    async def execute_agent(
        self,
        agent_name: str,
        request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """Execute a single agent"""
        agent = self.AGENTS.get(agent_name)
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

    async def execute_single_agent(
        self,
        agent_name: str,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """Execute a specific agent directly"""
        return await self.execute_agent(agent_name, task, context)

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents"""
        return [
            {
                "name": agent.name,
                "key": key,
                "prompts": agent.prompts,
                "description": agent.description,
                "memory_key": agent.memory_key
            }
            for key, agent in self.AGENTS.items()
        ]

    def get_agent_prompts(self, agent_name: str) -> List[str]:
        """Get prompts for specific agent"""
        agent = self.AGENTS.get(agent_name)
        return agent.prompts if agent else []


# Global orchestrator instance
_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create global orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
