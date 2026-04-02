# ADR-016c: Verification Agent — Red Team for Implementation

## Status
**Proposed** | 2026-04-02

## Context

### Problem Statement

After implementing explorer agents (ADR-016a, ADR-016b), we need a way to **verify** that implementations are correct. Claude Code has a specialized `VERIFICATION_AGENT` that acts as a "red team" — it tries to **break** the implementation, not just confirm it works.

### Reference: Claude Code verificationAgent.ts

Claude Code's verification agent:
- **Role**: "Your job is not to confirm the implementation works — it's to try to break it."
- **Model**: inherit (uses parent model)
- **Mode**: READ-ONLY verification (NO file modifications)
- **Key constraint**: "STRICTLY PROHIBITED from creating, modifying, or deleting any files IN THE PROJECT DIRECTORY"
- **Output**: Structured checks with PASS/FAIL/PARTIAL verdict

### Why We Need This

| Without Verification | With Verification |
|---------------------|-------------------|
| Agent says "implemented" | Agent proves it works with **real commands** |
| Tests pass (maybe mocks) | Tests run, endpoints hit, data verified |
| Happy path confirmed | **Adversarial probes** attempted |

---

## Decisions

### 1. Verification Agent Role

**File**: `prompts/agents/explorer/promt-verification.md`

```markdown
# Verification Agent — Red Team

## Role
Ты — специалист по верификации. Твоя задача — НЕ подтвердить что реализация работает,
а попытаться её СЛОМАТЬ.

Ты НЕ модифицируешь проект. Ты запускаешь реальные команды чтобы проверить.

## Core Principle
**VERIFICATION ≠ CONFIRMATION**

Твоя работа — найти проблемы, не подтвердить что всё хорошо.
```

---

### 2. Forbidden Tools (Verification)

| Tool | Reason |
|------|--------|
| AGENT_TOOL_NAME | No sub-agents |
| EXIT_PLAN_MODE_TOOL_NAME | Stay in verification mode |
| FILE_EDIT_TOOL_NAME | NO file modifications |
| FILE_WRITE_TOOL_NAME | NO file creation |
| NOTEBOOK_EDIT_TOOL_NAME | NO notebook modifications |
| **Any tool that modifies project state** | Verification only |

**Exception**: May write ephemeral test scripts to `/tmp` or `$TMPDIR` for complex tests.

---

### 3. Verification Output Format (REQUIRED)

Every verification check MUST follow this exact structure:

```markdown
### Check: [что проверяешь]

**Command run:**
[точная команда которую выполнил]

**Output observed:**
[актуальный вывод — копипаст, не пересказ]

**Expected vs Actual:**
[что ожидал vs что получил]

**Result: PASS** | **FAIL** | **PARTIAL**
```

### Example Output:

```markdown
### Check: POST /api/register validation

**Command run:**
curl -s -X POST localhost:8000/api/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"t@t.co","password":"short"}'

**Output observed:**
{
  "error": "password must be at least 8 characters"
}
(HTTP 400)

**Expected vs Actual:**
Expected 400 with password-length error. Got exactly that.

**Result: PASS**
```

### Required Ending:

```
VERDICT: PASS
```
или
```
VERDICT: FAIL
```
или
```
VERDICT: PARTIAL
```

---

### 4. Verification Strategy by Change Type

#### Frontend Changes
```
1. Start dev server
2. Check for browser automation tools (mcp__playwright__*, mcp__claude-in-chrome__*)
3. USE them: navigate, screenshot, click, read console
4. curl page subresources (images, API routes)
5. Run frontend tests
```

#### Backend/API Changes
```
1. Start server
2. curl/fetch endpoints
3. Verify response shapes (not just status codes)
4. Test error handling
5. Check edge cases
```

#### CLI/Script Changes
```
1. Run with representative inputs
2. Verify stdout/stderr/exit codes
3. Test edge inputs (empty, malformed, boundary)
4. Verify --help / usage output
```

#### Bug Fixes
```
1. Reproduce original bug
2. Verify fix works
3. Run regression tests
4. Check related functionality
```

---

### 5. Adversarial Probes

Beyond happy path — try to break it:

| Probe Type | What to Test |
|------------|--------------|
| **Concurrency** | Parallel requests to create-if-not-exists paths |
| **Boundary values** | 0, -1, empty string, very long strings, unicode, MAX_INT |
| **Idempotency** | Same mutating request twice |
| **Orphan operations** | Delete/reference IDs that don't exist |

---

### 6. Recognizing Rationalizations

The agent will feel the urge to skip checks. These are **excuses** — recognize and do opposite:

| Rationalization | What to Do |
|-----------------|------------|
| "The code looks correct" | **Run it.** Reading is not verification. |
| "The implementer's tests already pass" | **Verify independently.** Tests may be mocked. |
| "This is probably fine" | **Run it.** "Probably" is not verified. |
| "Let me check the code" | **No.** Start the server and hit the endpoint. |

---

## Implementation Plan

### Day 1: Basic Verification Agent

| Task | Deliverable |
|------|-------------|
| Create promt-verification.md | Verification prompt with constraints |
| Add verification keywords to P9iRouter | "проверь", "верифицируй", "verify" |
| Test with simple cases | Agent produces PASS/FAIL output |

### Day 2: Adversarial Probes

| Task | Deliverable |
|------|-------------|
| Implement probe templates | Concurrency, boundary, idempotency tests |
| Response format enforcement | Must end with VERDICT: PASS/FAIL/PARTIAL |
| Edge case handling | Large files, timeouts, errors |

---

## Integration with Explorer Agents

```
┌─────────────────────────────────────────────────────────────┐
│                      p9i Router                             │
└─────────────────────────────┬───────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
   ┌───────────┐        ┌───────────┐        ┌───────────┐
   │architect  │        │ reviewer  │        │developer  │
   └─────┬─────┘        └─────┬─────┘        └─────┬─────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │    EXPLORER     │
                     │  (read-only)    │
                     └────────┬────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
   ┌───────────┐        ┌───────────┐        ┌───────────┐
   │   Plan    │        │   Deep    │        │Verification│
   │  (read)   │        │  Analysis │        │  (red team)│
   └───────────┘        └───────────┘        └───────────┘
```

---

## Comparison: Current reviewer vs Verification Agent

| Aspect | Current reviewer | Verification Agent |
|--------|-----------------|-------------------|
| Focus | Code correctness | **Behavior verification** |
| Method | Reads code | **Runs real commands** |
| Output | Issues list | **PASS/FAIL with evidence** |
| Adversarial | No | **Yes (tries to break)** |
| Model | default | **inherit (parent model)** |

---

## Consequences

### Positive
- Catches issues before they reach production
- Provides **evidence** (command output) not just claims
- Forces agents to prove, not assume
- Catches edge cases and concurrency issues

### Negative
- Slower (real commands vs code reading)
- May find issues that are "works as designed"
- Requires clear specification to verify against

### Risks
| Risk | Mitigation |
|------|------------|
| "Works on my machine" | Use Docker/containerized testing |
| External dependencies down | Mock or skip with PARTIAL |
| Tests take too long | Timebox + PARTIAL verdict |

---

## Related ADRs

- [ADR-016a: Explorer Agent — MVP](ADR-016a-explorer-agent-mvp.md)
- [ADR-016b: Explorer Agent — Extended](ADR-016b-explorer-agent-extended.md)
- [ADR-007: Multi-Agent Orchestrator](ADR-007-multi-agent-orchestrator.md)

---

## References

- [Claude Code verificationAgent.ts](https://github.com/perovskikh/claude-code-sourcemap/blob/main/restored-src/src/tools/AgentTool/built-in/verificationAgent.ts)
