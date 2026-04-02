# ADR-017: Reviewer Agent Refactoring

**Date**: 2026-04-02
**Status**: Proposed
**Supersedes**: ADR-013, ADR-014

## Context

Текущий reviewer agent в p9i:
- Использует базовый `promt-llm-review` с JSON output
- Не интегрирован с MCP tools для code analysis
- Нет параллельных sub-agents как в Claude Code `simplify` skill
- Нет adversarial verification pattern

Claude Code имеет проверенные паттерны:
- **simplify.ts**: 3 параллельных агента (Reuse, Quality, Efficiency)
- **verificationAgent.ts**: Adversarial testing с VERDICT output
- **security-review.ts**: Git diff based security analysis
- **exploreAgent.ts**: Read-only, haiku model, forbidden tools

## Decision

Рефакторим reviewer agent по аналогии с explorer agent:

### Architecture: 4-Layer Reviewer System

```
reviewer/
├── MVP Layer (Fast, focused)
│   └── promt-reviewer-mvp.md
│       - Model: haiku (fast, экономичный)
│       - Max tools: 3
│       - Scope: git diff focused, single file
│
├── Enhanced Layer (Deep, parallel)
│   └── promt-reviewer-enhanced.md
│       - Model: inherit (от родительского агента)
│       - Max tools: 5
│       - 3-phase parallel review (Reuse, Quality, Efficiency)
│       - Caching support
│
├── Security Layer (Specialized)
│   └── promt-reviewer-security.md
│       - Model: inherit
│       - Security categories: SQL injection, XSS, auth bypass
│       - 80% confidence threshold
│       - Git diff based
│
└── Verification Layer (Adversarial)
    └── promt-verification.md
        - Model: haiku (для скорости) / inherit (для сложных)
        - MUST run actual tests, not narrate
        - Outputs VERDICT: PASS / FAIL / PARTIAL
        - Adversarial probes required
```

### MCP Tools (reviewer_tools.py)

```python
class ReviewerTools:
    async def reviewer_search(query: str, file_pattern: str = "*.py")
        # Search code patterns (vulnerabilities, anti-patterns)

    async def reviewer_diff(scope: str = "unstaged")
        # Get git diff for review scope

    async def reviewer_security(file_path: str)
        # Security scan for specific file

    async def reviewer_quality(file_path: str)
        # Quality metrics (complexity, duplication)

    async def reviewer_metrics(file_path: str)
        # Code metrics: cyclomatic complexity, LOC, coupling
```

### Claude Code Patterns to Implement

#### 1. simplify.ts Pattern (3-Phase Parallel Review)

```
Phase 1: Get git diff
Phase 2: Launch 3 agents in parallel:
  - Reuse Review: Find existing utilities to replace new code
  - Quality Review: Redundant state, copy-paste, leaky abstractions
  - Efficiency Review: N+1, missed concurrency, memory leaks
Phase 3: Aggregate findings and fix
```

#### 2. verificationAgent Pattern (Adversarial Testing)

```
Core Principles:
- Verification avoidance = FAIL
- Must RUN tests, not narrate
- At least ONE adversarial probe required
- Output: VERDICT: PASS/FAIL/PARTIAL

Strategies by change type:
- Frontend: Browser automation, curl, screenshots
- Backend: Start server, curl endpoints, verify response
- CLI: Run with inputs, verify stdout/stderr/exit codes
- Bug fixes: Reproduce bug, verify fix, check regressions
```

#### 3. security-review Pattern

```
Categories:
- Input validation: SQL injection, command injection, XXE
- Auth & Authz: Bypass logic, privilege escalation
- Crypto: Hardcoded keys, weak crypto
- Injection: RCE, XSS, eval injection
- Data exposure: PII handling, API leakage

Rules:
- 80%+ confidence to report
- Only HIGH and MEDIUM severity
- No theoretical issues
```

### Forbidden Tools (READ-ONLY enforcement)

| Tool | Reason |
|------|--------|
| FILE_WRITE_TOOL_NAME | Review is read-only |
| FILE_EDIT_TOOL_NAME | No modifications |
| NOTEBOOK_EDIT_TOOL_NAME | No notebook edits |
| AGENT_TOOL_NAME | No nested agents in MVP |
| EXIT_PLAN_MODE_TOOL_NAME | Stay in review mode |

### Routing Updates

```python
# p9i_router.py - Add new keywords
"reviewer": [
    # Existing
    "проверь", "ревью", "аудит", "security",
    # New from Claude Code patterns
    "simplify",       # simplify skill
    "verify",         # verification agent
    "quality",        # quality review
    "efficiency",    # efficiency review
    "reuse",          # reuse review
]
```

## Consequences

### Positive
- Интеграция с MCP tools (как explorer)
- Параллельные агенты (как Claude Code simplify)
- Adversarial verification
- Security audit layer
- READ-ONLY enforcement

### Negative
- Более сложная архитектура
- Больше промптов поддерживать
- Нужен reviewer_tools.py

## Implementation Plan

1. **Phase 1**: Create `promt-reviewer-mvp.md` (haiku, 3 tools, git diff)
2. **Phase 2**: Create `promt-reviewer-enhanced.md` (3-phase parallel)
3. **Phase 3**: Create `promt-reviewer-security.md` (security categories)
4. **Phase 4**: Create `promt-verification.md` (adversarial, VERDICT)
5. **Phase 5**: Create `reviewer_tools.py` (MCP wrapper)
6. **Phase 6**: Update routing in `agent_router.py` и `p9i_router.py`
7. **Phase 7**: Deprecate `promt-llm-review`, `promt-enhanced-reviewer.md`

## What to Keep / What to Discard

### Keep from Current
- ✅ promt-enhanced-reviewer.md criteria (confidence scoring, severity grouping)
- ✅ Security categories from promt-security-audit
- ✅ Quality gates logic

### Discard
- ❌ promt-llm-review (JSON format, superseded by structured markdown)
- ❌ promt-quality-test (merged into enhanced)
- ❌ No checkpoint support (like explorer, reviewer is stateless)

## Notes

参考 Claude Code:
- `src/skills/bundled/simplify.ts` - 3-phase parallel
- `src/tools/AgentTool/built-in/verificationAgent.ts` - adversarial
- `src/commands/security-review.ts` - security categories
- `src/tools/AgentTool/built-in/exploreAgent.ts` - tool restrictions pattern

## Implementation Status

### ✅ Implemented (Phase 1-6)
1. `promt-reviewer-mvp.md` — haiku, 3 tools, git diff focused
2. `promt-reviewer-enhanced.md` — 3-phase review (sequential, not parallel)
3. `promt-verification.md` — adversarial testing, VERDICT output
4. `reviewer_tools.py` — MCP wrapper (diff, search, security, quality, metrics)
5. Routing updates in `agent_router.py` — new keywords

### 🔜 TODO (Phase 7+)
1. `promt-reviewer-security.md` — dedicated security audit prompt (80% threshold)
2. Интеграция с `explorer_tools` — reuse analysis использует `explorer_search`
3. Cache layer — добавить Redis caching как у explorer agent

### ❌ Rejected / Deferred
1. **Параллельные sub-agents** — не поддерживается в read-only режиме p9i
2. `promt-llm-review` — JSON формат заменен markdown
3. `promt-enhanced-reviewer.md` (old) — deprecated, replaced by new structure
4. `promt-quality-test` — merged into enhanced review
5. **promt-verification в explorer** — перемещен в reviewer agent
