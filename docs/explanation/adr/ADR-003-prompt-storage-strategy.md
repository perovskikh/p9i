# ADR-003: Prompt Storage Strategy - Files + Lazy Loading

## Status
**Accepted** | 2026-03-20

## Context

**Question:** Should prompts be stored in PostgreSQL + Redis or remain as files?

**Requirements from previous ADRs:**
- Lazy Loading (−64% token savings)
- Baseline protection (SHA256)
- Fast access for LLM

## Decision

**Chosen Approach:** File-based storage with Lazy Loading

### Architecture

```
prompts/*.md (files) → TieredPromptLoader → lru_cache → LLM
                              ↓
                    SHA256 Baseline verification
```

### Why NOT PostgreSQL + Redis

| Factor | Files + Lazy Loading | PostgreSQL + Redis |
|--------|---------------------|-------------------|
| **Tokens** | ✅ −64% (works) | ❌ Same |
| **Speed** | ~1ms (cache) | ~1ms (Redis) |
| **Versioning** | ✅ Git | Table |
| **Baseline** | ✅ SHA256 files | Complex |
| **Server Start** | ✅ No DB needed | ❌ DB required |

### Token Economics

```
Request flow (both approaches):
User Request → Load Prompt → Send to LLM → Response
                         ↑
              This is where tokens are used

Loading from: File / Redis / PostgreSQL
↓ DOES NOT AFFECT TOKENS ↓
Tokens = prompt_content + user_input + response
```

**Conclusion:** Database choice affects SPEED, not TOKENS.
Lazy Loading affects TOKENS.

## Consequences

### Positive
- ✅ Lazy Loading already saves −64% tokens
- ✅ Git versioning (change history)
- ✅ Simple baseline lock (SHA256 on files)
- ✅ No DB dependency at startup
- ✅ Easy migration (copy files)

### Trade-offs
- ⚠️ Slower first read (50ms vs 10ms)
- ⚠️ No full-text search on content
- ⚠️ No transactions

## When to Reconsider

Move to PostgreSQL when:
- 1000+ prompts
- >10 concurrent users
- Need complex content search
- Enterprise requirements (ACL, audit)

## Related ADR

- **ADR-001:** System Genesis (flat file structure)
- **ADR-002:** Tiered Architecture (Lazy Loading implemented)

---

**Created:** 2026-03-20
**Status:** Proposed for discussion
