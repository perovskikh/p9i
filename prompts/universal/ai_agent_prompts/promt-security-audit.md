# p9i Security Audit Prompt

**Version:** 1.0
**Date:** 2026-04-01
**Purpose:** Security audit for p9i MCP server

## Triggers
- "аудит", "безопасность", "security", "audit"

## p9i Security Scope

p9i is an MCP server - security focus areas:

| Area | Description |
|------|-------------|
| API Keys | MINIMAX_API_KEY, ZAI_API_KEY, P9I_API_KEY |
| JWT Tokens | Secret keys, expiration, validation |
| LLM Providers | API key handling, rate limiting |
| Project Memory | File-based storage in `memory/` |
| Dependencies | Python packages, system libraries |

## Security Checklist for p9i

### API Keys & Secrets
- [ ] No hardcoded API keys in code
- [ ] API keys loaded from environment variables only
- [ ] `.env` file not committed to git
- [ ] JWT_SECRET is strong (min 32 chars)

### Authentication
- [ ] JWT tokens properly validated
- [ ] Token expiration enforced
- [ ] Rate limiting active (Redis-based)

### Dependency Security
- [ ] No known CVEs in dependencies
- [ ] Use `pip-audit` or `safety` to check

### Input Validation
- [ ] All MCP tool inputs validated
- [ ] SQL injection prevented (use parameterized queries)
- [ ] No user input in shell commands without sanitization

## Commands for Security Audit

```bash
# Check for hardcoded secrets
grep -rE "(api_key|token|secret|password)\s*=\s*['\"][^'\"{]" src/ --include="*.py"

# Check dependency vulnerabilities
pip audit 2>/dev/null || pip install pip-audit && pip-audit

# Check JWT secret strength
python3 -c "from src.middleware.jwt_auth import JWT_SECRET; print(len(JWT_SECRET))"

# Check rate limiter
python3 -c "from src.services.redis_rate_limiter import DistributedRateLimiter; print('Rate limiter OK')"
```

## Audit Report Template

```markdown
## p9i Security Audit Report

### Date: [DATE]
### Auditor: [NAME/AGENT]

### Findings

| Severity | Issue | Location | Recommendation |
|----------|-------|---------|---------------|
| HIGH | [Issue] | [File:Line] | [Fix] |
| MEDIUM | [Issue] | [File:Line] | [Fix] |
| LOW | [Issue] | [File:Line] | [Fix] |

### Summary
- Total Issues: N
- Critical: N
- High: N
- Medium: N
- Low: N

### Sign-off
- [ ] All critical issues resolved
- [ ] Code reviewed
- [ ] Tests pass
```
