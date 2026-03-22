# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Prompt System is an MCP (Model Context Protocol) server for managing AI prompts through their full lifecycle: from idea to production implementation. It provides 10 MCP tools for prompt execution, chaining, versioning, and project memory management.

The system supports natural language interaction through `ai_prompts` which automatically routes requests to appropriate prompts based on intent keywords.

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
pytest tests/test_specific.py

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
docker build -f docker/Dockerfile -t ai-prompt-system .

# Run with volume mounts (for development)
docker run --rm -i \
  -v $PWD/.env:/app/.env \
  -v $PWD:/project \
  -v $PWD/memory:/app/memory \
  ai-prompt-system
```

## Architecture

The system follows an MCP server architecture with the following key components:

```
src/api/server.py         # FastMCP server with 10 tools (main entry point)
src/services/executor.py  # PromptExecutor - executes prompts through LLM
src/services/llm_client.py  # LLMClient - multi-provider support
src/services/memory.py    # MemoryService - project context management
src/storage/prompts.py    # PromptStorage - loads and manages prompts
src/storage/database.py   # Database connection (PostgreSQL + Redis)
prompts/                 # 13 markdown prompt files with registry.json
memory/                  # Project context/memory storage (per-project JSON files)
config/                  # YAML configs for settings and API keys
docker/                  # Dockerfile and docker-compose.yml
```

### MCP Tools (10 total)

1. `ai_prompts` - **Natural language router** - Parse intent and auto-select appropriate prompt
2. `run_prompt` - Execute a single prompt through LLM
3. `run_prompt_chain` - Execute multi-stage prompt chain (ideation → finish)
4. `list_prompts` - List available prompts from registry
5. `get_project_memory` - Get project context/memory
6. `save_project_memory` - Save project context
7. `adapt_to_project` - Auto-detect project stack (Python/JS, frameworks, DB)
8. `clean_context` - Clean context when token limit exceeded
9. `context7_lookup` - Get Context7 library ID for documentation lookup
10. `get_available_mcp_tools` - List all available tools

### AI Prompts Intent Map

The `ai_prompts` tool routes natural language requests based on keywords:

| Keyword | Prompt | Purpose |
|---------|--------|---------|
| `feature`, `добавить`, `создать`, `new feature` | promt-feature-add | Add new functionality |
| `bug`, `исправить`, `фикс`, `fix bug`, `баг` | promt-bug-fix | Fix bugs |
| `refactor`, `рефакторинг`, `улучшить код` | promt-refactoring | Refactor code |
| `security`, `безопасност`, `audit` | promt-security-audit | Security audit |
| `test`, `тест`, `quality` | promt-quality-test | Quality testing |
| `ci-cd`, `pipeline`, `deploy` | promt-ci-cd-pipeline | CI/CD setup |
| `version`, `версион` | promt-versioning-policy | Versioning policy |
| `adapt`, `адаптац`, `onboard` | promt-project-adaptation | Project adaptation |
| `создай промт`, `new prompt`, `шаблон` | promt-prompt-creator | Create prompts |
| `адаптируй`, `init ai-promts`, `новый проект` | promt-system-adapt | Initialize system |

### Transport Modes

The server supports two transport modes controlled by `MCP_TRANSPORT` env var:

- **stdio** (default) - For Claude Code MCP integration
- **sse** - For HTTP-based MCP clients (runs on port 8000)

### Data Flow

- **Prompts**: Stored as `.md` files in `prompts/` directory, registered in `prompts/registry.json`
- **Memory**: Per-project JSON files stored in `memory/{project_id}/context.json`
- **API Keys**: Environment-based (`API_KEYS__SYSTEM`, `API_KEYS__PROJECT_{n}`)
- **Rate Limiting**: 60-second sliding window per API key
- **Audit Logging**: In-memory log of all API actions (max 10,000 entries)

### Prompt Format

Prompts support optional system/user section markers:

```markdown
system: System instructions here

user: User prompt here

---

# Alternative: first heading as system
# Heading content treated as system prompt
```

If no sections are found, entire content is used as system prompt.

### Storage Strategy

- **PostgreSQL** (port 5432): Persistent data (prompts, versions, projects, API keys)
- **Redis** (port 6379): Hot data, cache, pub/sub, rate limiting, sessions
- **File system**: Prompts (markdown files), Memory (JSON files)

The MCP server runs on port 8000 with SSE transport (stdio for Claude Code).

### Key Classes

- `APIKeyManager` (src/api/server.py) - Manages API keys with rate limiting (60s window), permissions
- `AuditLogger` (src/api/server.py) - Tracks all API actions in memory (max 10,000 logs)
- `PromptExecutor` (src/services/executor.py) - Executes prompts through LLM with chain support
- `LLMClient` (src/services/llm_client.py) - Multi-provider LLM client with streaming
- `MemoryService` (src/services/memory.py) - Manages project-specific context storage
- `PromptStorage` (src/storage/prompts.py) - Loads prompts from markdown files + registry
- FastMCP server instance created in `src/api/server.py`

### LLM Integration

The system executes prompts through multiple LLM providers with auto-detection:

**Provider Priority** (auto-detected from `.env`):
1. ZAI_API_KEY → GLM-4.7 (Z.ai, recommended)
2. ZAI_API_KEY → GLM-4.5-Air (Z.ai, if 4.7 unavailable)
3. OPENROUTER_API_KEY → hunter-alpha (free via OpenRouter)
4. MINIMAX_API_KEY → MiniMax-M2.5
5. DEEPSEEK_API_KEY → deepseek-chat or deepseek-reasoner
6. ANTHROPIC_API_KEY → claude-sonnet-4-20250514 (direct)
7. Fallback → hunter-alpha (free)

**Supported Models:**
- GLM-4.7, GLM-4.5-Air (via Z.ai)
- MiniMax-M2.5 (via MiniMax)
- deepseek-chat, deepseek-reasoner (via DeepSeek)
- claude-sonnet-4-20250514 (via Anthropic or Z.ai)
- openrouter/hunter-alpha (via OpenRouter, free)

**API Keys** (loaded from `.env`):
- `ZAI_API_KEY` - Primary (GLM models)
- `ANTHROPIC_API_KEY` - Anthropic direct
- `OPENROUTER_API_KEY` - OpenRouter (free models)
- `MINIMAX_API_KEY` - MiniMax fallback
- `DEEPSEEK_API_KEY` - DeepSeek fallback

**LLMClient Features:**
- Async requests with httpx
- Streaming support for real-time output
- Provider-specific payload formatting
- Automatic context injection into system prompts
- Error handling and response parsing

## Integration with Claude Code

To use with Claude Code, add to `~/.claude/settings.json`:

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
        "perovskikh/ai-prompt-system"
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
```

## Documentation

- `README.md` - Project overview and quick start
- `prompts/README.md` - Guide to using prompts
- `MCP_INTEGRATION.md` - Claude Code integration details
- `SYSTEM_ARCHITECTURE.md` - Full system diagram
- `pyproject.toml` - Project dependencies and tool configuration