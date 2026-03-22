# AI Prompt System

**MCP-сервис для управления AI-промтами с полным циклом: от идеи до production-реализации.**

---

## Статус системы

| Компонент | Статус | Порт |
|-----------|--------|------|
| MCP Server | ✅ Running | 8000 |
| PostgreSQL | ✅ Healthy | 5432 |
| Redis | ✅ Healthy | 6379 |

**Последнее тестирование:** 2026-03-21 — MiniMax-M2.5 ✅

### ADR-002 Реализация

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Complete | Tiered directories, baseline lock |
| Phase 2 | ✅ Complete | TieredPromptLoader, cascade priority |
| Phase 3 | ✅ Complete | 7 MPV stage prompts |
| Phase 4 | ✅ Complete | Plugin Packs (k8s-pack, ci-cd-pack) |
| Phase 5 | ✅ Complete | JWT Auth, RBAC, HTTPS Proxy |
| Phase 6 | ✅ Complete | Context7 MCP Integration |

**Всего промтов:** 40 | **Universal:** 38 | **Core:** 1 | **MPV:** 7

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
- ✅ **Tiered Architecture** — CORE → UNIVERSAL → MPV_STAGES → PROJECTS
- ✅ **Baseline Verification** — SHA256 контроль целостности промтов
- ✅ **Cascade Priority** — приоритетная загрузка по tiers
- ✅ **Plugin Packs** — k8s-pack, ci-cd-pack с триггерами
- ✅ **JWT Authentication** — токены с refresh mechanism
- ✅ **Tier-based RBAC** — роли: admin, developer, user, guest
- ✅ **HTTPS Proxy** — Caddy с автоматическим HTTPS

---

## Technology Stack

| Компонент | Выбор |
|-----------|-------|
| API Server | FastMCP 3.1.1 |
| Database | PostgreSQL 14+ |
| Cache/Events | Redis 7+ |
| Validation | Pydantic v2+ |
| Python | 3.11+ |
| Transport | stdio (Claude Code) / SSE (HTTP) |

### LLM Провайдеры

Система автоматически выбирает провайдер:

| Провайдер | API Key | Модель | Статус |
|-----------|---------|--------|--------|
| **MiniMax** | MINIMAX_API_KEY | MiniMax-M2.5 | ✅ Default |
| Z.ai | ZAI_API_KEY | GLM-4.7 | ⚠️ Rate Limited |
| OpenRouter | OPENROUTER_API_KEY | claude-3-haiku | ✅ Free |

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

## MCP Tools (14 инструментов)

После запуска доступны инструменты:

| Инструмент | Описание |
|------------|----------|
| `ai_prompts` | Универсальный маршрутизатор (пиши на естественном языке) |
| `run_prompt` | Выполнить один промт |
| `run_prompt_chain` | Выполнить цепочку (ideation → finish) |
| `list_prompts` | Список доступных промтов (40 штук) |
| `get_project_memory` | Получить память проекта |
| `save_project_memory` | Сохранить память проекта |
| `adapt_to_project` | Автоопределение стека проекта |
| `clean_context` | Очистка контекста при превышении лимита токенов |
| `context7_lookup` | Получить Context7 library ID для документации |
| `context7_query` | Запросить документацию через Context7 MCP |
| `generate_jwt_token` | Сгенерировать JWT токен |
| `validate_jwt_token` | Валидировать JWT токен |
| `revoke_jwt_token` | Отозвать JWT токен |
| `get_available_mcp_tools` | Список доступных инструментов |

---

## Естественный язык: `use p9i`

Главная фича — **универсальный триггер** `ai_prompts`:

```
"Добавь в README.md секцию с примерами. use p9i"
"Найди и исправь баги в коде. use p9i"
"Создай API эндпоинт для пользователей. use p9i"
"Сделай рефакторинг функции авторизации. use p9i"
```

**Как работает:**
1. Парсит намерение из запроса
2. Автоматически выбирает нужный промт
3. Выполняет и возвращает результат

---

## Структура промтов

Система использует **tiered архитектуру**:

```
prompts/
├── core/                    # Baseline промты (SHA256 верификация)
│   ├── system-prompts/     # Базовые системные промты
│   └── registry.json       # Baseline lock: 1.0.0
├── universal/              # Универсальные промты
│   ├── ai_agent_prompts/   # Agent промты (38 штук)
│   ├── mpv_stages/         # MVP Stage промты (7 штук)
│   └── registry.json
├── packs/                   # Plugin Packs
│   ├── k8s-pack/           # Kubernetes операции
│   └── ci-cd-pack/        # CI/CD pipelines
└── registry.json           # Общий реестр (40 промтов)
```

### Baseline Verification

```bash
# Проверить целостность baseline
curl http://localhost:8001/verify-baseline
```

---

## Context7 Integration

Система интегрирована с **Context7 MCP** (`https://mcp.context7.com/mcp`) для получения актуальной документации.

### Быстрый пример

```python
# Получить Context7 ID для библиотеки
context7_lookup(library="fastapi", query="create API endpoint")
# => library_id: /fastapi/fastapi

# Запросить документацию напрямую
context7_query(library="fastapi", query="create API endpoint")
# => results: [документация с примерами кода]
```

### JWT Authentication

Система использует JWT токены для аутентификации:

```python
# Сгенерировать токен
generate_jwt_token(subject="user", role="developer", expiry_hours=24)

# Использовать с запросом
ai_prompts("добавь функцию", jwt_token="eyJ...")
```

---

## Подключение удалённых клиентов по HTTP

MCP сервер работает на порту 8000 (SSE transport) и доступен для любых HTTP клиентов.

### Быстрый старт для удалённого клиента

```bash
# Пример подключения через curl
curl -X POST http://YOUR_SERVER:8000/sse \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "ai_prompts",
      "arguments": {
        "request": "добавь функцию",
        "jwt_token": "YOUR_JWT_TOKEN"
      }
    },
    "id": 1
  }'
```

### Python клиент

```python
import httpx
import json

MCP_URL = "http://your-server:8000/sse"

def call_mcp(method: str, params: dict):
    response = httpx.post(
        MCP_URL,
        json={
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        },
        headers={"Content-Type": "application/json"}
    )
    return response.json()

# Пример вызова
result = call_mcp("tools/call", {
    "name": "ai_prompts",
    "arguments": {
        "request": "добавь функцию логирования",
        "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
})
print(result)
```

### JavaScript/Node.js клиент

```javascript
const MCP_URL = 'http://your-server:8000/sse';

async function callMcp(method, params) {
  const response = await fetch(MCP_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      method,
      params,
      id: 1
    })
  });
  return response.json();
}

// Вызов ai_prompts
const result = await callMcp('tools/call', {
  name: 'ai_prompts',
  arguments: {
    request: 'добавь функцию',
    jwt_token: 'YOUR_JWT_TOKEN'
  }
});
```

### Получение JWT токена

```python
# Сначала получить токен
token_result = call_mcp("tools/call", {
    "name": "generate_jwt_token",
    "arguments": {
        "subject": "user-name",
        "role": "developer",
        "expiry_hours": 24
    }
})
jwt_token = token_result['result']['content'][0]['text']['token']
```

### Доступные методы

| Метод | Описание |
|-------|----------|
| `tools/list` | Список доступных инструментов |
| `tools/call` | Вызов инструмента |
| `resources/list` | Список ресурсов |
| `resources/read` | Чтение ресурса |

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

---

## Тестирование

```bash
# Все тесты
pytest

# С конкретным файлом
pytest tests/test_storage.py

# С покрытием
pytest --cov=src
```

---

## Структура проекта

```
ai-prompt-system/
├── src/
│   ├── api/
│   │   └── server.py         # FastMCP сервер (14 tools)
│   ├── services/
│   │   ├── executor.py       # PromptExecutor
│   │   ├── llm_client.py     # LLM клиент (MultiMax, ZAI, OpenRouter)
│   │   └── memory.py         # MemoryService
│   ├── storage/
│   │   ├── prompts.py        # Legacy storage
│   │   └── prompts_v2.py    # Tiered storage с baseline
│   └── middleware/
│       └── baseline_verification.py
├── prompts/                   # Markdown промты
│   ├── core/                # Baseline промты
│   ├── universal/           # Универсальные промты
│   └── registry.json        # Реестр
├── memory/                   # Память проектов
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
└── README.md
```

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

## Документация (Diátaxis)

Система следует **Diátaxis** стандартам документации 2026:

| Category | Папка | Статус |
|----------|-------|--------|
| Tutorials | `docs/tutorials/` | Требует создания |
| How-to | `docs/how-to/` | ✅ 5 файлов |
| Reference | `docs/reference/` | AUTO-GENERATED |
| Explanation | `docs/explanation/` | ✅ 4 ADR |

### Структура docs/

```
docs/
├── tutorials/     # Обучение с нуля
├── how-to/        # Практические задачи
│   ├── BOTTLENECKS_ANALYSIS.md
│   ├── AUTO_FIX_IMPLEMENTATION.md
│   ├── TECHNICAL_DEBT_TRACKER.md
│   ├── MPV.md
│   └── analysis-CodeShift-promt.md
├── reference/     # API справка (AUTO-GENERATED)
└── explanation/
    └── adr/       # Architecture Decision Records
        ├── ADR-001-system-genesis.md
        ├── ADR-002-tiered-prompt-architecture-mpv-integration.md
        └── ADR-003-prompt-storage-strategy.md
```

---

## Документация

| Файл | Описание |
|------|----------|
| [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) | Полная схема архитектуры |
| [MCP_INTEGRATION.md](MCP_INTEGRATION.md) | Подключение к Claude Code |

---

## Репозиторий

https://github.com/perovskikh/ai-prompt-system

---

## Лицензия

MIT License
