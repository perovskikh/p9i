# p9i — AI Prompt System

> **p9i** (p=prompt, 9=#, i=index) — MCP-сервер для управления AI-промтами через полный жизненный цикл: от идеи до production-реализации.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastMCP](https://img.shields.io/badge/FastMCP-3.1+-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Multi-Agent](https://img.shields.io/badge/Agents-7-orange.svg)](#multi-agent-orchestrator)

## Возможности

| Возможность | Описание |
|-------------|----------|
| **Prompt Factory** | Генерация промтов через 7-этапную цепочку |
| **Self-Verification** | Автоматическая проверка качества промтов |
| **Versioning** | PostgreSQL для хранения версий и rollback |
| **JWT Auth** | Токены с refresh + Redis persistence |
| **RBAC** | Роли: admin, developer, user, guest |
| **Multi-Agent** | 7 AI агентов с интеллектуальной маршрутизацией |
| **Browser** | Playwright для автоматизации браузера |
| **Deduplication** | Защита от дублирования промтов |
| **UI Generation** | Tailwind, shadcn/ui, Tauri |

## Быстрый старт

```bash
# Клонируй репозиторий
git clone https://github.com/p9i/p9i.git
cd p9i

# Создай конфигурацию
cp .env.example .env
# Добавь API ключи в .env

# Docker (рекомендуется)
docker compose up -d

# K3s Production
make deploy
```

## Команды Makefile

```bash
make dev        # docker compose up (локальная разработка)
make deploy     # build-push + helm upgrade (K3s)
make watch      # kubectl logs -f
make status     # kubectl get all -n p9i
make scale REPLICAS=5
```

## Claude Code Integration

```json
{
  "mcpServers": {
    "p9i": {
      "command": "python3",
      "args": ["/path/to/p9i/p9i_stdio_bridge.py"],
      "env": {
        "MCP_PROXY_URL": "https://mcp.coderweb.ru/mcp",
        "P9I_API_KEY": "sk-p9i-codeshift-mcp.coderweb.ru"
      }
    }
  }
}
```

## MCP Инструменты

### Core
| Инструмент | Назначение |
|------------|------------|
| `p9i` | Unified router — естественноязыковый интерфейс |
| `run_prompt` | Выполнить промт |
| `run_prompt_chain` | Выполнить цепочку промтов |
| `list_prompts` | Список доступных промтов |
| `get_prompt` | Получить промт по имени |

### Проекты
| Инструмент | Назначение |
|------------|------------|
| `create_project` | Создать проект |
| `get_project` | Получить проект |
| `list_projects` | Список проектов |
| `adapt_to_project` | Адаптировать к стеку проекта |

### Память
| Инструмент | Назначение |
|------------|------------|
| `get_project_memory` | Получить память проекта |
| `save_project_memory` | Сохранить память проекта |

### Аутентификация
| Инструмент | Назначение |
|------------|------------|
| `generate_jwt_token` | Сгенерировать JWT токен |
| `validate_jwt_token` | Проверить JWT токен |
| `revoke_jwt_token` | Отозвать JWT токен |

### API Keys
| Инструмент | Назначение |
|------------|------------|
| `create_api_key` | Создать API ключ |
| `list_api_keys` | Список API ключей |
| `revoke_api_key` | Отозвать API ключ |

### UI/UX
| Инструмент | Фреймворк |
|------------|-----------|
| `generate_tailwind` | TailwindCSS |
| `generate_shadcn` | shadcn/ui |
| `generate_textual` | Textual |
| `generate_tauri` | Tauri |

## Архитектура

```
src/
├── api/server.py          # FastMCP сервер (20+ tools)
├── agents/                # WebSocket клиент
├── application/           # Use cases, routing
│   └── p9i_router.py     # Unified router
├── domain/                # Entities, Business rules
├── infrastructure/         # LLM adapters
├── services/              # Business logic
│   ├── executor.py        # Prompt execution
│   ├── llm_client.py      # Multi-provider LLM
│   └── orchestrator.py    # Multi-agent orchestration
├── storage/               # Data access
└── middleware/            # JWT, RBAC
```

### Multi-Agent Оркестрация

| Agent | Назначение | Keywords |
|-------|-----------|----------|
| `p9i` | Unified router | Все запросы |
| `architect` | Архитектура | архитектура, спроектируй |
| `developer` | Код | создай, добавь, напиши |
| `reviewer` | Ревью | проверь, приведи |
| `designer` | UI/UX | дизайн, кнопка |
| `devops` | CI/CD | deploy, k8s, ci-cd |
| `explorer` | Анализ кода | как работает, explore |

### LLM Провайдеры

```
minimax → glm-4-7 → hunter → deepseek → anthropic
```

Автоматический failover при ошибках (401, 403, 429, 500+).

### Prompt Tiers

1. `core/` — Baseline (SHA256 locked)
2. `universal/` — Universal prompts
3. `packs/` — Plugin packs (k8s, ci-cd, uiux)

## Plugin Packs

| Pack | Description | Triggers |
|------|-------------|----------|
| k8s-pack | Kubernetes | deploy, k8s, pod, helm |
| ci-cd-pack | CI/CD | github, actions, ci, cd |
| uiux-pack | Design | tailwind, shadcn |
| github-pack | GitHub | issues, pr |

## Конфигурация

```bash
# .env
LLM_PROVIDER=auto
MINIMAX_API_KEY=sk-xxx
ZAI_API_KEY=xxx
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
JWT_SECRET=your-secret
JWT_ENABLED=true
P9I_API_KEY=sk-p9i-your-key
```

## Endpoints

| Endpoint | Описание |
|----------|----------|
| `http://localhost:8000/mcp` | Local MCP |
| `http://mcp.coderweb.ru/mcp` | External MCP |

## Тестирование

```bash
pytest
pytest tests/test_storage.py
pytest --cov=src
```

## Документация

- [CLAUDE.md](CLAUDE.md) — Claude Code интеграция
- [MCP-CONFIG.md](docs/MCP-CONFIG.md) — MCP конфигурация
- [docs/how-to/](docs/how-to/) — How-to гайды
- [docs/explanation/adr/](docs/explanation/adr/) — Architecture Decision Records
