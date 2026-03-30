# p9i — AI Prompt System

> **p9i** (p=prompt, 9=#, i=index) — MCP-сервис для управления AI-промтами с полным циклом: от идеи до production-реализации.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastMCP](https://img.shields.io/badge/FastMCP-3.1+-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Multi-Agent](https://img.shields.io/badge/Agents-7-orange.svg)](#multi-agent-orchestrator)

## О проекте

p9i — это MCP (Model Context Protocol) сервер для управления AI-промтами через полный жизненный цикл: от идеи до production-реализации. Система включает 18+ MCP инструментов для выполнения промтов, их связывания, версионирования, JWT-аутентификации и управления памятью проекта.

## Содержание

- [Возможности](#возможности)
- [Быстрый старт](#быстрый-старт)
- [Установка](#установка)
- [Development Setup](#development-setup)
- [Использование](#использование)
- [Конфигурация](#конфигурация)
- [MCP Инструменты](#mcp-инструменты)
- [Архитектура](#архитектура)
- [Деплой](#деплой)
- [Тестирование](#тестирование)
- [Лицензия](#лицензия)

## Возможности

| Возможность | Описание |
|-------------|----------|
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

## Быстрый старт

```bash
# Клонируй репозиторий
git clone https://github.com/p9i/p9i.git
cd p9i

# Создай конфигурацию
cp .env.example .env
# Добавь API ключи в .env (MINIMAX_API_KEY, ZAI_API_KEY и т.д.)

# Запусти сервер (рекомендуется)
docker compose up -d

# Или через Makefile
make dev
```

## Установка

### Docker (рекомендуется)

```bash
# Сборка образа
docker build -f docker/Dockerfile -t p9i .

# Запуск с Web UI + MCP (port 8000 + 8080)
docker run --rm -d -p 8000:8000 -p 8080:8080 \
  -v $PWD/.env:/app/.env \
  p9i
```

### Локальная разработка

```bash
# Установка зависимостей
pip install -e .

# Запуск сервера
MCP_TRANSPORT=streamable-http python -m src.api.server
```

### K3s (Production)

```bash
# Сборка и пуш в локальный registry
docker build -f docker/Dockerfile -t p9i .
docker tag p9i:latest localhost:5000/p9i:k8s
docker push localhost:5000/p9i:k8s

# Деплой
sudo k3s kubectl apply -f k8s/
```

## Development Setup

### Pre-commit Hooks

Проект использует pre-commit хуки для автоматической валидации ADR файлов при коммите.

```bash
# Установить pre-commit
pip install -r .pre-commit-requirements.txt

# Активировать хуки
pre-commit install --install-hooks

# Запустить вручную
pre-commit run --all-files
```

**Валидация ADR:** hook проверяет формат именования (ADR-NNN-title.md), уникальность номеров и тем.

### Запуск без хуков (не рекомендуется)

```bash
git commit --no-verify -m "message"
```

## Использование

### Claude Code

```json
{
  "mcpServers": {
    "p9i": {
      "type": "http",
      "url": "http://mcp.coderweb.ru/mcp",
      "headers": { "X-API-Key": "sk-p9i-codeshift-mcp.coderweb.ru" }
    }
  }
}
```

### Команды

| Команда | Описание |
|---------|----------|
| `init p9i` | Адаптировать к проекту |
| `создай функцию` | Сгенерировать код |
| `проверь код` | Code review |
| `приведи к стандарту` | Привести к стандартам |

### HTTP API

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "X-API-Key: sk-p9i-codeshift-dev" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"p9i","arguments":{"request":"создай функцию"}}}'
```

## Конфигурация

Скопируйте `.env.example` в `.env` и настройте:

```bash
# Primary Provider
LLM_PROVIDER=auto

# API Keys
MINIMAX_API_KEY=sk-xxx
ZAI_API_KEY=xxx

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# JWT
JWT_SECRET=your-secret
JWT_ENABLED=true

# API Key
P9I_API_KEY=sk-p9i-your-key
```

## MCP Инструменты

### Основные

| Инструмент | Назначение |
|------------|------------|
| `p9i` | Unified router — естественноязыковый интерфейс |
| `run_prompt` | Выполнить промт |
| `run_prompt_chain` | Выполнить цепочку промтов |
| `list_prompts` | Список доступных промтов |
| `get_prompt` | Получить промт по имени |

### Управление памятью

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

### Генерация UI/UX

| Инструмент | Фреймворк |
|------------|-----------|
| `generate_tailwind` | TailwindCSS |
| `generate_shadcn` | shadcn/ui |
| `generate_textual` | Textual |
| `generate_tauri` | Tauri |

## Архитектура

```
p9i/
├── src/
│   ├── api/                  # FastMCP сервер
│   ├── application/          # Use cases, Agent routing
│   ├── domain/               # Entities, Business rules
│   ├── infrastructure/       # LLM adapters, External services
│   ├── services/             # Business logic
│   ├── storage/              # Data access layer
│   └── middleware/           # JWT, RBAC
├── prompts/                  # 85+ markdown промтов
│   ├── core/                 # Baseline (SHA256 locked)
│   ├── universal/            # 40+ agent prompts
│   └── packs/                # Plugin packs (k8s, ci-cd)
└── memory/                   # Project memory
```

### Multi-Agent Оркестрация

| Agent | Назначение | Keywords |
|-------|-----------|----------|
| `full_cycle` | Полный цикл | реализуй, сделай, e2e |
| `architect` | Архитектура | архитектура, спроектируй |
| `developer` | Код | создай, добавь, напиши |
| `reviewer` | Ревью | проверь, приведи |
| `designer` | UI/UX | дизайн, кнопка |
| `devops` | CI/CD | deploy, k8s, ci-cd |

### Endpoints

| Endpoint | Описание |
|----------|----------|
| `http://localhost:30080/mcp` | K3s NodePort |
| `http://mcp.coderweb.ru/mcp` | Traefik ingress |
| `http://localhost:8501` | Web UI (Streamlit) |

## Деплой

### Makefile команды

```bash
make dev         # docker compose up
make deploy      # kubectl apply -f k8s/
make watch       # kubectl logs -f
make status      # kubectl get all -n p9i
make scale REPLICAS=5
make hpa
```

### Helm

```bash
helm upgrade --install p9i ./helm/p9i \
  --namespace p9i \
  --create-namespace \
  --wait \
  --timeout 15m
```

## Тестирование

```bash
# Все тесты
pytest

# specific
pytest tests/test_storage.py

# С покрытием
pytest --cov=src
```

## ADR Phases

| Phase | Status | Описание |
|-------|--------|----------|
| 1 | ✅ | Tiered directories, baseline lock |
| 2 | ✅ | PromptStorageV2, cascade priority |
| 3 | ✅ | 7 MPV stage prompts |
| 4 | ✅ | Plugin Packs (k8s, ci-cd) |
| 5 | ✅ | JWT Auth, RBAC, HTTPS Proxy |
| 6 | ✅ | Context7 MCP Integration |
| 7 | ✅ | Pipeline (interview, decompose) |
| 8 | ✅ | UI/UX Generation |
| 9 | ✅ | Multi-Agent Orchestrator (7 agents) |
| 10 | ✅ | Clean Architecture |
| 11 | ✅ | Pre-commit hooks installation |
| **Total** | **8 ADRs** | See [docs/explanation/adr/](docs/explanation/adr/) |

## Лицензия

MIT License — see [LICENSE](LICENSE) for details.

---

Built with FastMCP, PostgreSQL, Redis, and AI agents.
