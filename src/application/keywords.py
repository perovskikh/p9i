"""
Keywords - Unified Source of Truth

ЕДИНЫЙ источник для всех keywords системы.
Устраняет дублирование между agent_router.py и p9i_router.py.

Философия:
- AGENT_KEYWORDS: keyword -> agent_name mapping
- PROMPT_KEYWORDS: keyword -> prompt_name mapping
- p9i_router.py использует build_keyword_map() для генерации KEYWORD_MAP

Этот файл НЕ импортирует из p9i_router.py во избежание циклического импорта.
"""

from typing import Dict, List


# Keywords for agent detection (in priority order)
# More specific patterns FIRST
AGENT_KEYWORDS: Dict[str, List[str]] = {
    "explorer": [
        # Russian - MVP
        "как работает", "как работают", "структура", "связи", "зависимости",
        "вызовы", "вызов", "модуль", "файлы", "найди все", "найди где",
        "трассируй", "покажи структуру", "архитектура кода",
        "что делает", "где находится", "найди файл", "навигац",
        "верифицируй", "верификация",
        # English - MVP
        "explore", "trace", "dependencies", "structure", "связи",
        "find all", "where is", "how does", "call chain", "entry point",
        "architectur", "module", "files", "verify", "verification",
        # Russian - Extended
        "глубокий поиск", "проиндексируй", "переиндексируй",
        "построить граф", "анализ связей", "что зависит от", "затронет",
        "impact analysis", "call graph", "dependency graph",
        # English - Extended
        "reindex", "refresh index", "deep search", "analyze module",
        # Analysis & Study (NEW)
        "изучи", "анализ", "анализируй", "проанализируй",
        "консолидируй", "консолидация", "объедини adr",
        "analyze", "analysis", "study", "consolidate", "consolidation",
    ],
    "migration": ["мигрируй", "миграц", "migrat", "переход", "migrate", "от old", "на domain", "миграция"],
    # Full cycle keywords - активируют полный цикл с арбитражом
    "full_cycle": ["реализуй", "внедри", "сделай", "e2e", "полный цикл", "end-to-end", "implement", "build"],
    "architect": ["спроектируй", "архитектура", "adr", "design", "architect", "проектирование"],
    "reviewer": [
        # Claude Code simplify.ts patterns
        "simplify", "simplify code", "code review", "review changes",
        # Verification patterns
        "verify", "верифицируй", "verification", "adversarial", "тестирование",
        # Quality patterns
        "quality", "efficiency", "efficiency review", "performance",
        # Reuse patterns
        "reuse", "refactor", "рефакторинг", "улучши код",
        # Existing Russian patterns
        "проверь", "исправь", "приведи", "исправить", "привести", "фикс", "fix",
        "ревью", "аудит", "тест", "review", "check", "audit", "test",
        "standard", "standards",
    ],
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
PROMPT_KEYWORDS: Dict[str, List[str]] = {
    # Explorer prompts
    "promt-explorer-mvp": ["структура", "связи", "зависимости", "trace", "как работает", "вызовы", "модуль", "файлы", "explore", "dependencies", "structure", "найди где", "где находится", "найди все", "трассируй", "покажи структуру", "архитектура кода", "что делает", "найди файл", "навигац", "изучи", "анализ", "анализируй"],
    "promt-explorer-extended": ["глубокий поиск", "проиндексируй", "переиндексируй", "reindex", "refresh index", "deep search", "analyze module", "построить граф", "call graph", "dependency graph", "анализ связей", "что зависит от", "затронет", "impact analysis", "проанализируй", "консолидируй", "consolidate"],
    # Architect prompts
    "promt-architect-parallel-research": ["parallel", "3-phase", "research phase", "параллельн"],
    # Reviewer prompts (Claude Code patterns)
    "promt-reviewer-mvp": ["quick review", "fast review", "ревью", "проверь код", "check code", "git diff", "simplify", "code cleanup"],
    "promt-reviewer-enhanced": ["full review", "deep review", "3-phase", "parallel review", "reuse", "quality", "efficiency", "рефакторинг"],
    "promt-reviewer-security": ["security", "security review", "уязвимост", "sql injection", "xss", "auth bypass", "безопасност"],
    "promt-verification": ["verify", "верифицируй", "проверь реализацию", "verification", "adversarial", "тест", "прогон"],
    # Migration prompts
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
    "promt-readme-validator": ["readme", "валидация readme", "проверь документацию", "главная страница", "diataxis", "readme validator", "проверь readme", "приведи", "к стандарту", "документацию к стандарту", "приведи к стандарту"],
    "promt-readme-sync": ["синхронизируй readme", "обнови readme", "sync readme"]
}
