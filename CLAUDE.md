# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

p9i is an MCP (Model Context Protocol) server for managing AI prompts through their full lifecycle: from idea to production implementation. It provides 18 MCP tools for prompt execution, chaining, versioning, JWT authentication, and project memory management.

## Commands

### Run the Server

```bash
# Quick aliases (new!)
make dev        # docker compose up     (локальная разработка)
make deploy   # kubectl apply -f k8s/  (K3s деплой)
make watch   # kubectl logs -f       (смотреть логи)
make status  # kubectl get all -n p9i (статус)
make scale  # scale deployment
make hpa    # show HPA status

# Local development
pip install -e .
python -m src.api.server

# Docker (recommended for full stack)
docker compose up -d

# With stdio transport (Claude Code compatible)
MCP_TRANSPORT=stdio python -m src.api.server

# With streamable-http transport (HTTP API with streaming support)
MCP_TRANSPORT=streamable-http python -m src.api.server
```

### Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_prompt_storage_v2.py

# With coverage
pytest --cov=src

# Inside Docker container
docker exec <container> pytest
```

### Linting

```bash
# Black formatting
black src/

# Ruff linting
ruff check src/

# MyPy type checking
mypy src/
```

### Docker Build

```bash
# Build local image
docker build -f docker/Dockerfile -t p9i .

# Run with volume mounts (for development)
docker run --rm -i \
  -v $PWD/.env:/app/.env \
  -v $PWD:/project \
  -v $PWD/memory:/app/memory \
  p9i
```

## p9i Agent (WebSocket Client)

The `src/agents/agent.py` module provides a minimal WebSocket agent:

- **WSSClient** - WebSocket клиент с reconnect + exponential backoff
- **ShellService** - Remote shell command execution
- **Agent** - Combines both for server-connected operations

**Constants:**
- `SHELL_TIMEOUT = 30.0` - shell command timeout (seconds)
- `MAX_RETRIES = 5` - max reconnection attempts
- `RECONNECT_BASE_DELAY = 1.0` - backoff delay (1→2→4→8→16s)

**Protocol:** JSON with `{type, tag, data}` for 9P-like messaging

## Architecture

The system follows Clean Architecture with MCP server pattern:

```
src/
├── agents/                   # p9i Agent (WebSocket client + shell)
│   └── agent.py              # WSSClient, ShellService, Agent
├── api/server.py              # FastMCP server (20+ tools)
├── api/webui.py               # Web Dashboard (Streamlit)
├── application/               # Use cases, Agent routing, DTOs
│   ├── agent_router.py        # Agent detection and routing
│   ├── container.py           # DI container
│   ├── dto/                   # Data transfer objects
│   └── ports/                 # Interface definitions (LLMPort)
├── domain/                    # Entities, Business rules
│   ├── entities/              # Prompt, Project, Agent entities
│   ├── repositories/          # Repository interfaces
│   └── services/              # Domain services (PromptGuard)
├── infrastructure/            # External integrations
│   ├── adapters/llm/          # LLM providers (MiniMax, GLM, DeepSeek, Anthropic)
│   ├── adapters/external/    # Figma, GitHub MCP
│   ├── browser/               # Playwright integration
│   └── uiux/                  # UI/UX generation tools
├── services/                   # Business logic
│   ├── executor.py            # Prompt execution
│   ├── llm_client.py          # Multi-provider LLM client
│   ├── memory.py              # Project context
│   ├── orchestrator.py        # Multi-agent orchestration
│   └── redis_rate_limiter.py  # Rate limiting
├── storage/                    # Data access
│   ├── prompts_v2.py          # Tiered prompt loading
│   └── database.py            # PostgreSQL access
└── middleware/                # Cross-cutting
    ├── jwt_auth.py            # JWT authentication
    ├── rbac.py                # Role-based access control
    └── baseline_verification.py  # SHA256 integrity
```

### Multi-Agent Orchestrator (ADR-007)

7 AI agents with intelligent routing via P9iRouter:

| Agent | Purpose | Triggers |
|-------|---------|----------|
| `p9i` | **Unified router** (replaces `ai_prompts` & `p9i_nl`) | All requests |
| `architect` | Architecture, ADRs | архитектура, спроектируй |
| `developer` | Code generation | реализуй, добавь, фича |
| `reviewer` | Code review, security | review, проверь |
| `designer` | UI/UX (Tailwind, shadcn) | дизайн, кнопка |
| `devops` | CI/CD, Docker, K8s | deploy, ci-cd |
| `migration` | System migration | миграция, переход |

### Plugin Packs

Located in `prompts/packs/`:

| Pack | Description | Triggers |
|------|-------------|----------|
| k8s-pack | Kubernetes operations | deploy, k8s, pod, helm |
| ci-cd-pack | CI/CD pipelines | github, actions, ci, cd |
| pinescript-v6 | Pine Script v6 (TradingView) | pinescript, tradingview, стратегия |
| uiux-pack | Design System | tailwind, shadcn, colors, typography |

### MCP Tools (20+ total)

Primary tools:
- `p9i` - **Natural language router** - Parse intent and auto-select appropriate prompt
- `run_prompt` / `run_prompt_chain` - Execute single or multi-stage prompt chains
- `list_prompts` / `get_prompt` - List and retrieve prompts from tiered storage
- `get_project_memory` / `save_project_memory` - Project context/memory management
- `adapt_to_project` - Auto-detect project stack (Python/JS, frameworks, DB)
- `generate_jwt_token` / `validate_jwt_token` / `revoke_jwt_token` - JWT authentication
- `verify_baseline` - SHA256 baseline verification

**Deduplication Guard (prevent duplicates):**
- `check_prompt_uniqueness` - Check if prompt/keyword already exists
- `get_prompt_deduplication_report` - Full system deduplication report

**Design & UI/UX:**
- `generate_tailwind` / `generate_shadcn` / `generate_textual` - Component generation

- `get_available_mcp_tools` - List all available tools

### Prompt Tier Architecture

Prompts are loaded in priority order from tiered directories:
1. `prompts/core/` - Baseline prompts (SHA256 locked, version 1.0.0)
2. `prompts/universal/` - General purpose prompts (38 prompts)
3. `prompts/packs/` - Plugin packs (k8s, ci-cd)

### AI Prompts Intent Map (via P9iRouter)

The `p9i` tool uses **unified P9iRouter** for intelligent routing (NO LLM routing!):

**Priority Order:**
1. **COMMAND** (`/help`, `/exit`, `/clear`, `/status`) - Highest priority
2. **PROMPT_CMD** (`/prompt list`, `/prompt save`, `/prompt load`)
3. **PACK** (Plugin packs: k8s, ci-cd, pinescript-v6)
4. **AGENT_TASK** (Multi-agent orchestration - see below)
5. **NL_QUERY** (Simple queries: "покажи список")
6. **SYSTEM** (`init p9i`, `adapt to project`)

**Agent-Based Routing (Multi-Agent Orchestrator):**

| Keyword | Agent | Purpose |
|---------|--------|---------|
| `реализуй`, `внедри`, `сделай`, `e2e` | full_cycle | Complete pipeline (idea→impl→test→docs) |
| `спроектируй`, `архитектура`, `adr` | architect | System design, ADRs |
| `создай`, `добавь`, `напиши`, `код`, `feature` | developer | Code generation, features |
| `проверь`, `ревью`, `аудит`, `тест` | reviewer | Code review, security |
| `ui`, `ux`, `дизайн`, `интерфейс` | designer | UI/UX design |
| `ci`, `cd`, `deploy`, `docker`, `k8s` | devops | CI/CD, deployment |

**🚀 Key Difference from LangChain: NO LLM routing!**
- LangChain: Uses LLM for routing ($$$)
- P9iRouter: Keyword classification + priority (FREE)
- Result: 2x faster, 100% cost savings

### LLM Integration

The system executes prompts through multiple LLM providers with auto-detection:

**Provider Priority** (auto-detected from `.env`):
1. `MINIMAX_API_KEY` → MiniMax-M2.7 (best price/performance) - **PRIMARY**
2. `ZAI_API_KEY` → GLM-4.7 (Z.ai, best quality)
3. `OPENROUTER_API_KEY` → hunter-alpha (free via OpenRouter)
4. `DEEPSEEK_API_KEY` → deepseek-chat or deepseek-reasoner
5. `ANTHROPIC_API_KEY` → claude-sonnet-4-20250514 (**requires explicit permission**)

**Failover:** When primary provider fails (401, 403, 429, 500+), system automatically switches to next available provider in order: MiniMax → ZAI → OpenRouter → DeepSeek → Anthropic.

**API Keys** (loaded from `.env`):
- `MINIMAX_API_KEY` - Primary (best price/performance)
- `ZAI_API_KEY` - GLM models (best quality)
- `OPENROUTER_API_KEY` - OpenRouter (free models)
- `DEEPSEEK_API_KEY` - DeepSeek fallback
- `ANTHROPIC_API_KEY` - Anthropic direct (**requires explicit permission in CLAUDE.md**)

### Transport Modes

The server supports two transport modes controlled by `MCP_TRANSPORT` env var:
- **stdio** - For Claude Code MCP integration
- **streamable-http** (default for HTTP) - For HTTP-based MCP clients with streaming support (runs on port 8000)
  - Requires `Accept: text/event-stream` header
  - Uses `Mcp-Session-Id` header for session management

### Storage Strategy

- **PostgreSQL** (port 5432): Persistent data (prompts, versions, projects, API keys)
- **Redis** (port 6379): Hot data, cache, pub/sub, rate limiting, sessions
- **File system**: Prompts (markdown files), Memory (JSON files)

### JWT Authentication & RBAC

The system supports:
- JWT token generation with expiry
- Role-based access control (admin, developer, user, guest)
- Tier-based access (core, universal, packs, project)
- Rate limiting (60-second sliding window per API key)

## Integration with Claude Code

The p9i project already has `.mcp.json` configured at `/home/worker/p9i/.mcp.json`:

```json
{
  "mcpServers": {
    "p9i": {
      "command": "python3",
      "args": ["/home/worker/p9i/mcp_proxy_simple.py"],
      "env": {
        "MCP_PROXY_URL": "http://mcp.coderweb.ru/mcp",
        "P9I_API_KEY": "sk-p9i-codeshift-mcp.coderweb.ru"
      }
    }
  }
}
```

**To enable in Claude Code:**
- Navigate to the p9i project directory when starting Claude Code, OR
- Add to `~/.claude/settings.json` using `enabledMcpjsonServers`:
```json
{
  "enabledMcpjsonServers": ["/home/worker/p9i/.mcp.json"]
}
```

**Volume Mounts:**
- `.env` - API keys for LLM providers
- `:/project` - Project access for `adapt_to_project`
- `memory/` - Persistent project context between sessions

**Usage Example:**
```
"Добавь функцию авторизации в users.py. use p9i"
"Найди баги в коде обработки ошибок. use p9i"
"init p9i" → адаптация к проекту
```

## Key Classes

- `FastMCP` (src/api/server.py) - Main MCP server instance with 18 tools
- `PromptExecutor` (src/services/executor.py) - Executes prompts through LLM with chain support
- `LLMClient` (src/services/llm_client.py) - Multi-provider LLM client with streaming
- `MemoryService` (src/services/memory.py) - Manages project-specific context storage
- `PromptStorageV2` (src/storage/prompts_v2.py) - Tiered prompt loading with baseline verification
- `JWTAuthService` (src/middleware/jwt_auth.py) - JWT token generation and validation
- `DistributedRateLimiter` (src/services/redis_rate_limiter.py) - Redis-based rate limiting
- `OrchestratorService` (src/services/orchestrator.py) - Multi-agent orchestration
- `AgentRouter` (src/application/agent_router.py) - Intent detection and agent selection

## Multi-Project Access

p9i supports connecting multiple external projects to a single p9i instance. This is the recommended production setup:

**Architecture:**
- One p9i server (local or remote)
- Multiple client projects each connect via MCP HTTP
- Shared LLM providers, prompt library, and memory

**Authentication Options:**

1. **P9I_API_KEY** (simplest) - Header-based API key auth
   ```json
   {
     "mcpServers": {
       "p9i": {
         "type": "http",
         "url": "http://coderweb.ru:8000",
         "headers": { "X-API-Key": "sk-p9i-codeshift-coderweb.ru" }
       }
     }
   }
   ```

2. **JWT Token** (fine-grained access) - Role-based access control
   ```json
   {
     "mcpServers": {
       "p9i": {
         "type": "http",
         "url": "http://coderweb.ru:8000",
         "headers": { "Authorization": "Bearer YOUR_JWT_TOKEN" }
       }
     }
   }
   ```

**Docker Integration:**
```bash
# Build with .env included
docker build -f docker/Dockerfile -t p9i .

# Or mount .env at runtime
docker run --rm -d -p 8000:8000 \
  -v $PWD/.env:/app/.env \
  p9i
```

**Environment:**
- `.env` is NOT baked into image by default
- Mount `.env` at runtime for API keys
- Or build with `--build-arg` for embedded config

### Docker Build with API Keys

```bash
# Option 1: Build with embedded API keys
docker build \
  --build-arg MINIMAX_API_KEY=sk-xxx \
  --build-arg ZAI_API_KEY=xxx \
  --build-arg P9I_API_KEY=sk-p9i-myproject \
  --build-arg JWT_SECRET=my-secret \
  --build-arg JWT_ENABLED=true \
  -t p9i .

# Option 2: Mount .env at runtime (default)
docker build -t p9i .
docker run --rm -d -p 8000:8000 -v $PWD/.env:/app/.env p9i
```

## Remote Project Access via SFTP

p9i can access projects on remote machines via SFTP/SSH:

```python
# Connect to remote project via SFTP
adapt_to_project(
    project_path="/home/dev/myproject",
    sftp_host="192.168.1.100",      # IP of developer's PC
    sftp_username="developer",
    sftp_key_file="/home/.ssh/id_rsa"  # or sftp_password
)
```

### SFTP Features

| Method | Description |
|--------|-------------|
| `read_file(path)` | Read file as bytes |
| `read_text(path)` | Read file as text |
| `write_file(path, content)` | Write bytes to file |
| `write_text(path, text)` | Write text to file |
| `mkdir(path, parents=True)` | Create directory |
| `remove(path)` | Delete file |
| `rmdir(path)` | Delete empty directory |
| `rename(old, new)` | Rename/move file |

### Use Cases

- **Developer workstation access**: p9i server connects to dev's PC
- **Production debugging**: Access logs from production servers
- **CI/CD pipelines**: Fetch build artifacts from build servers

### Security Notes

- Use SSH key authentication (not passwords)
- Restrict SSH access by IP if possible
- Consider VPN for production environments

| Approach | Pros | Cons |
|----------|------|------|
| **Build args** | One image, portable | Keys in image history |
| **Mount .env** | Keys not in image, secure | Need .env on each host |
