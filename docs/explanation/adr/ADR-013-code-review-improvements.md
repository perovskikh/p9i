# ADR-013: Code Quality Improvements from Security Review

**Status**: Proposed
**Date**: 2026-03-30
**Deciders**: p9i team

## Context

Code review (score: 6/10) identified critical security and architecture issues:

| Severity | Issue | Location |
|----------|-------|----------|
| 🔴 HIGH | JWT expiration not validated explicitly | jwt_auth.py:45 |
| 🔴 HIGH | No rate limiting on public endpoints | server.py:142 |
| 🔴 HIGH | String interpolation in system prompt (injection risk) | server.py:891 |
| 🟡 MEDIUM | Function >300 lines (high complexity) | server.py:2340 |
| 🟡 MEDIUM | No retry logic for transient API failures | llm_client.py:67 |
| 🟡 MEDIUM | 30+ `# type: ignore` comments (type debt) | server.py:1847 |
| 🟢 LOW | Dict-based routing instead of Enum | p9i_router.py:89 |
| 🟢 LOW | Using print instead of structured logging | server.py:412 |

## Decision

Address HIGH severity issues first, then MEDIUM and LOW.

### Phase 1: Security Fixes (Critical)

**1. JWT Expiration Validation**
```python
# jwt_auth.py - Add explicit expiration check
def validate_token(self, token: str) -> Optional[JWTPayload]:
    payload = self._decode_token(token)
    if not payload:
        return None

    # Explicit expiration check
    exp = payload.get('exp', 0)
    if exp < time.time():
        logger.warning(f"JWT token expired at {datetime.fromtimestamp(exp)}")
        return None

    return JWTPayload(**payload)
```

**2. Rate Limiting Enhancement**
```python
# server.py - Add distributed rate limiter middleware
from src.services.redis_rate_limiter import create_redis_rate_limiter

# Already implemented in APIKeyManager.validate_key()
# Verify all critical endpoints use it
@mcp.tool()
async def p9i(request: str, context: dict = None, jwt_token: str = None) -> dict:
    # Rate limit check already integrated via api_keys.validate_key()
    # Verify: ensure APIKeyManager is initialized with Redis
    pass
```

**3. System Prompt Injection Prevention**
```python
# server.py - Add input sanitization for user-controlled prompt parts
from typing import Any

def sanitize_for_prompt(value: Any) -> str:
    """Sanitize user input to prevent prompt injection."""
    if not isinstance(value, str):
        value = str(value)
    # Remove potential injection patterns
    dangerous_patterns = ['{{', '}}', '${', '```']
    for pattern in dangerous_patterns:
        value = value.replace(pattern, '')
    return value.strip()[:1000]  # Limit length

# Use in prompt execution:
input_data = {k: sanitize_for_prompt(v) for k, v in input_data.items()}
```

### Phase 2: Architecture Improvements

**1. Decompose server.py (3000+ lines)**
```
src/
├── api/
│   ├── server.py          # Keep minimal FastMCP setup
│   ├── routes/            # NEW: Endpoint handlers
│   │   ├── auth.py        # JWT endpoints
│   │   ├── prompts.py      # Prompt management
│   │   ├── agents.py       # Agent orchestration
│   │   └── tools.py        # Utility endpoints
│   └── schemas/            # NEW: Pydantic models
│       ├── auth.py
│       ├── prompts.py
│       └── agents.py
```

**2. Add Retry Logic for LLM Calls**
```python
# llm_client.py - Add tenacity retry
from tenacity import retry, stop_after_attempt, wait_exponential

class LLMClient:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def _make_request(self, prompt: str, **kwargs) -> dict:
        # Existing request logic with retry on transient failures
        pass
```

**3. Type Hint Improvements**
- Audit all `# type: ignore` comments
- Add proper type annotations
- Consider using `mypy --strict` for new code

### Phase 3: Low Severity (Nice to Have)

**1. IntentType Enum for Router**
```python
# p9i_router.py - Replace dict with Enum
class IntentType(Enum):
    COMMAND = "command"
    PROMPT_CMD = "prompt_cmd"
    PACK = "pack"
    AGENT_TASK = "agent_task"
    NL_QUERY = "nl_query"
    SYSTEM = "system"
    UNKNOWN = "unknown"
```

**2. Structured Logging**
```python
# Replace print statements with logging
import structlog

logger = structlog.get_logger()
logger.info("endpoint_called", endpoint="/mcp", method="POST")
```

## Implementation Plan

| Phase | Task | Priority | Status |
|-------|------|----------|--------|
| 1.1 | JWT expiration validation | 🔴 HIGH | TODO |
| 1.2 | Rate limiting verification | 🔴 HIGH | TODO |
| 1.3 | Prompt injection sanitization | 🔴 HIGH | TODO |
| 2.1 | Decompose server.py | 🟡 MEDIUM | TODO |
| 2.2 | Add tenacity retry | 🟡 MEDIUM | TODO |
| 2.3 | Fix type hints | 🟡 MEDIUM | TODO |
| 3.1 | IntentType Enum | 🟢 LOW | TODO |
| 3.2 | Structured logging | 🟢 LOW | TODO |

## Consequences

### Positive
- Improved security posture
- Better maintainability
- Clearer type contracts
- Resilient LLM API calls

### Negative
- Requires testing of refactored code
- Potential breaking changes in API structure
- Need to update documentation

## References

- [Code Review Report](./ADR_INDEX.md) - Full review details
- [JWT Auth Implementation](../middleware/jwt_auth.py)
- [Rate Limiter](./services/redis_rate_limiter.py)
- [LLM Client](./services/llm_client.py)