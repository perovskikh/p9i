# AI Prompt System

**MCP-сервис для управления AI-промтами с полным циклом: от идеи до production-реализации.**

## Возможности

- ✅ **Prompt Factory** — генерация промтов из любой идеи через 7-этапную цепочку
- ✅ **Self-Verification** — автоматическая проверка качества промтов
- ✅ **Версионирование** — PostgreSQL для хранения версий и rollback
- ✅ **Multi-tenant изоляция** — API Keys для разделения проектов
- ✅ **Git Submodule** — подключение к проектам через субмодуль
- ✅ **MCP Server** — FastMCP (70% MCP серверов используют)
- ✅ **Гибридное хранилище** — Redis (hot) + PostgreSQL (persistent)

## Technology Stack

| Компонент | Выбор |
|-----------|-------|
| API Server | FastMCP |
| Database | PostgreSQL 14+ |
| Cache/Events | Redis 7+ |
| Validation | Pydantic v2+ |
| Python | 3.11+ |

## Быстрый старт

```bash
# Клонировать репозиторий
git clone https://github.com/perovskikh/ai-prompt-system.git
cd ai-prompt-system

# Запустить с Docker Compose
docker-compose up -d

# Или локально
pip install -e .
python -m src.api.server
```

## MCP Tools

После запуска доступны инструменты:

- `run_prompt` — выполнить один промт
- `run_prompt_chain` — выполнить цепочку (ideation → finish)
- `list_prompts` — список доступных промтов
- `get_project_memory` — получить память проекта
- `save_project_memory` — сохранить память проекта
- `adapt_to_project` — автоопределение стека проекта
- `clean_context` — очистка контекста при превышении лимита токенов

## Структура проекта

```
ai-prompt-system/
├── src/
│   ├── api/
│   │   └── server.py         # FastMCP сервер
│   ├── storage/
│   │   ├── database.py       # PostgreSQL + Redis
│   │   └── prompts.py        # Управление промтами
│   └── services/
│       ├── executor.py       # Выполнение промтов
│       └── memory.py        # Управление памятью
├── prompts/                  # Markdown промты (копируются из ai-agent-prompts)
├── config/                   # Конфигурация
├── docker/                   # Dockerfile
├── docker-compose.yml        # Full stack (PostgreSQL + Redis + Server)
└── tests/                    # Тесты
```

## Разработка

```bash
# Установка зависимостей
pip install -e ".[dev]"

# Запуск тестов
pytest

# Линтинг
black src/
ruff check src/
```

## Документация

Полная документация: [AI Prompt System Master](docs/how-to/ai-prompt-system-master.md)

## Лицензия

MIT License