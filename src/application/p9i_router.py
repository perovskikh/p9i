# src/application/p9i_router.py
"""
P9iRouter - ЕДИНЫЙ УМНЫЙ МАРШРУТИЗАТОР

Философия:
- Одна точка входа: "p9i" фраза
- Единая логика классификации намерений
- Интеллектуальная оркестрация (умнее LangChain)
- NO LLM для routing!

Part of Clean Architecture - Application layer.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Protocol, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Типы намерений в порядке приоритета."""

    # === ПРИОРИТЕТ 1: System Commands ===
    COMMAND = auto()              # /help, /exit, /clear, /status

    # === ПРИОРИТЕТ 2: Explicit Prompt Management ===
    PROMPT_CMD = auto()           # /prompt list, /prompt save, /prompt load

    # === ПРИОРИТЕТ 3: Pack Triggers (Plugin Packs) ===
    PACK = auto()                 # k8s-pack, ci-cd-pack, pinescript-v6

    # === ПРИОРИТЕТ 4: Agent-Based Multi-Task ===
    AGENT_TASK = auto()           # "реализуй", "спроектируй", "проверь"

    # === ПРИОРИТЕТ 5: Simple NL Query ===
    NL_QUERY = auto()            # "покажи список", "что умеет p9i?"

    # === ПРИОРИТЕТ 6: System Configuration ===
    SYSTEM = auto()              # "инициализация p9i", "adapt to project"

    # === ПРИОРИТЕТ 7: Fallback ===
    UNKNOWN = auto()


@dataclass
class Intent:
    """Результат классификации намерения."""
    type: IntentType
    confidence: float = 0.0           # 0.0-1.0
    agent_name: Optional[str] = None   # Для AGENT_TASK
    prompt_name: Optional[str] = None  # Для прямого выполнения
    matched_keyword: Optional[str] = None
    metadata: Dict[str, Any] = None


class Processor(Protocol):
    """Интерфейс для обработчиков намерений."""

    def can_handle(self, intent: Intent) -> bool:
        """Может ли этот обработчик обрабатывать данное намерение?"""
        ...

    async def process(self, intent: Intent, request: str, context: dict) -> dict:
        """Обработать запрос."""
        ...


class P9iRouter:
    """
    ЕДИНЫЙ УМНЫЙ МАРШРУТИЗАТОР

    Ключевое отличие от LangChain:
    - НЕ используем LLM для routing
    - Keyword classification + priority
    - Интеллектуальная multi-agent оркестрация
    """

    def __init__(self):
        self.processors: List[Processor] = [
            CommandProcessor(),
            PromptCmdProcessor(),
            PackProcessor(),
            AgentTaskProcessor(),
            NLQueryProcessor(),
            SystemProcessor(),
        ]
        self._init_keywords()

    def _init_keywords(self):
        """Инициализировать единую карту ключевых слов."""
        self.KEYWORD_MAP = {
            # === SYSTEM COMMANDS (highest priority) ===
            "/help": IntentType.COMMAND,
            "/exit": IntentType.COMMAND,
            "/clear": IntentType.COMMAND,
            "/status": IntentType.COMMAND,
            "/?": IntentType.COMMAND,

            # === PROMPT COMMANDS ===
            "/prompt": IntentType.PROMPT_CMD,

            # === FULL CYCLE (multi-agent orchestration) ===
            "реализуй": (IntentType.AGENT_TASK, "full_cycle"),
            "внедри": (IntentType.AGENT_TASK, "full_cycle"),
            "сделай": (IntentType.AGENT_TASK, "full_cycle"),
            "e2e": (IntentType.AGENT_TASK, "full_cycle"),
            "полный цикл": (IntentType.AGENT_TASK, "full_cycle"),
            "end-to-end": (IntentType.AGENT_TASK, "full_cycle"),
            "implement": (IntentType.AGENT_TASK, "full_cycle"),
            "build": (IntentType.AGENT_TASK, "full_cycle"),

            # === ARCHITECT ===
            "спроектируй": (IntentType.AGENT_TASK, "architect"),
            "архитектура": (IntentType.AGENT_TASK, "architect"),
            "adr": (IntentType.AGENT_TASK, "architect"),
            "design": (IntentType.AGENT_TASK, "architect"),
            "architect": (IntentType.AGENT_TASK, "architect"),
            "проектирование": (IntentType.AGENT_TASK, "architect"),

            # === DEVELOPER ===
            "создай": (IntentType.AGENT_TASK, "developer"),
            "добавь": (IntentType.AGENT_TASK, "developer"),
            "напиши": (IntentType.AGENT_TASK, "developer"),
            "код": (IntentType.AGENT_TASK, "developer"),
            "feature": (IntentType.AGENT_TASK, "developer"),
            "create": (IntentType.AGENT_TASK, "developer"),
            "add": (IntentType.AGENT_TASK, "developer"),
            "code": (IntentType.AGENT_TASK, "developer"),
            "фича": (IntentType.AGENT_TASK, "developer"),
            "новую возможность": (IntentType.AGENT_TASK, "developer"),
            "add feature": (IntentType.AGENT_TASK, "developer"),
            "new feature": (IntentType.AGENT_TASK, "developer"),
            "создать компонент": (IntentType.AGENT_TASK, "developer"),
            "создать": (IntentType.AGENT_TASK, "developer"),
            "добавить": (IntentType.AGENT_TASK, "developer"),
            "добавить функт": (IntentType.AGENT_TASK, "developer"),

            # === REVIEWER ===
            "проверь": (IntentType.AGENT_TASK, "reviewer"),
            "проведи": (IntentType.AGENT_TASK, "reviewer"),
            "исправь": (IntentType.AGENT_TASK, "reviewer"),
            "приведи": (IntentType.AGENT_TASK, "reviewer"),
            "исправить": (IntentType.AGENT_TASK, "reviewer"),
            "привести": (IntentType.AGENT_TASK, "reviewer"),
            "фикс": (IntentType.AGENT_TASK, "reviewer"),
            "fix": (IntentType.AGENT_TASK, "reviewer"),
            "ревью": (IntentType.AGENT_TASK, "reviewer"),
            "аудит": (IntentType.AGENT_TASK, "reviewer"),
            "тест": (IntentType.AGENT_TASK, "reviewer"),
            "review": (IntentType.AGENT_TASK, "reviewer"),
            "check": (IntentType.AGENT_TASK, "reviewer"),
            "audit": (IntentType.AGENT_TASK, "reviewer"),
            "test": (IntentType.AGENT_TASK, "reviewer"),
            "standard": (IntentType.AGENT_TASK, "reviewer"),
            "standards": (IntentType.AGENT_TASK, "reviewer"),
            "refactor": (IntentType.AGENT_TASK, "reviewer"),
            "рефакторинг": (IntentType.AGENT_TASK, "reviewer"),

            # === DESIGNER ===
            "ui": (IntentType.AGENT_TASK, "designer"),
            "ux": (IntentType.AGENT_TASK, "designer"),
            "дизайн": (IntentType.AGENT_TASK, "designer"),
            "интерфейс": (IntentType.AGENT_TASK, "designer"),
            "button": (IntentType.AGENT_TASK, "designer"),
            "card": (IntentType.AGENT_TASK, "designer"),
            "component": (IntentType.AGENT_TASK, "designer"),
            "кнопка": (IntentType.AGENT_TASK, "designer"),
            "карточка": (IntentType.AGENT_TASK, "designer"),
            "стиль": (IntentType.AGENT_TASK, "designer"),
            "палитра": (IntentType.AGENT_TASK, "designer"),
            "шрифт": (IntentType.AGENT_TASK, "designer"),
            "иконка": (IntentType.AGENT_TASK, "designer"),
            "ui component": (IntentType.AGENT_TASK, "designer"),
            "ux design": (IntentType.AGENT_TASK, "designer"),
            "ui design": (IntentType.AGENT_TASK, "designer"),
            "generate ui": (IntentType.AGENT_TASK, "designer"),
            "create ui": (IntentType.AGENT_TASK, "designer"),
            "компонент": (IntentType.AGENT_TASK, "designer"),

            # === DEVOPS ===
            "ci": (IntentType.AGENT_TASK, "devops"),
            "cd": (IntentType.AGENT_TASK, "devops"),
            "deploy": (IntentType.AGENT_TASK, "devops"),
            "деплой": (IntentType.AGENT_TASK, "devops"),
            "docker": (IntentType.AGENT_TASK, "devops"),
            "kubernetes": (IntentType.AGENT_TASK, "devops"),
            "k8s": (IntentType.AGENT_TASK, "devops"),
            "pipeline": (IntentType.AGENT_TASK, "devops"),

            # === MIGRATION ===
            "миграция": (IntentType.AGENT_TASK, "migration"),
            "мигрируй": (IntentType.AGENT_TASK, "migration"),
            "миграц": (IntentType.AGENT_TASK, "migration"),
            "migrate": (IntentType.AGENT_TASK, "migration"),
            "migration": (IntentType.AGENT_TASK, "migration"),
            "переход": (IntentType.AGENT_TASK, "migration"),

            # === SYSTEM ADAPTATION ===
            "init p9i": IntentType.SYSTEM,
            "p9i init": IntentType.SYSTEM,
            "инициализация p9i": IntentType.SYSTEM,
            "подключи систему": IntentType.SYSTEM,
            "новый проект": IntentType.SYSTEM,
            "new project": IntentType.SYSTEM,
            "адаптируй": IntentType.SYSTEM,
            "adapt": IntentType.SYSTEM,
            "onboard": IntentType.SYSTEM,
            "адаптац": IntentType.SYSTEM,

            # === PACK TRIGGERS ===
            "k8s": IntentType.PACK,
            "kubernetes pack": IntentType.PACK,
            "ci-cd": IntentType.PACK,
            "pipeline pack": IntentType.PACK,
            "pinescript": IntentType.PACK,
            "tradingview": IntentType.PACK,
            "pinescript-v6": IntentType.PACK,

            # === UI/UX GENERATION ===
            "ui component": (IntentType.AGENT_TASK, "designer"),
            "ux design": (IntentType.AGENT_TASK, "designer"),
            "ui design": (IntentType.AGENT_TASK, "designer"),
            "generate ui": (IntentType.AGENT_TASK, "designer"),
            "create ui": (IntentType.AGENT_TASK, "designer"),
            "ui ": (IntentType.AGENT_TASK, "designer"),
            "ux ": (IntentType.AGENT_TASK, "designer"),

            # === BROWSER INTEGRATION ===
            "browser": (IntentType.AGENT_TASK, "developer"),
            "браузер": (IntentType.AGENT_TASK, "developer"),
            "автоматизация браузера": (IntentType.AGENT_TASK, "developer"),
            "playwright": (IntentType.AGENT_TASK, "developer"),
            "puppeteer": (IntentType.AGENT_TASK, "developer"),

            # === SECURITY ===
            "уязвим": (IntentType.AGENT_TASK, "reviewer"),
            "уязвимост": (IntentType.AGENT_TASK, "reviewer"),
            "security": (IntentType.AGENT_TASK, "reviewer"),
            "безопасност": (IntentType.AGENT_TASK, "reviewer"),
            "audit": (IntentType.AGENT_TASK, "reviewer"),

            # === BUG FIX ===
            "баг": (IntentType.AGENT_TASK, "developer"),
            "исправить ошибку": (IntentType.AGENT_TASK, "developer"),
            "fix bug": (IntentType.AGENT_TASK, "developer"),
            "найди": (IntentType.AGENT_TASK, "developer"),
            "фикс": (IntentType.AGENT_TASK, "developer"),
            "ошибку": (IntentType.AGENT_TASK, "developer"),
            "исправить": (IntentType.AGENT_TASK, "developer"),
            "исправь": (IntentType.AGENT_TASK, "developer"),
            "bug": (IntentType.AGENT_TASK, "developer"),

            # === TESTING ===
            "напиши тест": (IntentType.AGENT_TASK, "reviewer"),
            "проверь": (IntentType.AGENT_TASK, "reviewer"),
            "quality": (IntentType.AGENT_TASK, "reviewer"),
            "тест": (IntentType.AGENT_TASK, "reviewer"),
            "test": (IntentType.AGENT_TASK, "reviewer"),

            # === REFACTORING ===
            "упрости код": (IntentType.AGENT_TASK, "architect"),
            "улучшить код": (IntentType.AGENT_TASK, "architect"),
            "рефакторинг": (IntentType.AGENT_TASK, "architect"),
            "модернизируй": (IntentType.AGENT_TASK, "architect"),
            "оптимизируй": (IntentType.AGENT_TASK, "architect"),
            "перепиши": (IntentType.AGENT_TASK, "architect"),
            "упрости": (IntentType.AGENT_TASK, "architect"),
            "улучшить": (IntentType.AGENT_TASK, "architect"),
            "улучши": (IntentType.AGENT_TASK, "architect"),
            "refactor": (IntentType.AGENT_TASK, "architect"),

            # === VERSIONING ===
            "версион": IntentType.NL_QUERY,
            "version": IntentType.NL_QUERY,

            # === ONBOARDING ===
            "подключи": IntentType.SYSTEM,
            "onboard": IntentType.SYSTEM,
        }

    def classify(self, request: str) -> Intent:
        """
        Классифицировать намерение.

        Приоритет проверки:
        1. P9i prefix (p9i /help, p9i создай)
        2. System Commands (/help, /exit)
        3. Prompt Commands (/prompt)
        4. Pack Triggers (k8s, pinescript)
        5. Agent Tasks (реализуй, спроектируй, проверь)
        6. NL Queries (покажи, что умеет)
        7. System (init p9i, adapt)
        """
        request_lower = request.lower().strip()

        # 0. Проверка p9i prefix (p9i /help, p9i создай функцию)
        p9i_prefix = "p9i "
        if request_lower.startswith(p9i_prefix):
            # Убираем префикс и обрабатываем как обычный запрос
            request_stripped = request_lower[len(p9i_prefix):].strip()
            if request_stripped:
                # Рекурсивно классифицируем без префикса
                # Но сохраняем информацию что был префикс
                stripped_request = request_stripped if len(request_stripped) < len(request) else request_stripped
                result = self._classify_internal(stripped_request)
                # Увеличиваем confidence если был p9i prefix
                if result.confidence < 1.0:
                    result.confidence = min(1.0, result.confidence + 0.1)
                return result
            else:
                # p9i без аргументов - показываем capabilities
                return Intent(
                    type=IntentType.NL_QUERY,
                    confidence=0.8,
                    matched_keyword="p9i",
                    metadata={"bare_p9i": True}
                )

        return self._classify_internal(request_lower)

    def _classify_internal(self, request_lower: str) -> Intent:

        # 1. Проверка prompt commands (HIGHER priority than system commands!)
        if request_lower.startswith('/prompt'):
            return Intent(
                type=IntentType.PROMPT_CMD,
                confidence=1.0,
                matched_keyword="/prompt",
                metadata={"command": request_lower}
            )

        # 2. Проверка system commands (исключаем /prompt)
        if request_lower.startswith(('/', '!', '\\')):
            return Intent(
                type=IntentType.COMMAND,
                confidence=1.0,
                matched_keyword=request_lower.split()[0],
                metadata={"command": request_lower}
            )

        # 3. Проверка agent tasks FIRST (before packs to prevent conflicts)
        agent_match = self._check_agents(request_lower)
        if agent_match:
            return Intent(
                type=IntentType.AGENT_TASK,
                confidence=0.90,
                agent_name=agent_match,
                matched_keyword=request_lower,
                metadata={"agent": agent_match}
            )

        # 4. Проверка pack triggers
        pack_match = self._check_packs(request_lower)
        if pack_match:
            return Intent(
                type=IntentType.PACK,
                confidence=0.95,
                prompt_name=pack_match.get("prompt_file"),
                matched_keyword=pack_match.get("matched_keyword"),
                metadata=pack_match
            )

        # 5. Check NL queries
        if self._is_nl_query(request_lower):
            return Intent(
                type=IntentType.NL_QUERY,
                confidence=0.70,
                matched_keyword="nl",
                metadata={"query": request_lower}
            )

        # 6. Check for bare "p9i" command - show capabilities
        if request_lower.strip() == "p9i":
            return Intent(
                type=IntentType.NL_QUERY,
                confidence=1.0,
                matched_keyword="p9i",
                metadata={"query": "what can you do"}
            )

        # 7. Check system commands
        if self._is_system_command(request_lower):
            return Intent(
                type=IntentType.SYSTEM,
                confidence=0.80,
                matched_keyword="system",
                metadata={"command": request_lower}
            )

        # 7. Fallback
        intent = Intent(
            type=IntentType.UNKNOWN,
            confidence=0.30,
            matched_keyword="unknown",
            metadata={"original": request_lower}
        )
        logger.debug(f"classify() returning UNKNOWN fallback: {intent.type}")
        return intent

    def _check_packs(self, request_lower: str) -> Optional[dict]:
        """Проверить pack triggers."""
        try:
            from src.storage.packs import get_pack_loader
            pack_loader = get_pack_loader()
            return pack_loader.find_by_trigger(request_lower)
        except Exception as e:
            logger.warning(f"Pack check failed: {e}")
            return None

    def _check_agents(self, request_lower: str) -> Optional[tuple]:
        """Проверить agent keywords (longest first) with word boundary matching."""
        import re
        # Priority order (longest first!) для избежания конфликтов
        for keyword, mapping in sorted(
            self.KEYWORD_MAP.items(),
            key=lambda x: len(x[0]),
            reverse=True
        ):
            if isinstance(mapping, tuple) and mapping[0] == IntentType.AGENT_TASK:
                # Use word boundary matching to avoid substring matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, request_lower):
                    return mapping[1]  # Return agent_name

        return None

    def _is_nl_query(self, request_lower: str) -> bool:
        """Определить NL query."""
        # Expand patterns to catch more queries
        nl_patterns = [
            r'^покажи',           # show
            r'^список',           # list
            r'^что\s+(умеешь|можешь)',  # what can
            r'^как\s+(работает|использовать)',  # how
            r'^help$',            # help (exact)
            r'^what\s+can',      # what can
            r'^status',          # status
            r'^version',         # version
            r'^show\s+',         # show ...
            r'^list\s+',         # list ...
            r'^agents',          # agents
            r'^version\s+',     # version ...
            r'^help\s+',        # help ...
        ]
        return any(re.match(p, request_lower) for p in nl_patterns)

    def _is_system_command(self, request_lower: str) -> bool:
        """Определить system command."""
        sys_patterns = [
            r'init\s+p9i',
            r'инициализация\s+p9i',
            r'подключи\s+(систему|проект)',
            r'новый\s+проект',
            r'адаптируй',
            r'onboard',
        ]
        return any(re.search(p, request_lower) for p in sys_patterns)

    async def route(self, request: str, context: dict = None) -> dict:
        """
        ОСНОВНАЯ ТОЧКА ВХОДА!

        КОНТУР:
        User → P9iRouter.classify() → P9iRouter.route()
          → Processor.process() → Response
        """
        if context is None:
            context = {}

        # Step 1: Classify the intent
        intent = self.classify(request)

        # Step 2: Handle special cases that need immediate response
        # (These are command-line style shortcuts)
        request_clean = request.lower().strip()
        p9i_prefix = "p9i "

        # Bare "p9i" command - show capabilities
        if request_clean == "p9i":
            return {
                "status": "success",
                "output": """
# p9i - Intelligent AI Assistant

## Usage
- Natural language: "p9i создай функцию"
- System commands: /help, /exit, /clear, /status
- Prompt management: /prompt list

## Examples
- "p9i реализуй систему авторизации"
- "p9i спроектируй архитектуру API"
- "p9i проверь код на безопасность"
                """.strip(),
                "processor": "CommandProcessor"
            }

        # Commands with p9i prefix: strip and handle simple cases
        if request_clean.startswith(p9i_prefix):
            request_stripped = request_clean[len(p9i_prefix):].strip()
            if request_stripped in ['/help', '/?', 'help']:
                return {
                    "status": "success",
                    "output": """
# p9i - Intelligent AI Assistant

## Usage
- Natural language: "p9i создай функцию"
- System commands: /help, /exit, /clear, /status
- Prompt management: /prompt list

## Examples
- "p9i реализуй систему авторизации"
- "p9i спроектируй архитектуру API"
- "p9i проверь код на безопасность"
                    """.strip(),
                    "processor": "CommandProcessor"
                }
            elif request_stripped in ['/exit', '/quit', 'exit']:
                return {"status": "success", "message": "Goodbye!", "processor": "CommandProcessor"}
            elif request_stripped in ['/status', 'status']:
                return {"status": "success", "message": "P9iRouter is running.", "processor": "CommandProcessor"}
            elif request_stripped in ['/clear']:
                return {"status": "success", "message": "Context cleared.", "processor": "CommandProcessor"}
            elif request_stripped in ['init p9i', 'инициализация p9i', 'адаптируй', 'адаптац']:
                # Route to SystemProcessor
                for processor in self.processors:
                    if processor.can_handle(intent):
                        return await processor.process(intent, request, context)
            elif request_stripped.startswith('/'):
                return {"status": "error", "error": f"Unknown command: {request_stripped}"}

        # Step 3: Route to appropriate processor based on classified intent
        for processor in self.processors:
            if processor.can_handle(intent):
                result = await processor.process(intent, request, context)
                result["intent_type"] = intent.type.name
                return result

        # Fallback: unknown intent
        return {"status": "error", "error": f"Unknown command: {request}"}

    def _extract_clean_request(self, request: str) -> str:
        """Extract request without p9i prefix."""
        request_lower = request.lower().strip()
        p9i_prefix = "p9i "
        if request_lower.startswith(p9i_prefix):
            stripped = request_lower[len(p9i_prefix):].strip()
            if stripped:
                return stripped
        return ""  # No prefix or empty after strip

    async def _route_with_cascade(self, request: str, context: dict) -> dict:
        """CascadeRouter fallback для сложных запросов."""
        try:
            from src.application.router.cascade import (
                HybridPromptRouter,
                RoutingContext as V2Context,
                PromptRegistry,
                PromptEntry,
                PromptMetadata,
            )

            # Инициализация V2 роутера
            if not hasattr(self, '_v2_router'):
                self._v2_router = HybridPromptRouter()
                # Регистрация базовых промтов
                registry = PromptRegistry()
                # Добавляем дефолтные промты для V2
                for name, template, tags in [
                    ("developer", "Создай код: {query}", {"code", "feature"}),
                    ("architect", "Спроектируй: {query}", {"architecture", "design"}),
                    ("reviewer", "Проверь: {query}", {"review", "security"}),
                    ("designer", "Создай UI: {query}", {"ui", "design"}),
                    ("devops", "Деплой: {query}", {"deploy", "k8s"}),
                ]:
                    entry = PromptEntry(
                        name=name,
                        template=template,
                        metadata=PromptMetadata(tags=tags, description=f"{name} task")
                    )
                    registry.register(entry)

                self._v2_router.register_prompts(registry.list_all())

            # V2 роутинг
            v2_context = V2Context(query=request, metadata=context)
            result = await self._v2_router.route(v2_context)

            if result.is_successful():
                return {
                    "status": "success",
                    "output": f"[V2 Router] {result.prompt_entry.name}: {result.reasoning}",
                    "v2_strategy": result.routing_strategy,
                    "confidence": result.confidence_score,
                    "processor": "V2FallbackProcessor"
                }

        except Exception as e:
            logger.warning(f"V2 fallback failed: {e}")

        return None


# ==================== PROCESSORS ====================

class CommandProcessor(Processor):
    """Обработка system команд."""

    def can_handle(self, intent: Intent) -> bool:
        return intent.type == IntentType.COMMAND

    async def process(self, intent: Intent, request: str, context: dict) -> dict:
        command = intent.metadata.get("command", "") if intent.metadata else request

        handlers = {
            "/help": self._handle_help,
            "/exit": self._handle_exit,
            "/clear": self._handle_clear,
            "/status": self._handle_status,
        }

        handler = handlers.get(command)
        if handler:
            return handler()

        return {"status": "error", "error": f"Unknown command: {command}"}

    def _handle_help(self) -> dict:
        return {
            "status": "success",
            "output": """
# p9i - Intelligent AI Assistant

## Usage
- Natural language: "p9i создай функцию"
- System commands: /help, /exit, /clear, /status
- Prompt management: /prompt list, /prompt save <name>

## Examples
- "p9i реализуй систему авторизации"
- "p9i спроектируй архитектуру API"
- "p9i проверь код на безопасность"
- "p9i создай UI компонент"

## Available Agents
- **full_cycle**: Complete development pipeline (idea → impl → test → docs)
- **architect**: System design, ADRs, architecture decisions
- **developer**: Code generation, features, bug fixes
- **reviewer**: Code review, security, quality checks
- **designer**: UI/UX design and generation
- **devops**: CI/CD, deployment, infrastructure
- **migration**: Migration planning and execution
            """,
            "processor": "CommandProcessor"
        }

    def _handle_exit(self) -> dict:
        return {
            "status": "success",
            "message": "Goodbye! Use /help for more information.",
            "processor": "CommandProcessor"
        }

    def _handle_clear(self) -> dict:
        return {
            "status": "success",
            "message": "Context cleared.",
            "processor": "CommandProcessor"
        }

    def _handle_status(self) -> dict:
        return {
            "status": "success",
            "message": "P9iRouter is running normally.",
            "processor": "CommandProcessor"
        }


class PromptCmdProcessor(Processor):
    """Обработка /prompt команд."""

    def can_handle(self, intent: Intent) -> bool:
        return intent.type == IntentType.PROMPT_CMD

    async def process(self, intent: Intent, request: str, context: dict) -> dict:
        parts = request.split(maxsplit=2)

        if len(parts) < 2:
            return {"status": "error", "error": "Usage: /prompt <command> [args]"}

        cmd = parts[1]
        args = parts[2] if len(parts) > 2 else ""

        handlers = {
            'list': self._handle_list,
            'save': self._handle_save,
            'load': self._handle_load,
            'delete': self._handle_delete,
        }

        handler = handlers.get(cmd)
        if handler:
            return await handler(args, context)

        return {"status": "error", "error": f"Unknown /prompt command: {cmd}"}

    async def _handle_list(self, args: str, context: dict) -> dict:
        try:
            from src.api.server import load_registry
            registry = load_registry()
            prompts = registry.get("prompts", [])

            # Ensure prompts is a list, not dict
            if isinstance(prompts, dict):
                prompts = list(prompts.values())
            elif not isinstance(prompts, list):
                prompts = []

            output = "# Available Prompts\n\n"
            for prompt in prompts[:20]:  # Limit output
                name = prompt.get("name", "Unknown")
                description = prompt.get("description", "No description")
                output += f"- **{name}**: {description}\n"

            return {
                "status": "success",
                "output": output,
                "count": len(prompts),
                "processor": "PromptCmdProcessor"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _handle_save(self, args: str, context: dict) -> dict:
        return {
            "status": "error",
            "error": "Prompt saving not yet implemented. Use the filesystem directly."
        }

    async def _handle_load(self, args: str, context: dict) -> dict:
        return {
            "status": "error",
            "error": "Use p9i() for execution, not individual prompt loading."
        }

    async def _handle_delete(self, args: str, context: dict) -> dict:
        return {
            "status": "error",
            "error": "Prompt deletion not yet implemented."
        }


class PackProcessor(Processor):
    """Обработка plugin packs."""

    def can_handle(self, intent: Intent) -> bool:
        return intent.type == IntentType.PACK

    async def process(self, intent: Intent, request: str, context: dict) -> dict:
        try:
            from src.services.executor import PromptExecutor
            from src.api.server import load_prompt

            executor = PromptExecutor()
            prompt_name = intent.prompt_name

            if not prompt_name:
                return {"status": "error", "error": "No pack prompt name specified"}

            prompt_data = load_prompt(prompt_name)
            if not prompt_data:
                return {"status": "error", "error": f"Pack prompt not found: {prompt_name}"}

            result = await executor.execute(prompt_data["content"], {
                "request": request,
                "context": context
            })

            return {
                "status": result.get("status", "success"),
                "content": result.get("content", ""),
                "pack": prompt_name,
                "model": result.get("model", "unknown"),
                "processor": "PackProcessor"
            }
        except Exception as e:
            logger.error(f"PackProcessor error: {e}")
            return {"status": "error", "error": str(e)}


class AgentTaskProcessor(Processor):
    """
    МУЛЬТИ-АГЕНТНАЯ ОРКЕСТРАЦИЯ

    Это ключевая разница от LangChain:
    - НЕ используем LLM для routing
    - Используем keyword classification + priority
    - Интеллектуальная оркестрация с multi-agent coordination
    """

    def __init__(self):
        try:
            from src.services.orchestrator import AgentOrchestrator
            self.orchestrator = AgentOrchestrator()
        except Exception as e:
            logger.error(f"Failed to initialize AgentOrchestrator: {e}")
            self.orchestrator = None

    def can_handle(self, intent: Intent) -> bool:
        return intent.type == IntentType.AGENT_TASK

    async def process(self, intent: Intent, request: str, context: dict) -> dict:
        """
        Multi-agent orchestration with PromptEntry propagation.

        Ключевое отличие от ai_prompts:
        - НЕ просто выполняет один prompt
        - ОРКЕСТРИРУЕТ нескольких агентов последовательно
        - Интеллектуальная остановка при ошибках
        - Сохраняет memory между агентами
        - Пропагирует PromptEntry metadata через цепочку агентов
        """
        if not self.orchestrator:
            return {
                "status": "error",
                "error": "AgentOrchestrator not available"
            }

        try:
            # Get initial PromptEntry for this request - use orchestrator's registry
            prompt_entry = None
            if intent.agent_name:
                # Get prompt entry from orchestrator's router registry
                registry = getattr(self.orchestrator.router, 'registry', None)
                if registry:
                    # Get actual prompt name for this agent + request, then look up in registry
                    prompt_name = self.orchestrator.router.select_prompt(intent.agent_name, request)
                    prompt_entry = registry.get_by_name(prompt_name)

            # Route with PromptEntry propagation
            result = await self.orchestrator.route_with_entry(
                request,
                prompt_entry=prompt_entry,
                intent_agent=intent.agent_name,
                context=context)

            return {
                "status": result.get("status", "success"),
                "agents_used": result.get("agents_used", []),
                "results": result.get("results", []),
                "output": result.get("output", ""),
                "errors": result.get("errors", []),
                "prompt_entry": result.get("prompt_entry"),
                "orchestration": "multi-agent",  # KEY DIFFERENCE!
                "processor": "AgentTaskProcessor"
            }
        except Exception as e:
            logger.error(f"AgentTaskProcessor error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "processor": "AgentTaskProcessor"
            }


class NLQueryProcessor(Processor):
    """Обработка NL queries."""

    def can_handle(self, intent: Intent) -> bool:
        return intent.type == IntentType.NL_QUERY

    async def process(self, intent: Intent, request: str, context: dict) -> dict:
        # Simple NL handling without LLM routing
        req_lower = request.lower()

        # Handle bare "p9i" command - show capabilities
        if intent.matched_keyword == "p9i" or req_lower.strip() == "p9i":
            return self._handle_capabilities()

        # List commands
        if "список" in req_lower or "list" in req_lower or "покажи" in req_lower:
            return await self._handle_list_prompts()

        # What can you do
        if "что умеет" in req_lower or "what can" in req_lower or "capabilities" in req_lower:
            return self._handle_capabilities()

        # Version
        if "верси" in req_lower or "version" in req_lower or "v1" in req_lower:
            return self._handle_version()

        # Help
        if "help" in req_lower or "помощь" in req_lower or "справка" in req_lower:
            return self._handle_help()

        # Status
        if "status" in req_lower or "статус" in req_lower:
            return self._handle_status()

        # Agents
        if "agents" in req_lower or "агент" in req_lower:
            return self._handle_agents()

        return {"status": "error", "error": "Unknown NL query"}

    async def _handle_list_prompts(self) -> dict:
        try:
            from src.api.server import load_registry
            registry = load_registry()
            prompts = registry.get("prompts", [])

            # Ensure prompts is a list, not dict
            if isinstance(prompts, dict):
                prompts = list(prompts.values())
            elif not isinstance(prompts, list):
                prompts = []

            output = f"# Available Prompts ({len(prompts)})\n\n"
            for prompt in prompts[:20]:
                name = prompt.get("name", "Unknown")
                description = prompt.get("description", "No description")
                output += f"- **{name}**: {description}\n"

            return {
                "status": "success",
                "output": output,
                "count": len(prompts),
                "processor": "NLQueryProcessor"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _handle_capabilities(self) -> dict:
        return {
            "status": "success",
            "output": """
# P9i Capabilities

## Available Agents
- **full_cycle**: Complete development pipeline (idea → impl → test → docs)
- **architect**: System design, ADRs, architecture decisions
- **developer**: Code generation, features, bug fixes
- **reviewer**: Code review, security, quality checks
- **designer**: UI/UX design and generation
- **devops**: CI/CD, deployment, infrastructure
- **migration**: Migration planning and execution

## Features
- Natural language interface
- Multi-agent orchestration
- Plugin packs (k8s, ci-cd, pinescript)
- Project memory management
- JWT authentication
- Rate limiting

## Usage
- "p9i создай функцию" - Generate code
- "p9i реализуй систему авторизации" - Full cycle implementation
- "p9i спроектируй архитектуру" - Design architecture
- "p9i проверь код" - Code review
            """,
            "processor": "NLQueryProcessor"
        }

    def _handle_version(self) -> dict:
        return {
            "status": "success",
            "output": "P9i v1.0.0 - Intelligent AI Assistant with Multi-Agent Orchestration",
            "processor": "NLQueryProcessor"
        }

    def _handle_help(self) -> dict:
        return {
            "status": "success",
            "output": """# p9i Commands

## Natural Language
- "создай функцию" - Generate code
- "добавь кнопку" - UI component
- "deploy k8s" - Deployment
- "сделай сайт" - Full website

## Commands
- /help - Show this help
- /prompt list - List prompts
- /status - System status
- init p9i - Initialize project

## Keywords
- реализуй, добавь, создай → developer
- проверь, ревью, аудит → reviewer
- дизайн, ui, кнопка → designer
- deploy, ci, cd, k8s → devops
            """,
            "processor": "NLQueryProcessor"
        }

    def _handle_status(self) -> dict:
        return {
            "status": "success",
            "output": "System status: OK. MCP server running. Use /prompt list to see available prompts.",
            "processor": "NLQueryProcessor"
        }

    def _handle_agents(self) -> dict:
        return {
            "status": "success",
            "output": """# Available Agents

- **full_cycle**: Complete development pipeline
- **architect**: System design
- **developer**: Code generation
- **reviewer**: Code review
- **designer**: UI/UX design
- **devops**: CI/CD
- **migration**: Migration
            """,
            "processor": "NLQueryProcessor"
        }


class SystemProcessor(Processor):
    """Обработка system команд."""

    def can_handle(self, intent: Intent) -> bool:
        return intent.type == IntentType.SYSTEM

    async def process(self, intent: Intent, request: str, context: dict) -> dict:
        if "init p9i" in request.lower() or "инициализация p9i" in request.lower():
            return await self._handle_system_init(context)
        elif "адаптируй" in request.lower() or "adapt" in request.lower():
            return await self._handle_adapt_project(context)
        elif "подключи" in request.lower():
            return await self._handle_adapt_project(context)

        return {"status": "error", "error": "Unknown system command"}

    async def _handle_system_init(self, context: dict) -> dict:
        """Handle p9i system initialization - detect project stack."""
        try:
            import os
            from pathlib import Path

            # Use context project_path or default to current directory
            project_path = context.get("project_path") if context else None
            if not project_path:
                project_path = "."

            path = Path(project_path) if project_path else None

            # Mount mapping for Docker patterns
            if path and not path.exists():
                mount_mappings = [
                    ("/home/", "/project/"),
                    ("/workspace/", "/project/"),
                    ("/app/", "/project/"),
                ]
                path_str = str(path)
                for host_prefix, container_prefix in mount_mappings:
                    if path_str.startswith(host_prefix):
                        remaining = path_str[len(host_prefix):]
                        project_name = remaining.split('/')[-1] if remaining else ""
                        new_path = f"/project/{project_name}"
                        mapped = Path(new_path)
                        if mapped.exists():
                            path = mapped
                            break
                # Scattered mount pattern
                if path and not path.exists():
                    app_path = Path("/app")
                    if app_path.exists() and ((app_path / "src").exists() or (app_path / "prompts").exists()):
                        path = app_path

            # Detect stack
            language, framework, database = "Unknown", "not detected", "not detected"

            if path and path.exists():
                # Language detection
                if (path / "requirements.txt").exists() or (path / "pyproject.toml").exists():
                    language = "Python"
                elif (path / "package.json").exists():
                    language = "JavaScript/TypeScript"
                elif (path / "go.mod").exists():
                    language = "Go"
                elif (path / "Cargo.toml").exists():
                    language = "Rust"

                # Framework detection from requirements.txt
                req_file = path / "requirements.txt"
                if req_file.exists():
                    content = req_file.read_text().lower()
                    if "fastapi" in content:
                        framework = "FastAPI"
                    elif "flask" in content:
                        framework = "Flask"
                    elif "django" in content:
                        framework = "Django"

                # Framework detection from pyproject.toml
                pyproject_file = path / "pyproject.toml"
                if pyproject_file.exists():
                    try:
                        import tomli
                        pyproject_content = tomli.loads(pyproject_file.read_text())
                        deps = []
                        deps.extend(pyproject_content.get("project", {}).get("dependencies", []))
                        deps.extend(pyproject_content.get("project", {}).get("optional-dependencies", {}).get("dev", []))
                        deps_str = " ".join(deps).lower()
                        if "fastapi" in deps_str:
                            framework = "FastAPI"
                        elif "flask" in deps_str:
                            framework = "Flask"
                        elif "django" in deps_str:
                            framework = "Django"
                        elif "streamlit" in deps_str:
                            framework = "Streamlit"
                    except ImportError:
                        # Fallback: read as text
                        content = pyproject_file.read_text().lower()
                        if "fastapi" in content:
                            framework = "FastAPI"
                        elif "flask" in content:
                            framework = "Flask"
                        elif "django" in content:
                            framework = "Django"

                pkg_file = path / "package.json"
                if pkg_file.exists():
                    try:
                        import json
                        pkg = json.loads(pkg_file.read_text())
                        deps = list(pkg.get("dependencies", {}).keys())
                        if "next" in deps:
                            framework = "Next.js"
                        elif "react" in deps:
                            framework = "React"
                        elif "vue" in deps:
                            framework = "Vue.js"
                    except (json.JSONDecodeError, OSError, KeyError):
                        pass  # Framework detection is best-effort

                # Database detection
                db_detected = False
                for db_file in ["*sqlite*.py", "*postgres*", "*mysql*"]:
                    if list(path.glob(f"**/{db_file}")):
                        database = "Detected"
                        db_detected = True
                        break
                # Also check docker-compose.yml for database services
                if not db_detected and (path / "docker-compose.yml").exists():
                    content = (path / "docker-compose.yml").read_text()
                    if "postgres" in content.lower():
                        database = "PostgreSQL"
                    elif "mysql" in content.lower():
                        database = "MySQL"
                    elif "mariadb" in content.lower():
                        database = "MariaDB"
                    elif "mongodb" in content.lower():
                        database = "MongoDB"
                    elif "redis" in content.lower() and "postgres" not in content.lower():
                        database = "Redis"

            resolved = f"- Path resolved to: {path}" if path and path != Path(project_path) else None
            lines = [
                "# p9i System Initialized",
                "",
                f"**Project**: `{project_path}`",
                resolved if resolved else "",
                "",
                "**Detected Stack**:",
                f"- Language: {language}",
                f"- Framework: {framework}",
                f"- Database: {database}",
                "",
                "**Status**: Ready for development",
                "",
                "**Available Commands**:",
                '- "создай функцию" → developer agent',
                '- "спроектируй архитектуру" → architect agent',
                '- "проверь код" → reviewer agent',
                '- "дизайн" → designer agent',
            ]
            output = "\n".join(lines)

            return {
                "status": "success",
                "output": output.strip(),
                "language": language,
                "framework": framework,
                "database": database,
                "project_path": str(path) if path else project_path,
                "processor": "SystemProcessor"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "processor": "SystemProcessor"
            }

    async def _handle_adapt_project(self, context: dict) -> dict:
        """Handle project adaptation - detect and configure for project."""
        try:
            from pathlib import Path
            import os
            import json

            project_path = context.get("project_path") if context else None
            if not project_path:
                project_path = "."

            path = Path(project_path) if project_path else None

            # Mount mapping for Docker patterns
            if path and not path.exists():
                mount_mappings = [
                    ("/home/", "/project/"),
                    ("/workspace/", "/project/"),
                    ("/app/", "/project/"),
                ]
                path_str = str(path)
                for host_prefix, container_prefix in mount_mappings:
                    if path_str.startswith(host_prefix):
                        remaining = path_str[len(host_prefix):]
                        project_name = remaining.split('/')[-1] if remaining else ""
                        new_path = f"/project/{project_name}"
                        mapped = Path(new_path)
                        if mapped.exists():
                            path = mapped
                            break
                if path and not path.exists():
                    app_path = Path("/app")
                    if app_path.exists() and ((app_path / "src").exists() or (app_path / "prompts").exists()):
                        path = app_path

            language, framework, database = "Unknown", "not detected", "not detected"

            if path and path.exists():
                if (path / "requirements.txt").exists() or (path / "pyproject.toml").exists():
                    language = "Python"
                elif (path / "package.json").exists():
                    language = "JavaScript/TypeScript"
                elif (path / "go.mod").exists():
                    language = "Go"
                elif (path / "Cargo.toml").exists():
                    language = "Rust"

                if (path / "requirements.txt").exists():
                    content = (path / "requirements.txt").read_text().lower()
                    if "fastapi" in content:
                        framework = "FastAPI"
                    elif "flask" in content:
                        framework = "Flask"
                    elif "django" in content:
                        framework = "Django"

                # Framework detection from pyproject.toml
                if (path / "pyproject.toml").exists():
                    content = (path / "pyproject.toml").read_text().lower()
                    if "fastapi" in content:
                        framework = "FastAPI"
                    elif "flask" in content:
                        framework = "Flask"
                    elif "django" in content:
                        framework = "Django"
                    elif "streamlit" in content:
                        framework = "Streamlit"

                if (path / "package.json").exists():
                    try:
                        pkg = json.loads((path / "package.json").read_text())
                        deps = list(pkg.get("dependencies", {}).keys())
                        if "next" in deps:
                            framework = "Next.js"
                        elif "react" in deps:
                            framework = "React"
                        elif "vue" in deps:
                            framework = "Vue.js"
                    except (json.JSONDecodeError, OSError, KeyError):
                        pass  # Framework detection is best-effort

                # Database detection
                db_detected = False
                for db_file in ["*sqlite*.py", "*postgres*", "*mysql*"]:
                    if list(path.glob(f"**/{db_file}")):
                        database = "Detected"
                        db_detected = True
                        break
                # Also check docker-compose.yml for database services
                if not db_detected and (path / "docker-compose.yml").exists():
                    content = (path / "docker-compose.yml").read_text()
                    if "postgres" in content.lower():
                        database = "PostgreSQL"
                    elif "mysql" in content.lower():
                        database = "MySQL"
                    elif "mariadb" in content.lower():
                        database = "MariaDB"
                    elif "mongodb" in content.lower():
                        database = "MongoDB"
                    elif "redis" in content.lower() and "postgres" not in content.lower():
                        database = "Redis"

            resolved = f"- Path resolved to: {path}" if path and path != Path(project_path) else None
            lines = [
                "# p9i Project Adapted",
                "",
                f"**Project**: `{project_path}`",
                resolved if resolved else "",
                "",
                "**Detected Stack**:",
                f"- Language: {language}",
                f"- Framework: {framework}",
                f"- Database: {database}",
                "",
                "**Ready**: p9i is now configured for this project",
            ]
            output = "\n".join(lines)

            return {
                "status": "success",
                "output": output.strip(),
                "language": language,
                "framework": framework,
                "database": database,
                "project_path": str(path) if path else project_path,
                "processor": "SystemProcessor"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "processor": "SystemProcessor"
            }
