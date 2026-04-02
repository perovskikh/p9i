# ADR-016a: Code Explorer Agent — MVP (1-2 Days)

## Status
**Proposed** | 2026-04-02

## Context

### Problem Statement

Claude Code has a specialized `code-explorer` agent (lightweight, fast, read-only) for deep codebase navigation. p9i lacks this capability — users cannot ask "how does X work?" or "find all dependencies of Y".

### Reference: Claude Code code-explorer Agent

Claude Code's explorer is:
- **Model**: haiku (fast, lightweight)
- **Tools**: Glob, Grep, Read, LS, WebFetch, WebSearch
- **Mode**: READ-ONLY (no file creation/modification)
- **Constraints**: Disallowed tools = AGENT_TOOL_NAME, EXIT_PLAN_MODE_TOOL_NAME, FILE_EDIT_TOOL_NAME, FILE_WRITE_TOOL_NAME, NOTEBOOK_EDIT_TOOL_NAME
- **Purpose**: Find files by patterns, search code for keywords, answer codebase questions

### Strategic Fit

| Агент | Фокус | Explorer Enhancement |
|-------|-------|---------------------|
| `architect` | System design | Architecture layer mapping |
| `reviewer` | Code review | Execution tracing, impact analysis |
| `developer` | Code generation | Entry point identification |
| `explorer` | **Deep navigation** | **Find, trace, map code relationships** |

---

## Decisions

### 1. Explorer Agent Prompt (MVP)

**File**: `prompts/agents/explorer/promt-explorer-mvp.md`

**Key Features:**
- **Model**: haiku (fast, economic)
- **READ-ONLY MODE**: Strict prohibition on file modifications
- **Forbidden Tools**: AGENT_TOOL_NAME, EXIT_PLAN_MODE_TOOL_NAME, FILE_EDIT_TOOL_NAME, FILE_WRITE_TOOL_NAME, NOTEBOOK_EDIT_TOOL_NAME

```markdown
=== CRITICAL: READ-ONLY MODE - NO FILE MODIFICATIONS ===

This is a READ-ONLY exploration task. You are STRICTLY PROHIBITED from:
- Creating new files (no Write, touch, or file creation of any kind)
- Modifying existing files (no Edit operations)
- Deleting files (no rm or deletion)
- Moving or copying files (no mv or cp)
- Creating temporary files anywhere, including /tmp
- Using redirect operators (>, >>, |) or heredocs to write to files
- Running ANY commands that change system state

Your role is EXCLUSIVELY to search and analyze existing code.
```

---

### 2. P9iRouter Integration (MVP)

**File**: `src/application/p9i_router.py` additions

```python
# === EXPLORER ===
"как работает": (IntentType.AGENT_TASK, "explorer"),
"как работают": (IntentType.AGENT_TASK, "explorer"),
"как работать": (IntentType.AGENT_TASK, "explorer"),
"explore": (IntentType.AGENT_TASK, "explorer"),
"навигац": (IntentType.AGENT_TASK, "explorer"),
"найди все": (IntentType.AGENT_TASK, "explorer"),
"найди где": (IntentType.AGENT_TASK, "explorer"),
"trace": (IntentType.AGENT_TASK, "explorer"),
"трассируй": (IntentType.AGENT_TASK, "explorer"),
"связи": (IntentType.AGENT_TASK, "explorer"),
"dependencies": (IntentType.AGENT_TASK, "explorer"),
"зависимости": (IntentType.AGENT_TASK, "explorer"),
"вызовы": (IntentType.AGENT_TASK, "explorer"),
"вызов": (IntentType.AGENT_TASK, "explorer"),
"найди вызовы": (IntentType.AGENT_TASK, "explorer"),
"покажи структуру": (IntentType.AGENT_TASK, "explorer"),
"структура кода": (IntentType.AGENT_TASK, "explorer"),
"архитектура кода": (IntentType.AGENT_TASK, "explorer"),
"что делает": (IntentType.AGENT_TASK, "explorer"),
"где находится": (IntentType.AGENT_TASK, "explorer"),
"найди файл": (IntentType.AGENT_TASK, "explorer"),
"файлы": (IntentType.AGENT_TASK, "explorer"),
```

---

### 3. Agent Directory Structure

```
prompts/agents/explorer/
├── promt-explorer-mvp.md          # MVP prompt
├── promt-explorer-extended.md      # Extended with caching
└── promt-verification.md          # Verification agent
```

---

## Implementation Plan

### Day 1: Core Implementation

| Time | Task | Deliverable |
|------|------|-------------|
| Morning | Create prompt file `promt-explorer-mvp.md` | Prompt with role, tools, patterns |
| Morning | Add explorer keywords to P9iRouter | Routing table updates |
| Afternoon | Integrate with AgentOrchestrator | Explorer agent callable |
| Afternoon | Basic testing | Explorer responds to queries |

### Day 2: Refinement

| Time | Task | Deliverable |
|------|------|-------------|
| Morning | Edge cases (large files, binary) | Graceful handling |
| Morning | Response format consistency | Matches spec |
| Afternoon | Documentation | Usage examples |
| Afternoon | Integration testing | All routing paths work |

---

## Enhanced Constraints (from Claude Code)

### READ-ONLY MODE Enforcement

| Forbidden Tool | Reason | Error if Attempted |
|---------------|--------|-------------------|
| AGENT_TOOL_NAME | Prevents spawning sub-agents | "Sub-agents not allowed in read-only mode" |
| EXIT_PLAN_MODE_TOOL_NAME | Prevents leaving read-only | "Cannot exit read-only mode" |
| FILE_EDIT_TOOL_NAME | Prevents modifications | "File editing disabled" |
| FILE_WRITE_TOOL_NAME | Prevents file creation | "File creation disabled" |
| NOTEBOOK_EDIT_TOOL_NAME | Prevents notebook edits | "Notebook editing disabled" |

### Model Selection

| Model | Use Case | Justification |
|-------|----------|---------------|
| **haiku** | Default for explorer | Fast, cheap, sufficient for read-only search |
| **inherit** | For complex analysis | When parent agent model is better |

---

## Comparison: Claude Code vs p9i Explorer MVP

| Aspect | Claude Code | p9i MVP |
|--------|-------------|---------|
| Model | haiku | MiniMax-M2.7 (haiku-level) |
| Tools | Glob, Grep, Read, LS, WebFetch | Glob, Grep, Read, BashOutput |
| Routing | Built-in | P9iRouter keyword match |
| READ-ONLY enforcement | Yes (forbidden tools) | Yes (same pattern) |
| Caching | None | None (MVP) |
| Context | Current session | Current session |
| Latency | ~200ms | ~500ms (network LLM) |

---

## Consequences

### Positive
- Fast implementation (1-2 days)
- No new infrastructure needed
- Complements existing agents
- User can ask "how does X work?"
- READ-ONLY enforcement prevents accidents

### Negative
- No persistence between sessions
- No indexing (每次查询重新扫描)
- Limited to single-file analysis

### Risks
- Large codebases may timeout
- Complex call chains hard to trace

---

## Related ADRs

- [ADR-007: Multi-Agent Orchestrator](ADR-007-multi-agent-orchestrator.md)
- [ADR-016b: Explorer Agent — Extended](ADR-016b-explorer-agent-extended.md)
- [ADR-016c: Verification Agent](ADR-016c-verification-agent.md)

---

## References

- [Claude Code code-explorer agent](https://github.com/anthropics/claude-code/blob/main/plugins/feature-dev/agents/code-explorer.md)
- [exploreAgent.ts](https://github.com/perovskikh/claude-code-sourcemap/blob/main/restored-src/src/tools/AgentTool/built-in/exploreAgent.ts)
