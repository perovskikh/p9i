# p9i — AI Prompt System

> **p9i** (p=prompt, 9=#, i=index) — MCP-сервис для управления AI-промтами с полным циклом: от идеи до production-реализации.

<p align="center">

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastMCP](https://img.shields.io/badge/FastMCP-3.1+-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Multi-Agent](https://img.shields.io/badge/Agents-7-orange.svg)](#multi-agent-orchestrator)

</p>

## Quick Start

```bash
# Docker (recommended)
docker compose up -d

# Or local
pip install -e . && python -m src.api.server
```

**Usage:**
```bash
# Claude Code
"Добавь функцию авторизации. use p9i"

# HTTP API
curl -X POST http://localhost:8000/sse \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"ai_prompts","arguments":{"request":"добавь функцию"}},"id":1}'
```

---

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

---

## Architecture

```
p9i/
├── src/
│   ├── api/server.py           # FastMCP (20+ tools)
│   ├── application/            # Use cases, Agent routing
│   ├── domain/                # Entities, Business rules
│   ├── infrastructure/         # LLM adapters, External services
│   ├── services/              # Business logic
│   ├── storage/               # Data access layer
│   └── middleware/             # JWT, RBAC
├── prompts/                   # 40+ markdown промтов
│   ├── core/                  # Baseline (SHA256 locked)
│   ├── universal/             # 38 agent prompts
│   └── packs/                 # Plugin packs (k8s, ci-cd)
└── memory/                    # Project memory
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
└── packs/                 # Plugin Packs (k8s, ci-cd)
```

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

# Run with volume mounts
docker run --rm -i \
  -v $PWD/.env:/app/.env \
  -v $PWD:/project \
  -v $PWD/memory:/app/memory \
  p9i
```

### Claude Code Integration

```bash
# Add to ~/.claude/settings.json
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