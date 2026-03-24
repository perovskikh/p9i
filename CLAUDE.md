# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

p9i is an MCP (Model Context Protocol) server for managing AI prompts through their full lifecycle: from idea to production implementation. It provides 18 MCP tools for prompt execution, chaining, versioning, JWT authentication, and project memory management.

## Commands

### Run the Server

```bash
# Local development
pip install -e .
python -m src.api.server

# Docker (recommended for full stack)
docker compose up -d

# With stdio transport (Claude Code compatible)
MCP_TRANSPORT=stdio python -m src.api.server

# With SSE transport (HTTP API)
MCP_TRANSPORT=sse python -m src.api.server
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

## Architecture

The system follows an MCP server architecture with the following key components:

```
src/api/server.py         # FastMCP server with 18 tools (main entry point)
src/services/executor.py  # PromptExecutor - executes prompts through LLM
src/services/llm_client.py  # LLMClient - multi-provider support (auto-detect priority)
src/services/memory.py    # MemoryService - project context management
src/storage/prompts_v2.py  # PromptStorageV2 - tiered prompt loading
src/middleware/jwt_auth.py  # JWT authentication with RBAC
src/middleware/rbac.py     # Role-based access control
```

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

### AI Prompts Intent Map

The `p9i` tool routes natural language requests based on keywords:

| Keyword | Prompt | Purpose |
|---------|--------|---------|
| `реализуй`, `внедри`, `сделай`, `e2e` | promt-feature-add | Full cycle (idea→impl→test→docs) |
| `browser`, `браузер`, `playwright` | promt-browser-integration | Browser automation |
| `feature`, `добавить`, `создать`, `new feature` | promt-feature-add | Add new functionality |
| `bug`, `исправить`, `фикс`, `fix bug`, `баг` | promt-bug-fix | Fix bugs |
| `refactor`, `рефакторинг`, `улучшить код` | promt-refactoring | Refactor code |
| `security`, `безопасност`, `audit` | promt-security-audit | Security audit |
| `test`, `тест`, `quality` | promt-quality-test | Quality testing |
| `ci-cd`, `pipeline`, `deploy` | promt-ci-cd-pipeline | CI/CD setup |
| `adapt`, `адаптац`, `onboard` | promt-project-adaptation | Project adaptation |
| `init p9i`, `адаптируй` | promt-system-adapt | Initialize system |

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
- **stdio** (default) - For Claude Code MCP integration
- **sse** - For HTTP-based MCP clients (runs on port 8000)

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

To use with Claude Code, add to `~/.claude/settings.json`:

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
        "perovskikh/p9i"
      ]
    }
  }
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
