# ADR-014: Fix Critical Failover and JWT Validation Issues

## Status
**Proposed** | 2026-04-01

## Context

Code review (confidence-based, threshold ≥80) identified 2 CRITICAL and 2 IMPORTANT issues:

| Severity | Issue | Location | Confidence |
|----------|-------|----------|------------|
| 🔴 CRITICAL | Failover Logic Bug | llm_client.py:405-411 | 90% |
| 🔴 CRITICAL | Failover Never Executes | llm_client.py:404-411 | 88% |
| 🟡 IMPORTANT | Unreachable Code (JWTError) | jwt_auth.py:185 | 92% |
| 🟡 IMPORTANT | Silent Fallback for Invalid Tokens | jwt_auth.py:241-242 | 86% |

---

## Decisions

### CRITICAL-1: Fix Failover Logic Bug (llm_client.py:405-411)

**Problem:**
```python
if should_failover and attempt_provider != fallback_providers[-1]:
    try:
        idx = fallback_providers.index(attempt_provider)
        next_provider = fallback_providers[idx + 1]
        continue  # ← jumps to next iteration (CORRECT)
    except (ValueError, IndexError):
        pass      # ← falls through to return (WRONG!)
return result      # ← always reached after except, defeating failover
```

**Fix:**
```python
if should_failover and attempt_provider != fallback_providers[-1]:
    try:
        idx = fallback_providers.index(attempt_provider)
        next_provider = fallback_providers[idx + 1]
        continue  # ✅ Correct: skip to next provider
    except (ValueError, IndexError):
        continue  # ✅ Also continue if provider not in list
# Only reached if should_failover=False
return result
```

### CRITICAL-2: Ensure Failover Executes for All Providers

**Problem:** If `self.provider` is not in `fallback_providers`, the except block's `pass` causes immediate return instead of trying fallbacks.

**Fix:** Change `pass` to `continue` (see above).

### IMPORTANT-1: Remove Dead Code (jwt_auth.py:185)

**Problem:**
```python
except ExpiredSignatureError:     # catches ExpiredSignatureError
    ...
except (JWTClaimsError, Exception):  # catches JWTClaimsError
    ...
except JWSSignatureError:         # catches JWSSignatureError
    ...
except JWTError as e:             # NEVER REACHED - base class
    ...
```

`JWTError` is the base class for all JWT exceptions. Python matches most specific first, so the generic handler is dead code.

**Fix:**
```python
except ExpiredSignatureError:
    logger.warning("Token expired")
    return None
except JWSSignatureError:
    logger.warning("Invalid token signature")
    return None
except JWTClaimsError as e:
    logger.warning(f"Invalid claims: {e}")
    return None
except JWTError as e:
    logger.error(f"JWT error: {e}")
    return None
except Exception as e:
    logger.error(f"Token validation error: {e}")
    return None
```

### IMPORTANT-2: Reject Invalid Tokens Explicitly (jwt_auth.py:241-242)

**Problem:**
```python
def revoke_token(self, token: str) -> bool:
    try:
        payload = jwt.decode(token, ..., options={'verify_exp': False})
        exp = payload.get("exp", 0)
        ttl = max(0, exp - int(time.time()))
    except Exception:
        ttl = self.default_expiry  # Silently accepts malformed tokens
    self._revoke_token(token, ttl)
    return True
```

**Fix:**
```python
def revoke_token(self, token: str) -> bool:
    try:
        payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm],
                          options={'verify_exp': False})
        exp = payload.get("exp", 0)
        ttl = max(0, exp - int(time.time()))
    except JWTError:
        # Reject malformed/tampered tokens - don't revoke
        logger.warning(f"Cannot revoke invalid token: {token[:20]}...")
        return False
    except Exception:
        logger.error(f"Unexpected error revoking token: {e}")
        return False
    self._revoke_token(token, ttl)
    return True
```

---

## Implementation Plan

| Order | File | Issue | Priority | Status |
|-------|------|-------|----------|--------|
| 1 | llm_client.py:405-411 | Failover Logic Bug | 🔴 CRITICAL | TODO |
| 2 | llm_client.py:404-411 | Failover Never Executes | 🔴 CRITICAL | TODO |
| 3 | jwt_auth.py:185 | Remove dead code | 🟡 IMPORTANT | TODO |
| 4 | jwt_auth.py:241-242 | Reject invalid tokens | 🟡 IMPORTANT | TODO |

**Estimated Time:** 2-3 hours (parallel work possible)

---

## Consequences

### Positive
- Failover actually works when primary provider fails
- JWT validation is more secure (rejects malformed tokens)
- No more dead code

### Negative
- `revoke_token()` now returns `False` for invalid tokens (minor breaking change in error handling)
- Requires testing of failover scenarios

### Testing Required
- [ ] Unit test: failover when primary returns 401/403/429/5xx
- [ ] Unit test: malformed JWT token handling in `revoke_token()`
- [ ] Unit test: expired token in `revoke_token()`

---

## References

- Code Review Report (this session)
- [JWT Auth Implementation](../middleware/jwt_auth.py)
- [LLM Client Implementation](../services/llm_client.py)
