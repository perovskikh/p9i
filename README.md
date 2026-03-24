# p9i — AI Prompt System

> **p9i** (p=prompt, 9=#, i=index) — MCP-сервис для управления AI-промтами с полным циклом: от идеи до production-реализации.

<p align="center">

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastMCP](https://img.shields.io/badge/FastMCP-3.1+-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Multi-Agent](https://img.shields.io/badge/Agents-7-orange.svg)](#multi-agent-orchestrator)

</p>

## Features

| Feature | Description |
|---------|-------------|
| **Prompt Factory** | Генерация промтов из любой идеи через 7-этапную цепочку |
| **Self-Verification** | Автоматическая проверка качества промтов |
| **Versioning** | PostgreSQL для хранения версий и rollback |
| **Baseline Verification** | SHA256 контроль целостности промтов |
| **JWT Auth** | Токены с refresh mechanism + Redis persistence |
| **Tier-based RBAC** | Роли: admin, developer, user, guest |
| **Multi-Agent Orchestrator** | 7 AI агентов с интеллектуальной маршрутизацией |
| **Browser Integration** | Playwright для автоматизации браузера |
| **Deduplication Guard** | Защита от дублирования промтов и ключевых слов |
| **Web Dashboard** | Мониторинг и управление через браузер |

---

## Quick Start

### Шаг 1: Клонируй и настрой

```bash
cd /home/worker/p9i
cp .env.example .env
# Добавь API ключи в .env (MINIMAX_API_KEY, ZAI_API_KEY и т.д.)
```

### Шаг 2: Запусти сервер

```bash
# Docker (рекомендуется) — ЗАПУСКАЕТ ВСЕ СЕРВИСЫ
docker compose up -d

# Или только MCP сервер без PostgreSQL/Redis (для тестов)
pip install -e .
MCP_TRANSPORT=stdio python -m src.api.server
```

### Шаг 3: Проверь статус

```bash
# Должно показать работающие сервисы
docker compose ps
```

**После запуска:**
- MCP SSE: `http://localhost:8000`
- Web UI: `http://localhost:8501` (Streamlit)

**Использование:**
```bash
# Claude Code - адаптация к проекту (ПРАВИЛЬНО!)
"init p9i"
"адаптируй к проекту"
"новый проект"

# Claude Code - основные команды
"Добавь функцию авторизации. use p9i"
"Исправь баг в коде. use p9i"

# HTTP API
curl -X POST http://localhost:8000/sse \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"ai_prompts","arguments":{"request":"добавь функцию"}},"id":1}'
```

### Подключение нового проекта

Для адаптации p9i к новому проекту используй команды:

| Команда | Описание |
|---------|----------|
| `init p9i` | Адаптация к проекту (English) |
| `адаптируй` | Адаптация к проекту (Русский) |
| `новый проект` | Инициализация нового проекта |
| `new project` | Инициализация нового проекта (English) |

> **Важно:** Порядок слов имеет значение! Используй `init p9i`, а не `p9i init`.

---

## Architecture

| Feature | Description |
|---------|-------------|
| **Prompt Factory** | Генерация промтов из любой идеи через 7-этапную цепочку |
| **Self-Verification** | Автоматическая проверка качества промтов |
| **Versioning** | PostgreSQL для хранения версий и rollback |
| **Baseline Verification** | SHA256 контроль целостности промтов |
| **JWT Auth** | Токены с refresh mechanism + Redis persistence |
| **Tier-based RBAC** | Роли: admin, developer, user, guest |
| **Multi-Agent Orchestrator** | 7 AI агентов с интеллектуальной маршрутизацией |
| **Browser Integration** | Playwright для автоматизации браузера |
| **Deduplication Guard** | Защита от дублирования промтов и ключевых слов |

```
p9i/
├── src/
│   ├── api/
│   │   ├── server.py          # FastMCP (20+ tools)
│   │   └── webui.py           # Web Dashboard
│   ├── application/           # Use cases, Agent routing
│   ├── domain/                # Entities, Business rules
│   ├── infrastructure/        # LLM adapters, External services
│   ├── services/              # Business logic
│   ├── storage/               # Data access layer
│   └── middleware/            # JWT, RBAC
├── prompts/                   # 40+ markdown промтов
│   ├── core/                  # Baseline (SHA256 locked)
│   ├── universal/             # 38 agent prompts
│   └── packs/                 # Plugin packs (k8s, ci-cd, pinescript-v6, uiux-pack)
└── memory/                    # Project memory
```

---

## Web Dashboard

Web UI доступен по адресу `http://localhost:8080` при запуске в SSE режиме.

### Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Main dashboard |
| `/health` | Health check |
| `/status` | System status |
| `/api/stats` | Real-time CPU/Memory/Requests |
| `/api/prompts` | List prompts |
| `/api/tools` | List MCP tools |
| `/api/memory` | Project memory |
| `/api/logs` | Server logs |

### Claude Code Integration

#### Option 1: Docker (stdio) — для локальной разработки p9i
```json
{
  "mcpServers": {
    "p9i": {
      "command": "docker",
      "args": ["run", "--rm", "-i",
        "-v", "$PWD/.env:/app/.env",
        "-v", "$PWD:/project",
        "-v", "$PWD/memory:/app/memory",
        "p9i"
      ]
    }
  }
}
```

#### Option 2: HTTP (SSE) — подключение из любого проекта

Запуск сервера:
```bash
MCP_TRANSPORT=sse python -m src.api.server
# или
docker run --rm -d -p 8000:8000 -p 8080:8080 -v ~/p9i/.env:/app/.env p9i:latest
```

Подключение в Claude Code:
```json
{
  "mcpServers": {
    "p9i": {
      "type": "http",
      "url": "http://localhost:8000"
    }
  }
}
```

**Преимущества:**
- Один экземпляр p9i для всех проектов
- Не нужно создавать `.env` в каждом проекте
- Централизованная память и состояние

---

## Устранение проблем

### Ошибка: "MCP server failed" / HTTP 404

Если в Claude Code видишь ошибку:
```
Status: ✘ failed
Error: HTTP 404: Not Found
```

**Причина:** p9i MCP сервер не запущен на `http://localhost:8000`

**Решение:**

```bash
# Вариант 1: Docker (рекомендуется)
cd /home/worker/p9i
docker compose up -d

# Вариант 2: Локальный запуск
pip install -e .
MCP_TRANSPORT=sse python -m src.api.server
```

После запуска в Claude Code выбери **"Reconnect"** в меню `/mcp`.

### Ошибка: "init p9i" не распознаётся

**Причина:** `init p9i` — это не команда shell, а **запрос к MCP серверу**.

**Решение:** После подключения MCP сервера просто напиши:
```
"init p9i"
```
в чате Claude Code. p9i автоматически определит запрос через INTENTS_MAP.

### Ошибка: Auth: not authenticated

**Причина:** Требуется JWT токен или API ключ.

**Решение:** Смотри раздел "Аутентификация" ниже.

### Ошибка: "Your input 'init p9i' is incomplete"

```
❯ init p9i
● Your input "init p9i" is incomplete. Could you clarify what you'd like to do?
```

**Причина:** MCP сервер не подключён! Claude Code не видит p9i как MCP провайдера.

**Решение:**

1. **Запусти p9i сервер:**
   ```bash
   cd /home/worker/p9i
   docker compose up -d
   ```

2. **Проверь что сервер запущен:**
   ```bash
   docker compose ps
   # Должен показать: mcp-server, db, redis - Status: running
   ```

3. **Переподключи MCP в Claude Code:**
   - Нажми `/mcp`
   - Выбери **"Reconnect"**

4. **После переподключения** команда `"init p9i"` будет работать!

### Проверка работы сервера

```bash
# Тест HTTP endpoint
curl http://localhost:8000/health

# Тест MCP tools
curl -X POST http://localhost:8000/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

---

## Аутентификация

p9i поддерживает JWT токены и API ключи для авторизации.

### Настройка через .env

```bash
# .env
JWT_SECRET=your-super-secret-key
JWT_ENABLED=true

# API ключ (альтернатива JWT)
P9I_API_KEY=sk-p9i-your-key
```

### Получение токена

```bash
# Сгенерировать JWT токен
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'
```

### Использование токена

```python
# В Claude Code settings.json
{
  "mcpServers": {
    "p9i": {
      "type": "http",
      "url": "http://localhost:8000",
      "headers": {
        "Authorization": "Bearer YOUR_JWT_TOKEN"
      }
    }
  }
}
```

### Без аутентификации (для разработки)

```bash
# Отключить JWT в .env
JWT_ENABLED=false
```

---

## MCP Tools

### Core
| Tool | Purpose |
|------|---------|
| `ai_prompts` | Universal router (`use p9i`) |
| `run_prompt` / `run_prompt_chain` | Execute prompts |
| `list_prompts` | List available prompts |

### Pipeline (ADR-004)
| Tool | Purpose |
|------|---------|
| `run_interview` | AI interview for requirements |
| `decompose_prompt` | Complex task decomposition |
| `generate_spec` | Generate specification |
| `checkpoint_save/load` | Session checkpoints |

### UI/UX Generation (ADR-005)
| Tool | Framework | Purpose |
|------|-----------|---------|
| `generate_tailwind` | TailwindCSS | Web components |
| `generate_shadcn` | shadcn/ui | React components |
| `generate_textual` | Textual | TUI interfaces |
| `generate_tauri` | Tauri | Desktop apps |

### Multi-Agent Orchestrator (ADR-007)
| Tool | Purpose |
|------|---------|
| `p9i_siri` | Central voice router |
| `architect_design` | Architecture design |
| `developer_code` | Code generation |
| `reviewer_check` | Code review |
| `list_agents` | List available agents |

---

## Multi-Agent Routing

p9i автоматически маршрутизирует голосовые команды (Siri):

| Command | Keywords | Route |
|---------|----------|-------|
| **реализуй** | реализуй, внедри, сделай, e2e | full_cycle → research→impl→test→docs |
| **UI/UX** | дизайн, ui, кнопка, component | designer → developer → reviewer |
| **Deploy** | deploy, ci, cd, docker | developer → reviewer → devops |
| **Complex** | архитектура, спроектируй | architect → developer → reviewer |

**Available Agents:**
- **Architect** — проектирование, ADRs
- **Developer** — код, фичи, баги
- **Reviewer** — ревью, безопасность, тесты
- **Designer** — UI/UX (Tailwind, shadcn)
- **DevOps** — CI/CD, Docker, Kubernetes

---

## LLM Providers

Full configuration via `.env` (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `auto` | Explicit: `minimax`, `glm-4-7`, `deepseek`, etc. |
| `LLM_PROVIDER_PRIORITY` | `minimax,glm-4-7,hunter,deepseek,anthropic` | Auto-detection order |
| `LLM_FAILOVER_ORDER` | `minimax,glm-4-7,hunter,deepseek,anthropic` | Fallback chain on errors |
| `{PROVIDER}_ENABLED` | `true` | Feature flags per provider |
| `{PROVIDER}_MODEL` | provider default | Custom model |
| `{PROVIDER}_TEMPERATURE` | `0.7` | Sampling temperature |
| `{PROVIDER}_MAX_TOKENS` | `4096` | Max tokens |

**Provider Priority (auto-detection):**
```
LLM_PROVIDER=auto → LLM_PROVIDER_PRIORITY → First available API_KEY
```

**Fallback Chain (on errors):**
```
LLM_FAILOVER_ENABLED=true → Try next provider in LLM_FAILOVER_ORDER
```

---

## Prompt Structure

```
prompts/
├── core/                  # Baseline (SHA256, version 1.0.0 locked)
├── universal/             # 38 prompts
│   ├── ai_agent_prompts/  # Agent prompts
│   └── mpv_stages/        # MVP Stage (7 stages)
└── packs/                 # Plugin Packs (k8s, ci-cd, pinescript-v6, uiux-pack)
```

## Plugin Packs

| Pack | Description | Triggers |
|------|-------------|----------|
| k8s-pack | Kubernetes operations | deploy, k8s, pod, helm |
| ci-cd-pack | CI/CD pipelines | github, actions, ci, cd |
| pinescript-v6 | Pine Script v6 for TradingView | pinescript, tradingview, стратегия, индикатор |
| uiux-pack | UI/UX Design System | tailwind, shadcn, colors, typography, design system |

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your API keys
```

All configuration via `.env` (see `.env.example` for full list):

```bash
# Primary Provider
LLM_PROVIDER=auto
LLM_PROVIDER_PRIORITY=minimax,glm-4-7,hunter,deepseek,anthropic

# API Keys
MINIMAX_API_KEY=sk-xxx
ZAI_API_KEY=xxx
OPENROUTER_API_KEY=sk-or-xxx
DEEPSEEK_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=p9i

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# JWT
JWT_SECRET=your-secret
JWT_ENABLED=true
```

See [docs/reference/env-variables.md](docs/reference/env-variables.md) for full documentation.

---

## Docker

```bash
# Build
docker build -f docker/Dockerfile -t p9i .

# Run with volume mounts (stdio mode for Claude Code)
docker run --rm -i \
  -v $PWD/.env:/app/.env \
  -v $PWD:/project \
  -v $PWD/memory:/app/memory \
  p9i

# Run with Web UI + MCP SSE (port 8000 + 8080)
docker run --rm -d -p 8000:8000 -p 8080:8080 \
  -v $PWD/.env:/app/.env \
  p9i

# Или через docker-compose
docker compose up -d
```

---

## Testing

```bash
# All tests
pytest

# Specific
pytest tests/test_storage.py

# With coverage
pytest --cov=src
```

---

## ADR Phases

| Phase | Status | Description |
|-------|--------|-------------|
| 1 | ✅ | Tiered directories, baseline lock |
| 2 | ✅ | PromptStorageV2, cascade priority |
| 3 | ✅ | 7 MPV stage prompts |
| 4 | ✅ | Plugin Packs (k8s, ci-cd) |
| 5 | ✅ | JWT Auth, RBAC, HTTPS Proxy |
| 6 | ✅ | Context7 MCP Integration |
| 7 | ✅ | Pipeline (interview, decompose) |
| 8 | ✅ | UI/UX Generation (Tailwind, shadcn) |
| 9 | ✅ | Multi-Agent Orchestrator (7 agents) |
| 10 | ✅ | Clean Architecture (P0-P3) |

---

## Documentation

| Type | Location |
|------|-----------|
| How-to | `docs/how-to/` |
| Reference | `docs/reference/` |
| ADR | `docs/explanation/adr/` |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with FastMCP, PostgreSQL, Redis, and AI agents.*