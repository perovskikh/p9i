# AI Prompt System

**MCP-сервис для управления AI-промтами с полным циклом: от идеи до production-реализации.**

---

## Статус системы

| Компонент | Статус | Порт |
|-----------|--------|------|
| MCP Server | ✅ Running | 8000 |
| PostgreSQL | ✅ Healthy | 5432 |
| Redis | ✅ Healthy | 6379 |

**Последнее тестирование:** 2026-03-16 — ВСЕ ТЕСТЫ ПРОЙДЕНЫ ✅

---

## Возможности

- ✅ **Prompt Factory** — генерация промтов из любой идеи через 7-этапную цепочку
- ✅ **Self-Verification** — автоматическая проверка качества промтов
- ✅ **Версионирование** — PostgreSQL для хранения версий и rollback
- ✅ **Multi-tenant изоляция** — API Keys для разделения проектов
- ✅ **Git Submodule** — подключение к проектам через субмодуль
- ✅ **MCP Server** — FastMCP (70% MCP серверов используют)
- ✅ **Гибридное хранилище** — Redis (hot) + PostgreSQL (persistent)
- ✅ **Audit Logging** — полное логирование всех операций

---

## Technology Stack

| Компонент | Выбор |
|-----------|-------|
| API Server | FastMCP 3.x |
| Database | PostgreSQL 14+ |
| Cache/Events | Redis 7+ |
| Validation | Pydantic v2+ |
| Python | 3.11+ |
| Transport | stdio (Claude Code) / SSE (HTTP) |

### LLM Провайдеры

Система автоматически выбирает провайдер:

| Провайдер | API Key | Модель | Статус |
|-----------|---------|--------|--------|
| **Z.ai** | ZAI_API_KEY | GLM-4.7 | ✅ Default |
| MiniMax | MINIMAX_API_KEY | MiniMax-M2.5 | ✅ |
| OpenRouter | OPENROUTER_API_KEY | hunter-alpha | ✅ Free |

---

## Быстрый старт

### Docker Compose (рекомендуется)

```bash
# Клонировать репозиторий
git clone https://github.com/perovskikh/ai-prompt-system.git
cd ai-prompt-system

# Запустить полный стек
docker compose up -d

# Проверить статус
docker compose ps
```

### Локальный запуск

```bash
# Установка зависимостей
pip install -e .

# Запуск сервера
python -m src.api.server
```

---

## MCP Tools (10 инструментов)

После запуска доступны инструменты:

| Инструмент | Описание |
|------------|----------|
| `ai_prompts` | Универсальный маршрутизатор (пиши на естественном языке) |
| `run_prompt` | Выполнить один промт |
| `run_prompt_chain` | Выполнить цепочку (ideation → finish) |
| `list_prompts` | Список доступных промтов (30 штук) |
| `get_project_memory` | Получить память проекта |
| `save_project_memory` | Сохранить память проекта |
| `adapt_to_project` | Автоопределение стека проекта |
| `clean_context` | Очистка контекста при превышении лимита токенов |
| `context7_lookup` | Получить Context7 library ID для документации |
| `get_available_mcp_tools` | Список доступных инструментов |

---

## Естественный язык: `use ai-prompts`

Главная фича — **универсальный триггер** `ai_prompts`:

```
"Добавь в README.md секцию с примерами. use ai-prompts"
"Найди и исправь баги в коде. use ai-prompts"
"Создай API эндпоинт для пользователей. use ai-prompts"
"Сделай рефакторинг функции авторизации. use ai-prompts"
```

**Как работает:**
1. Парсит намерение из запроса
2. Автоматически выбирает нужный промт из 30
3. Выполняет и возвращает результат

**Поддерживаемые намерения:**

| Ключевое слово | Промт |
|---------------|-------|
| `readme`, `документац` | promt-readme-sync |
| `feature`, `добавить`, `создать` | promt-feature-add |
| `bug`, `исправить`, `фикс` | promt-bug-fix |
| `refactor`, `рефакторинг` | promt-refactoring |
| `test`, `тест` | promt-quality-test |
| `security`, `безопасност` | promt-security-audit |
| `verify`, `проверит` | promt-verification |
| `adapt`, `адаптац` | promt-project-adaptation |
| `rules`, `правила` | promt-project-rules-sync |
| `ci-cd`, `pipeline` | promt-ci-cd-pipeline |
| `database`, `db` | promt-db-baseline-governance |
| `version`, `версион` | promt-versioning-policy |
| `adr`, `decision` | promt-adr-implementation-planner |
| `remove`, `удалить` | promt-feature-remove |
| `создай промт`, `new prompt` | promt-prompt-creator |

---

## Context7 Integration

Система интегрирована с **Context7 MCP** для получения актуальной документации.

### Быстрый пример

```python
# Получить Context7 ID для библиотеки
context7_lookup(library="fastapi", query="create API endpoint")
# => library_id: /tiangolo/fastapi
# => mcp call: mcp__context7__query_docs(library_id="/tiangolo/fastapi", query="create API endpoint")
```

### Поддерживаемые библиотеки

| Библиотека | Context7 ID |
|------------|-------------|
| FastAPI | /tiangolo/fastapi |
| Flask | /pallets/flask |
| React | /facebook/react |
| Next.js | /vercel/next.js |
| Supabase | /supabase/supabase |
| Prisma | /prisma/prisma |
| Pydantic | /pydantic/pydantic |
| Django | /django/django |

### Использование с Claude Code

```bash
# Оба MCP должны быть подключены
claude mcp add ai-prompt-system -- ...
claude mcp add context7 -- ...
```

### Промт для генерации с Context7

Новый промт `promt-context7-generation` автоматически:
1. Определяет библиотеку из запроса
2. Получает Context7 ID
3. Запрашивает документацию
4. Генерирует код по документации

---

## Тестирование

```bash
# Смонтировать .env и проект
docker run --rm -i \
  -v $PWD/.env:/app/.env \
  -v $PWD:/project \
  -v $PWD/memory:/app/memory \
  ai-prompt-system-mcp-server:latest python -c "
from src.api.server import list_prompts, run_prompt

# Тест 1: Список промтов
result = list_prompts()
print(f'Prompts: {result[\"count\"]}')

# Тест 2: Выполнение промта
result = run_prompt('promt-verification', {'project': 'test', 'action': 'list'})
print(f'Status: {result[\"status\"]}')
print(f'Model: {result[\"model\"]}')
"
```

---

## Интеграция с Claude Code

### Подключение (рекомендуется — локальный образ)

```bash
# Добавить MCP сервер с монтированием .env, проекта и памяти
claude mcp add ai-prompt-system -- docker run --rm -i \
  -v $PWD/.env:/app/.env \
  -v $PWD:/project \
  -v $PWD/memory:/app/memory \
  ai-prompt-system-mcp-server:latest
```

**Для чего нужно:**
- `$PWD/.env` — API ключи для LLM
- `$PWD:/project` — доступ к файлам проекта (для `adapt_to_project`)
- `$PWD/memory` — сохранение памяти проекта между сессиями

### Подключение (Docker Hub — после публикации)

```bash
claude mcp add ai-prompt-system -- docker run --rm -i perovskikh/ai-prompt-system
```

### Подключение через settings.json

Добавь в `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "ai-prompt-system": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-v", "$PWD/.env:/app/.env",
        "-v", "$PWD:/project",
        "-v", "$PWD/memory:/app/memory",
        "ai-prompt-system-mcp-server:latest"
      ]
    }
  }
}
```

**Важно:** нужен `.env` файл с API ключами.

### Проверка

```bash
claude mcp list
```

Должно показать:
```
ai-prompt-system: ✓ Connected
```

### Доступные инструменты

После подключения доступны 8 MCP инструментов:
- `run_prompt` — выполнить промт
- `run_prompt_chain` — выполнить цепочку
- `list_prompts` — список промтов
- `get_project_memory` / `save_project_memory` — память проекта
- `adapt_to_project` — автоопределение стека
- `clean_context` — очистка контекста
- `get_available_mcp_tools` — список инструментов

### Примеры использования

#### Определить стек проекта

```bash
# Нужно примонтировать проект для доступа к файлам
docker run --rm -i \
  -v $PWD/.env:/app/.env \
  -v $PWD:/project \
  ai-prompt-system-mcp-server:latest \
  python -c "from src.api.server import adapt_to_project; import json; print(json.dumps(adapt_to_project('/project'), indent=2))"
```

#### Выполнить промт

```bash
docker run --rm -i \
  -v $PWD/.env:/app/.env \
  ai-prompt-system-mcp-server:latest \
  python -c "from src.api.server import run_prompt; import asyncio; print(asyncio.run(run_prompt('promt-verification', {'project': 'test'})))"
```

#### Создать новый промт

```bash
docker run --rm -i \
  -v $PWD/.env:/app/.env \
  -v $PWD/prompts:/app/prompts \
  ai-prompt-system-mcp-server:latest \
  python -c "
from src.api.server import ai_prompts
import asyncio

result = asyncio.run(ai_prompts(
    request='Создай промт для автоматической генерации changelog из git commits',
    context={}
))
print(result.get('content', '')[:500])
"
```

**Или через `use ai-prompts`:**

```
"Создай промт для генерации changelog из git commits. use ai-prompts"
```

Подробнее: [MCP_INTEGRATION.md](MCP_INTEGRATION.md)

---

## Структура проекта

```
ai-prompt-system/
├── src/
│   └── api/
│       └── server.py         # FastMCP сервер (8 tools)
├── prompts/                  # Markdown промты (28 файлов)
│   └── README.md             # Гайд по использованию промтов
├── database/
│   └── schema.sql           # PostgreSQL схема (6 таблиц)
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml   # Full stack
├── MCP_INTEGRATION.md       # Настройка Claude Code
├── SYSTEM_ARCHITECTURE.md   # Полная схема системы
└── TEST_RESULTS.md          # Результаты тестирования
```

---

## Prompts (28 файлов)

| Категория | Количество |
|-----------|------------|
| Operations | verification, quality-test, sync-optimization |
| Design | mvp-baseline-generator, adr-impl-planner |
| Implementation | feature-add, bug-fix |
| Meta | system-evolution, versioning-policy |

Полный список: `list_prompts()` tool

---

## API Keys & Rate Limiting

Система поддерживает множественные API ключи с:

- **Rate limiting** — 60-секундное окно
- **Permissions** — разграничение доступа (read, write, admin)
- **Audit logging** — логирование всех запросов

Настройка через переменные окружения:
```
API_KEYS__SYSTEM=sk-system-dev
API_KEYS__PROJECT_1=sk-project-1-key
```

---

## Документация

| Файл | Описание |
|------|----------|
| [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) | Полная схема архитектуры |
| [MCP_INTEGRATION.md](MCP_INTEGRATION.md) | Подключение к Claude Code |
| [TEST_RESULTS.md](TEST_RESULTS.md) | Результаты тестирования |
| [prompts/README.md](prompts/README.md) | Гайд по промтам |

---

## Репозиторий

https://github.com/perovskikh/ai-prompt-system

---

## Лицензия

MIT License
