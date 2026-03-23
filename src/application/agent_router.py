# src/application/agent_router.py
"""
Agent Router - Handles agent detection and prompt selection.

Part of Clean Architecture - Application layer.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class Agent:
    """Agent definition."""
    name: str
    prompts: List[str]
    memory_key: str
    description: str


# Agent definitions
AGENTS = {
    "architect": Agent(
        name="Architect",
        prompts=[
            "promt-project-adaptation",
            "promt-adr-implementation-planner",
            "create_adr"
        ],
        memory_key="architecture",
        description="System design, ADRs, architecture decisions"
    ),
    "developer": Agent(
        name="Developer",
        prompts=[
            "promt-feature-add",
            "promt-bug-fix",
            "promt-refactoring",
            "promt-implementation"
        ],
        memory_key="code",
        description="Code generation, features, bug fixes"
    ),
    "reviewer": Agent(
        name="Reviewer",
        prompts=[
            "promt-llm-review",
            "promt-security-audit",
            "promt-quality-test"
        ],
        memory_key="reviews",
        description="Code review, security, quality checks"
    ),
    "designer": Agent(
        name="Designer",
        prompts=[
            "promt-ui-generator",
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


# Prompt keywords for selection
PROMPT_KEYWORDS = {
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


class AgentRouter:
    """Handles agent detection and prompt selection."""

    def detect_agents(self, request: str) -> List[str]:
        """
        Detect which agents are needed based on request.

        Args:
            request: User request

        Returns:
            List of agent names to execute
        """
        request_lower = request.lower()
        needed = []

        for agent_name, keywords in AGENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in request_lower:
                    if agent_name not in needed:
                        needed.append(agent_name)
                    break

        # Default to developer if no specific agent detected
        if not needed:
            needed = ["developer"]

        return needed

    def select_prompt(self, agent_name: str, request: str) -> str:
        """
        Select appropriate prompt for agent based on request.

        Args:
            agent_name: Agent name
            request: User request

        Returns:
            Prompt name to use
        """
        agent = AGENTS.get(agent_name)
        if not agent:
            return list(AGENTS.values())[0].prompts[0]

        request_lower = request.lower()

        # Try to match prompt based on keywords
        for prompt in agent.prompts:
            keywords = PROMPT_KEYWORDS.get(prompt, [])
            for keyword in keywords:
                if keyword in request_lower:
                    return prompt

        # Default to first prompt
        return agent.prompts[0]

    def get_agent(self, agent_name: str) -> Optional[Agent]:
        """Get agent by name."""
        return AGENTS.get(agent_name)

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents."""
        return [
            {
                "key": key,
                "name": agent.name,
                "description": agent.description,
                "prompts": agent.prompts,
                "memory_key": agent.memory_key
            }
            for key, agent in AGENTS.items()
        ]
