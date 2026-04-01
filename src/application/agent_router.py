# src/application/agent_router.py
"""
Agent Router - Handles agent detection and prompt selection.

Part of Clean Architecture - Application layer.
Now integrated with PromptRegistry for unified pipeline: Intent → Agent → Prompt
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Import PromptRegistry from cascade module
from src.application.router.cascade import (
    PromptRegistry,
    PromptEntry,
    PromptMetadata,
    PromptCategory,
)


@dataclass
class Agent:
    """Agent definition."""
    name: str
    prompts: List[str]
    memory_key: str
    description: str
    # Agent category for PromptRegistry mapping
    category: PromptCategory = PromptCategory.CUSTOM
    # Whether to use checkpoint executor for write operations
    use_checkpoint: bool = True


# Agent definitions
AGENTS = {
    # Full cycle agent - orchestrates complete development pipeline
    "full_cycle": Agent(
        name="Full Cycle",
        prompts=[
            "promt-feature-add",  # Includes: research → ADR → impl → test → docs
        ],
        memory_key="full_cycle",
        description="Complete development cycle: idea → implementation → tests → fixes → docs",
        category=PromptCategory.CODE,
    ),
    "architect": Agent(
        name="Architect",
        prompts=[
            "promt-project-adaptation",
            "promt-adr-implementation-planner",
            "create_adr"
        ],
        memory_key="architecture",
        description="System design, ADRs, architecture decisions",
        category=PromptCategory.ANALYSIS,
        use_checkpoint=False,
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
        description="Code generation, features, bug fixes",
        category=PromptCategory.CODE,
    ),
    "reviewer": Agent(
        name="Reviewer",
        prompts=[
            "promt-llm-review",
            "promt-security-audit",
            "promt-quality-test",
            "promt-readme-validator"
        ],
        memory_key="reviews",
        description="Code review, security, quality checks",
        category=PromptCategory.QA,
        use_checkpoint=False,
    ),
    "designer": Agent(
        name="Designer",
        prompts=[
            "promt-ui-generator",
        ],
        memory_key="design",
        description="UI/UX design and generation",
        category=PromptCategory.CREATIVE,
        use_checkpoint=False,
    ),
    "devops": Agent(
        name="DevOps",
        prompts=[
            "promt-ci-cd-pipeline",
            "promt-onboarding"
        ],
        memory_key="devops",
        description="CI/CD, deployment, infrastructure",
        category=PromptCategory.CUSTOM,
        use_checkpoint=False,
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
        description="Migration planning and execution",
        category=PromptCategory.CUSTOM,
        use_checkpoint=False,
    ),
}


# Keywords for agent detection (in priority order)
# More specific patterns FIRST
AGENT_KEYWORDS = {
    "migration": ["мигрируй", "миграц", "migrat", "переход", "migrate", "от old", "на domain", "миграция"],
    # Full cycle keywords - активируют полный цикл с арбитражом
    "full_cycle": ["реализуй", "внедри", "сделай", "e2e", "полный цикл", "end-to-end", "implement", "build"],
    "architect": ["спроектируй", "архитектура", "adr", "design", "architect", "проектирование", "рефакторинг", "refactor"],
    "reviewer": ["проверь", "исправь", "приведи", "исправить", "привести", "фикс", "fix", "ревью", "аудит", "тест", "review", "check", "audit", "test", "standard", "standards"],
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
    "promt-migration-planner": ["миграц", "миграция", "migrat", "план миграции", "migrate plan", "monolith", "microservices", "переход с", "на микросервисы"],
    "promt-migration-implementation": ["выполни миграцию", "запусти миграцию", "execute migration"],
    "promt-migration-review": ["проверь миграцию", "верифицируй миграцию", "verify migration"],
    "promt-migration-devops": ["тест миграции", "ci/cd миграции"],
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
    "promt-onboarding": ["онбординг", "onboard", "адаптация"],
    # Documentation
    "promt-readme-validator": ["readme", "валидация readme", "проверь документацию", "главная страница", "diataxis", "readme validator", "проверь readme"],
    "promt-readme-sync": ["синхронизируй readme", "обнови readme", "sync readme"]
}


class AgentRouter:
    """
    Handles agent detection and prompt selection.

    Unified pipeline: Intent → Agent → Prompt
    Now uses PromptRegistry for semantic prompt selection.
    """

    # Priority order - more specific agents first
    AGENT_PRIORITY = ["migration", "full_cycle", "architect", "reviewer", "developer", "designer", "devops"]

    def __init__(self):
        """Initialize AgentRouter with PromptRegistry."""
        self._registry: Optional[PromptRegistry] = None
        self._hybrid_router: Optional[Any] = None  # HybridPromptRouter, lazy init

    @property
    def registry(self) -> PromptRegistry:
        """Lazy initialization of PromptRegistry."""
        if self._registry is None:
            self._registry = PromptRegistry()
            self._load_prompts_from_storage()
            self._register_agent_rules()
            self._init_hybrid_router()
        return self._registry

    def _load_prompts_from_storage(self) -> None:
        """Load prompts from file storage into PromptRegistry."""
        from pathlib import Path

        PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"

        # Walk through prompts directory and register prompts
        search_dirs = [
            PROMPTS_DIR,
            PROMPTS_DIR / "universal" / "ai_agent_prompts",
            PROMPTS_DIR / "universal" / "mpv_stages",
            PROMPTS_DIR / "agents",
        ]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            self._scan_directory(search_dir)

    def _scan_directory(self, directory: Path) -> None:
        """Recursively scan directory for prompt files."""
        try:
            for md_file in directory.rglob("*.md"):
                # Skip deprecated and non-prompt files
                if "deprecated" in md_file.parts:
                    continue

                # Extract prompt name from filename
                prompt_name = md_file.stem  # Remove .md

                # Skip non-prompt files
                if prompt_name in ["README", "index", "config"]:
                    continue

                # Read file to extract metadata (first 500 chars)
                try:
                    content = md_file.read_text(encoding="utf-8", errors="ignore")
                    # Extract description from first heading or first line
                    description = ""
                    lines = content.split("\n")
                    for line in lines[:10]:
                        if line.strip() and not line.startswith("---"):
                            description = line.strip()[:200]
                            break

                    # Determine category from path
                    from src.application.router.cascade import PromptCategory
                    category = PromptCategory.GENERAL
                    if "architect" in md_file.parts:
                        category = PromptCategory.ANALYSIS
                    elif "developer" in md_file.parts:
                        category = PromptCategory.CODE
                    elif "reviewer" in md_file.parts:
                        category = PromptCategory.QA
                    elif "designer" in md_file.parts:
                        category = PromptCategory.CREATIVE

                    # Create PromptEntry
                    entry = PromptEntry(
                        name=prompt_name,
                        template=content[:500],  # First 500 chars as template
                        metadata=PromptMetadata(
                            category=category,
                            description=description,
                            tags={prompt_name},
                        ),
                    )

                    # Register if not exists
                    if not self._registry.get_by_name(prompt_name):
                        self._registry.register(entry)

                except Exception as e:
                    # Skip problematic files
                    logger.warning(f"Skipped prompt file {md_file}: {e}")
        except Exception as e:
            logger.warning(f"Error scanning directory {directory}: {e}")

    def _register_agent_rules(self) -> None:
        """
        Register routing rules for each agent's prompts with PromptRegistry.

        This enables HybridPromptRouter to use rules for agent detection.
        """
        if self._registry is None:
            return

        for agent_name, agent in AGENTS.items():
            keywords = AGENT_KEYWORDS.get(agent_name, [])
            for prompt_name in agent.prompts:
                entry = self._registry.get_by_name(prompt_name)
                if entry:
                    # Add agent-specific rules to the entry
                    entry.rules.append({
                        "type": "agent_keyword",
                        "keywords": keywords,
                        "agent": agent_name
                    })

    def _init_hybrid_router(self) -> None:
        """
        Initialize HybridPromptRouter with registered prompts.

        Uses cascade: Rule-based → Semantic → LLM fallback
        """
        from src.application.router.cascade import HybridPromptRouter

        if self._registry is None:
            return

        self._hybrid_router = HybridPromptRouter()
        # Register all prompts with the hybrid router (single call to avoid N rebuilds)
        all_prompts = self._registry.list_all()
        self._hybrid_router.register_prompts(all_prompts)

    def detect_agents(self, request: str, intent_agent: Optional[str] = None) -> List[str]:
        """
        Detect which agents are needed based on request.

        Uses HybridPromptRouter cascade:
        1. Static keyword matching (fast path)
        2. HybridPromptRouter semantic matching (if available)

        Priority: migration > full_cycle > architect > reviewer > developer > designer > devops

        Args:
            request: User request
            intent_agent: Optional agent from P9iRouter.classify() to avoid duplication

        Returns:
            List of agent names to execute
        """
        # If we already have agent from P9iRouter, use it directly
        if intent_agent and intent_agent in AGENTS:
            return [intent_agent]

        request_lower = request.lower()
        needed = []

        # Check for full cycle commands first (реализуй, внедри, сделай, e2e)
        if "full_cycle" in AGENT_KEYWORDS:
            import re
            for keyword in AGENT_KEYWORDS["full_cycle"]:
                # Use word boundary matching to avoid substring matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, request_lower):
                    # Full cycle detected - determine orchestration based on context
                    return self._orchestrate_full_cycle(request_lower)

        # Check in priority order for other keywords (fast path)
        import re
        for agent_name in self.AGENT_PRIORITY:
            if agent_name == "full_cycle":
                continue
            keywords = AGENT_KEYWORDS.get(agent_name, [])
            for keyword in keywords:
                # Use word boundary matching to avoid substring matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, request_lower):
                    needed.append(agent_name)
                    break

        # If no explicit keyword match, try HybridPromptRouter semantic matching
        if not needed and self._hybrid_router is not None:
            try:
                from src.application.router.cascade import RoutingContext
                context = RoutingContext(query=request)
                result = self._hybrid_router.route_sync(context)
                if result.prompt_entry and result.confidence_score >= 0.5:
                    # Extract agent from matched prompt entry rules
                    agent_name = self._get_agent_for_prompt(result.prompt_entry.name)
                    if agent_name:
                        needed = [agent_name]
            except Exception:
                pass  # Fall back to default

        # Default to developer if no specific agent detected
        if not needed:
            needed = ["developer"]

        return needed

    def _get_agent_for_prompt(self, prompt_name: str) -> Optional[str]:
        """Get agent name for a given prompt name."""
        for agent_name, agent in AGENTS.items():
            if prompt_name in agent.prompts:
                return agent_name
        return None

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

        Uses PromptRegistry for semantic matching when available,
        falls back to keyword matching.

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

        # Try semantic matching via PromptRegistry first
        # Access self.registry to trigger lazy initialization if needed
        if self._registry is not None:
            # Get agent's category for filtering
            agent_category = agent.category

            # First try: find prompts by category
            category_results = self.registry.find_by_category(agent_category)

            # Filter by agent's prompts and keyword match
            agent_prompts_set = set(agent.prompts)
            for entry in category_results:
                if entry.name in agent_prompts_set and entry.matches_keyword(request_lower):
                    return entry.name

            # Second try: search prompts in registry and filter
            results = self.registry.search(request, limit=10)
            for entry in results:
                if entry.name in agent_prompts_set:
                    return entry.name

            # Third: use keyword matching within agent's prompts
            for prompt_name in agent.prompts:
                entry = self._registry.get_by_name(prompt_name)
                if entry and entry.matches_keyword(request_lower):
                    return prompt_name

        # Fallback to keyword matching (legacy) - use word boundaries
        import re
        for prompt in agent.prompts:
            keywords = PROMPT_KEYWORDS.get(prompt, [])
            for keyword in keywords:
                # Use word boundary matching - keyword must be standalone word, not substring
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, request_lower):
                    return prompt

        # Default to first prompt
        return agent.prompts[0]

    def select_prompt_entry(self, agent_name: str, request: str) -> Optional[PromptEntry]:
        """
        Select prompt as PromptEntry with full metadata.

        Args:
            agent_name: Agent name
            request: User request

        Returns:
            PromptEntry or None
        """
        prompt_name = self.select_prompt(agent_name, request)
        return self.registry.get_by_name(prompt_name)

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

    def get_unified_keyword_map(self) -> Dict[str, str]:
        """
        Generate unified keyword -> agent_name mapping from AGENT_KEYWORDS.

        This provides a single source of truth for agent keywords,
        replacing duplicative KEYWORD_MAP in P9iRouter.

        Returns:
            Dict mapping keywords to agent names
        """
        unified = {}
        for agent_name, keywords in AGENT_KEYWORDS.items():
            for keyword in keywords:
                unified[keyword] = agent_name
        return unified
