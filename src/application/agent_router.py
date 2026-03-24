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
    # Full cycle agent - orchestrates complete development pipeline
    "full_cycle": Agent(
        name="Full Cycle",
        prompts=[
            "promt-feature-add",  # Includes: research → ADR → impl → test → docs
        ],
        memory_key="full_cycle",
        description="Complete development cycle: idea → implementation → tests → fixes → docs"
    ),
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
    # Full cycle keywords - активируют полный цикл с арбитражом
    "full_cycle": ["реализуй", "внедри", "сделай", "e2e", "полный цикл", "end-to-end", "implement", "build"],
    "architect": ["спроектируй", "архитектура", "adr", "design", "architect", "проектирование", "рефакторинг", "refactor"],
    "reviewer": ["проверь", "ревью", "аудит", "тест", "review", "check", "audit", "test"],
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
    AGENT_PRIORITY = ["migration", "full_cycle", "architect", "reviewer", "developer", "designer", "devops"]

    def detect_agents(self, request: str) -> List[str]:
        """
        Detect which agents are needed based on request.

        Priority: migration > full_cycle > architect > reviewer > developer > designer > devops

        Args:
            request: User request

        Returns:
            List of agent names to execute
        """
        request_lower = request.lower()
        needed = []

        # Check for full cycle commands first (реализуй, внедри, сделай, e2e)
        if "full_cycle" in AGENT_KEYWORDS:
            for keyword in AGENT_KEYWORDS["full_cycle"]:
                if keyword in request_lower:
                    # Full cycle detected - determine orchestration based on context
                    return self._orchestrate_full_cycle(request_lower)

        # Check in priority order for other keywords
        for agent_name in self.AGENT_PRIORITY:
            if agent_name == "full_cycle":
                continue
            keywords = AGENT_KEYWORDS.get(agent_name, [])
            for keyword in keywords:
                if keyword in request_lower:
                    needed.append(agent_name)
                    break

        # Default to developer if no specific agent detected
        if not needed:
            needed = ["developer"]

        return needed

    def _orchestrate_full_cycle(self, request_lower: str) -> List[str]:
        """
        Orchestrate full cycle based on request context.

        Determines which agents to invoke:
        - Simple feature → developer only (promt-feature-add has full cycle built-in)
        - UI/UX task → designer + developer + reviewer
        - Complex architecture → architect + developer + reviewer + devops
        - Deployment → developer + reviewer + devops

        Args:
            request_lower: Lowercased request

        Returns:
            Ordered list of agents to execute
        """
        orchestration = []

        # Check for UI/UX requirements
        ui_keywords = ["ui", "ux", "дизайн", "интерфейс", "design", "component", "кнопка", "карточка"]
        has_ui = any(kw in request_lower for kw in ui_keywords)

        # Check for deployment/infrastructure requirements
        deploy_keywords = ["deploy", "деплой", "ci", "cd", "docker", "kubernetes", "pipeline"]
        has_deploy = any(kw in request_lower for kw in deploy_keywords)

        # Check for complex architecture (new system, redesign, major feature)
        complex_keywords = ["спроектируй", "архитектура", "нов систем", "редизайн", "architecture"]
        has_complex = any(kw in request_lower for kw in complex_keywords)

        # Orchestration logic
        if has_complex:
            # Complex task: Architect first for design decisions
            orchestration.append("architect")
            orchestration.append("developer")
            orchestration.append("reviewer")
            if has_deploy:
                orchestration.append("devops")
        elif has_ui:
            # UI task: Designer first, then developer, then reviewer
            orchestration.append("designer")
            orchestration.append("developer")
            orchestration.append("reviewer")
        elif has_deploy:
            # Deployment task: Developer + Reviewer + DevOps
            orchestration.append("developer")
            orchestration.append("reviewer")
            orchestration.append("devops")
        else:
            # Simple feature: Use full cycle prompt (already includes all phases)
            # This goes directly to promt-feature-add which has research→impl→test→docs built-in
            orchestration.append("full_cycle")

        return orchestration

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
