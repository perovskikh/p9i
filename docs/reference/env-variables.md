# Environment Variables Reference

Complete reference for all environment variables in p9i.

## Usage

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your API keys
```

## LLM Providers

### Provider Selection

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LLM_PROVIDER` | string | `auto` | Explicit provider selection. Options: `auto`, `minimax`, `glm-4-7`, `glm-4-5-air`, `zai-claude`, `deepseek`, `deepseek-reasoner`, `anthropic`, `hunter` |

### MiniMax (Primary - Best Price/Performance)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MINIMAX_API_KEY` | string | - | API key from [platform.minimax.io](https://platform.minimax.io/account/api-keys) |
| `MINIMAX_ENABLED` | bool | `true` | Enable/disable this provider |
| `MINIMAX_MODEL` | string | `MiniMax-M2.7` | Model to use |
| `MINIMAX_TEMPERATURE` | float | `0.7` | Sampling temperature (0.0-2.0) |
| `MINIMAX_MAX_TOKENS` | int | `4096` | Maximum tokens in response |

### Z.ai (GLM Models - Best Quality)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ZAI_API_KEY` | string | - | API key from [z.ai](https://z.ai/dashboard/keys) |
| `ZAI_ENABLED` | bool | `true` | Enable/disable this provider |
| `ZAI_MODEL` | string | `GLM-4.7` | Model: `GLM-4.7`, `GLM-4.5-Air`, `zai-claude` |
| `ZAI_TEMPERATURE` | float | `0.7` | Sampling temperature (0.0-2.0) |
| `ZAI_MAX_TOKENS` | int | `4096` | Maximum tokens in response |

### DeepSeek

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DEEPSEEK_API_KEY` | string | - | API key from [platform.deepseek.com](https://platform.deepseek.com/api-keys) |
| `DEEPSEEK_ENABLED` | bool | `true` | Enable/disable this provider |
| `DEEPSEEK_MODEL` | string | `deepseek-chat` | Model: `deepseek-chat`, `deepseek-reasoner` |
| `DEEPSEEK_TEMPERATURE` | float | `0.7` | Sampling temperature (0.0-2.0) |
| `DEEPSEEK_MAX_TOKENS` | int | `4096` | Maximum tokens in response |

### OpenRouter (Free Models)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OPENROUTER_API_KEY` | string | - | API key from [openrouter.ai](https://openrouter.ai/settings) |
| `OPENROUTER_ENABLED` | bool | `true` | Enable/disable this provider |
| `OPENROUTER_MODEL` | string | `anthropic/claude-3-haiku` | Model name |
| `OPENROUTER_TEMPERATURE` | float | `0.7` | Sampling temperature (0.0-2.0) |
| `OPENROUTER_MAX_TOKENS` | int | `4096` | Maximum tokens in response |

### Anthropic Direct

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ANTHROPIC_API_KEY` | string | - | API key from [console.anthropic.com](https://console.anthropic.com/settings/keys) |
| `ANTHROPIC_ENABLED` | bool | `false` | Enable/disable this provider (requires CLAUDE.md permission) |
| `ANTHROPIC_MODEL` | string | `claude-sonnet-4-20250514` | Model name |
| `ANTHROPIC_TEMPERATURE` | float | `0.7` | Sampling temperature (0.0-2.0) |
| `ANTHROPIC_MAX_TOKENS` | int | `4096` | Maximum tokens in response |

## Fallback & Retry Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LLM_FAILOVER_ENABLED` | bool | `true` | Enable automatic failover when provider fails |
| `LLM_FAILOVER_ORDER` | string | `minimax,glm-4-7,hunter,deepseek,anthropic` | Custom fallback chain (comma-separated provider names) |
| `LLM_MAX_RETRIES` | int | `3` | Maximum retry attempts for rate limiting |
| `LLM_RETRY_DELAY` | float | `1.0` | Base delay between retries (seconds) |
| `LLM_TIMEOUT` | int | `120` | Request timeout (seconds) |

## Server Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MCP_TRANSPORT` | string | `stdio` | Transport mode: `stdio` (Claude Code) or `sse` (HTTP) |
| `SERVER_PORT` | int | `8000` | Server port for SSE transport |
| `LOG_LEVEL` | string | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

## Database Configuration

### PostgreSQL

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `POSTGRES_HOST` | string | `localhost` | PostgreSQL host |
| `POSTGRES_PORT` | int | `5432` | PostgreSQL port |
| `POSTGRES_DB` | string | `p9i` | Database name |
| `POSTGRES_USER` | string | `p9i` | Database user |
| `POSTGRES_PASSWORD` | string | - | Database password |

### Redis

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `REDIS_HOST` | string | `localhost` | Redis host |
| `REDIS_PORT` | int | `6379` | Redis port |
| `REDIS_PASSWORD` | string | - | Redis password |

## JWT Authentication

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `JWT_SECRET_KEY` | string | - | Secret key for JWT token generation |
| `JWT_ADMIN_KEY` | string | - | Admin key for generating admin tokens |
| `JWT_EXPIRY_HOURS` | int | `24` | Token expiration time (hours) |

## Project Adaptation

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PROJECT_ROOT` | string | `/project` | Root directory for project access (used by `adapt_to_project`) |

## Rate Limiting

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RATE_LIMIT_REQUESTS` | int | `60` | Requests per minute per API key |

## Provider Priority (Auto-Detection)

When `LLM_PROVIDER=auto`, providers are detected in this order:

1. **MiniMax** - Best price/performance (PRIMARY)
2. **Z.ai / GLM** - Best quality
3. **OpenRouter** - Free via OpenRouter
4. **DeepSeek** - Reasoning tasks
5. **Anthropic** - Requires explicit permission in CLAUDE.md
6. **Fallback** - hunter (free)

## Example Configuration

```bash
# Primary provider
LLM_PROVIDER=auto

# MiniMax (primary)
MINIMAX_API_KEY=sk-xxx
MINIMAX_ENABLED=true

# Fallback chain
LLM_FAILOVER_ORDER=minimax,glm-4-7,hunter,deepseek,anthropic
```
