# p9i — AI Prompt System

> **p9i** (p=prompt, 9=#, i=index) — MCP-сервис для управления AI-промтами с полным циклом: от идеи до production-реализации.

| Команда | Описание |
|---------|----------|
| `use p9i` | Универсальный триггер на естественном языке |
| `init p9i` | Инициализация в новом проекте |

---

## Быстрый старт

```bash
# Запуск (Docker)
docker compose up -d

# Или локально
pip install -e . && python -m src.api.server
```

### Быстрые команды

```bash
# HTTP API
curl -X POST http://localhost:8000/sse -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"ai_prompts","arguments":{"request":"добавь функцию"}},"id":1}'

# Claude Code
"Добавь функцию логирования. use p9i"
```

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
| **MiniMax** | MINIMAX_API_KEY | MiniMax-M2.7 | ✅ Default |
| Z.ai | ZAI_API_KEY | GLM-4.7 | ⚠️ Rate Limited |
| OpenRouter | OPENROUTER_API_KEY | claude-3-haiku | ✅ Free |

---

## MCP Tools (14)

| Инструмент | Назначение |
|------------|------------|
| `ai_prompts` | Универсальный маршрутизатор (`use p9i`) |
| `run_prompt` / `run_prompt_chain` | Выполнение промтов |
| `list_prompts` | Список 40 промтов |
| `get/save_project_memory` | Память проекта |
| `adapt_to_project` | Автоопределение стека |
| `context7_lookup/query` | Документация (Context7) |
| `generate/validate/revoke_jwt_token` | JWT аутентификация |
| `get_available_mcp_tools` | Список инструментов |

---

## Естественный язык: `use p9i`

Универсальный триггер работает на русском и английском:

```
"Добавь функцию авторизации. use p9i"
"Найди баги в обработке ошибок. use p9i"
"Создай API эндпоинт. use p9i"
"Рефакторинг функции. use p9i"
"init p9i" → адаптация к проекту
```

**Маршрутизация по ключевым словам:**

| Ключевое слово | Промт | Назначение |
|----------------|-------|------------|
| `добавить`, `new feature` | promt-feature-add | Новая функциональность |
| `баг`, `исправить`, `fix` | promt-bug-fix | Исправление багов |
| `рефакторинг`, `refactor` | promt-refactoring | Рефакторинг |
| `test`, `тест` | promt-quality-test | Тестирование |
| `security`, `безопасност` | promt-security-audit | Аудит безопасности |
| `init p9i`, `адаптируй` | promt-system-adapt | Адаптация к проекту |

---

## Архитектура промтов

**Tiered структура** (приоритет загрузки):

```
prompts/
├── core/                  # Baseline (SHA256, 1.0.0 lock)
├── universal/             # 40 промтов
│   ├── ai_agent_prompts/  # Agent промты
│   └── mpv_stages/        # MVP Stage (7 штук)
└── packs/                 # Plugin Packs (k8s, ci-cd)
```

### Baseline Verification

```bash
curl http://localhost:8000/verify-baseline
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
claude mcp add p9i -- docker run --rm -i \
  -v $PWD/.env:/app/.env \
  -v $PWD:/project \
  -v $PWD/memory:/app/memory \
  p9i-mcp-server:latest
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
    "p9i": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-v", "$PWD/.env:/app/.env",
        "-v", "$PWD:/project",
        "-v", "$PWD/memory:/app/memory",
        "p9i-mcp-server:latest"
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
p9i: ✓ Connected
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
p9i/
├── src/api/server.py       # FastMCP (14 tools)
├── src/services/          # executor, llm_client, memory
├── prompts/               # 40 markdown промтов
├── memory/                # Память проектов
├── docker/                # Dockerfile, docker-compose
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

| Category | Папка |
|----------|-------|
| How-to | `docs/how-to/` |
| Reference | `docs/reference/` (AUTO) |
| Explanation | `docs/explanation/adr/` |

---

## Ссылки

- [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTUREURE.md) — Архитектура
- [MCP_INTEGRATION.md](MCP_INTEGRATION.md) — Claude Code
- [GitHub](https://github.com/perovskikh/p9i)

**MIT License**
