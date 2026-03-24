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
    ),
    "migration": Agent(
        name="Migration",
        prompts=[
            "promt-migration-planner",
            "promt-migration-implementation",
            "promt-migration-review",
            "promt-migration-devops"
        ],
        memory_key="migration",
        description="Migration planning and execution"
    ),
}


# Keywords for agent detection (in priority order)
# More specific patterns FIRST
AGENT_KEYWORDS = {
    "migration": ["мигрируй", "миграц", "migrat", "переход", "migrate", "от old", "на domain", "миграция"],
    "architect": ["спроектируй", "архитектура", "adr", "design", "architect", "проектирование", "рефакторинг", "refactor"],
    "reviewer": ["проверь", "ревью", "аудит", "тест", "review", "check", "audit", "test"],  # Перенесено ВЫШЕ developer
    # Full cycle shortcuts → routes to promt-feature-add (already has full cycle)
    # "developer_full_cycle": ["реализуй", "внедри", "сделай", "реализуем", "внедряем", "выполни", "implement", "build", "deploy"],
    "developer": ["создай", "добавь", "напиши", "код", "feature", "create", "add", "code"],
    "designer": [
        # English
        "ui", "ux", "design", "button", "card", "component",
        "color", "palette", "typography", "font", "icon",
        "layout", "responsive", "accessibility", "a11y",
        # Russian
        "дизайн", "интерфейс", "компонент", "кнопка", "карточка",
        "цвет", "палитра", "шрифт", "иконка", "верстка",
    ],
    "devops": ["ci", "cd", "deploy", "docker", "kubernetes", "pipeline", "деплой"]
}


# Prompt keywords for selection
PROMPT_KEYWORDS = {
    "promt-migration-planner": ["миграц", "migrat", "план миграции", "migrate plan"],
    "promt-migration-implementation": ["выполни миграцию", "запусти миграцию", "execute migration"],
    "promt-migration-review": ["проверь миграцию", "верифицируй миграцию", "verify migration"],
    "promt-migration-devops": ["тест миграции", "ci/cd миграции"],
    "promt-architect-design": ["спроектируй", "проектирование", "design"],
    "promt-architect-review": ["ревью", "review", "анализ"],
    "create_adr": ["adr", "документация"],
    # Full cycle implementation (idea → implementation → testing → fixes → docs)
    # Full cycle shortcuts now route to promt-feature-add (already has full cycle)
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

    # Priority order - more specific agents first
    AGENT_PRIORITY = ["migration", "architect", "reviewer", "developer", "designer", "devops"]

    def detect_agents(self, request: str) -> List[str]:
        """
        Detect which agents are needed based on request.

        Priority: migration > architect > developer > reviewer > designer > devops

        Args:
            request: User request

        Returns:
            List of agent names to execute
        """
        request_lower = request.lower()
        needed = []

        # Check in priority order - migration checked FIRST
        for agent_name in self.AGENT_PRIORITY:
            keywords = AGENT_KEYWORDS.get(agent_name, [])
            for keyword in keywords:
                if keyword in request_lower:
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
