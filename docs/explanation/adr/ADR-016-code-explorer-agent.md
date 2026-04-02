# ADR-016: Code Explorer Agent — Unified Implementation

## Status

**Accepted** | 2026-04-02

Supersedes: [ADR-015](ADR-015-code-explorer-agent.md), ADR-016a, ADR-016b, ADR-016c

## Context

### Problem Statement

Claude Code has a specialized `code-explorer` agent (lightweight, fast, read-only) for deep codebase navigation. p9i needs this capability to answer questions like:
- "How does authentication flow through this codebase?"
- "What are all the entry points to this API?"
- "Which modules depend on the legacy payment processor?"
- "Verify that implementation is correct"

### Reference: Claude Code Explorer Agent

```
Source: https://github.com/perovskikh/claude-code-sourcemap
File: restored-src/src/tools/AgentTool/built-in/exploreAgent.ts
```

Key features from Claude Code:
- **Model**: haiku (fast) or inherit (complex analysis)
- **READ-ONLY MODE**: Strict prohibition on file modifications
- **Forbidden Tools**: AGENT_TOOL_NAME, EXIT_PLAN_MODE_TOOL_NAME, FILE_EDIT_TOOL_NAME, FILE_WRITE_TOOL_NAME, NOTEBOOK_EDIT_TOOL_NAME
- **Tools**: Glob, Grep, Read, BashOutput (read-only shell)
- **Parallel execution**: Encourages multiple parallel tool calls

### Strategic Fit

| Agent | Focus | Explorer Enhancement |
|-------|-------|---------------------|
| `architect` | System design | Architecture layer mapping |
| `reviewer` | Code review | Execution tracing, impact analysis |
| `explorer` | **Deep navigation** | **Find, trace, map code relationships** |
| `verification` | **Red team** | **Prove it works, try to break it** |

---

## Decisions

### 1. Architecture Pattern

**Pattern**: `CachedLayeredIndex` — Simple, pragmatic approach

```
┌─────────────────────────────────────────────────────────┐
│                    Explorer Agent                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ Entry Point │  │ Call Chain  │  │ Architecture    │  │
│  │ Finder      │  │ Tracer      │  │ Mapper          │  │
│  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘  │
│         │                │                  │           │
│         └────────────────┼──────────────────┘           │
│                          ▼                              │
│               ┌─────────────────────┐                    │
│               │   ExplorerService   │                    │
│               │  (orchestration)    │                    │
│               └──────────┬──────────┘                    │
└──────────────────────────┼──────────────────────────────┘
                           ▼
               ┌─────────────────────┐
               │   Cache Manager     │
               │  (Redis + SQLite)   │
               └──────────┬──────────┘
                          ▼
               ┌─────────────────────┐
               │   File Indexer      │
               │  (AST parsing)      │
               └─────────────────────┘
```

**Why not ADR-015 microservices?**
- ADR-015 proposes: Neo4j, Qdrant, Kafka, multiple ML services
- Reality: p9i is a lightweight MCP server, not an enterprise platform
- Decision: Use existing Redis + SQLite infrastructure (already available)

### 2. Explorer Agent Variants

Three variants based on complexity:

| Variant | Model | Use Case | Latency |
|---------|-------|----------|---------|
| **MVP** | haiku | Fast navigation, simple queries | ~500ms |
| **Extended** | inherit | Deep analysis, call graphs | ~2s (cache: ~50ms) |
| **Verification** | inherit | Red team verification | ~5s+ |

### 3. Cache Layer Design

#### Cache Types

| Cache | Storage | TTL | Invalidation |
|-------|---------|-----|--------------|
| File index | Redis | 24h | Manual/webhook |
| Symbol map | Redis | 1h | File change |
| Call graph | Redis | 24h | File change |
| Search results | Redis | 1h | File change |
| Session context | Redis | Session | Manual clear |

#### Cache Schema

```python
# explorer:index:{project_path} — File index metadata
# explorer:symbol:{project_path}:{name} — Symbol lookup
# explorer:graph:{project_path}:{entry} — Call graph
# explorer:search:{project_path}:{hash} — Search results
```

### 4. Explorer Tools (MCP)

| Tool | Description | Cache Behavior |
|------|-------------|----------------|
| `explorer_search` | Search using cached index | Cached (1h) |
| `explorer_index` | Rebuild project index | Fresh |
| `explorer_call_graph` | Get call graph for entry | Cached (24h) |
| `explorer_module_analysis` | Analyze module structure | Cached (1h) |

### 5. Forbidden Tools (All Variants)

| Tool | Reason |
|------|--------|
| AGENT_TOOL_NAME | No sub-agents |
| EXIT_PLAN_MODE_TOOL_NAME | Stay in read-only mode |
| FILE_EDIT_TOOL_NAME | No file modifications |
| FILE_WRITE_TOOL_NAME | No file creation |
| NOTEBOOK_EDIT_TOOL_NAME | No notebook edits |

---

## Implementation

### File Structure

```
prompts/agents/explorer/
├── promt-explorer-mvp.md          # MVP prompt (fast, simple)
├── promt-explorer-extended.md      # Extended with caching
└── promt-verification.md           # Verification (red team)

src/services/
├── explorer_service.py             # Main orchestration
├── explorer_cache.py              # Redis cache management
└── explorer_indexer.py            # AST-based file indexing

src/api/tools/
└── explorer_tools.py              # MCP tool wrappers
```

### ExplorerService API

```python
class ExplorerService:
    """Main service for code exploration."""

    async def ensure_index(self, force_refresh: bool = False) -> ProjectIndex
    async def search_symbol(self, name: str) -> Optional[SymbolResult]
    async def get_call_graph(self, entry: str, max_depth: int = 5) -> CallGraph
    async def analyze_module(self, module: str) -> ModuleAnalysis
    async def refresh_index(self) -> RefreshResult
    async def get_cache_stats(self) -> CacheStats
```

---

## Prompt Templates

### MVP (Fast Navigation)

**When to use**: "Find file", "Show structure", "Where is X?"

**Constraints**:
- Max 3 tool calls per query
- Max file size: 1000 lines
- Timeout: 30 seconds
- Model: haiku

### Extended (Deep Analysis)

**When to use**: "Trace calls", "Build graph", "Analyze dependencies"

**Constraints**:
- Max 5 tool calls per query
- Max file size: 5000 lines
- Timeout: 60 seconds
- Model: inherit

**Additional features**:
- Cache status reporting
- Impact analysis
- Architecture layer detection

### Verification (Red Team)

**When to use**: "Verify implementation", "Check it works", "Run tests"

**Constraints**:
- Must run actual commands
- Must produce PASS/FAIL/PARTIAL verdict
- Required: adversarial probes

**Output format**:
```
### Check: [what]
**Command run:** ...
**Output:** ...
**Result: PASS** | **FAIL** | **PARTIAL**

VERDICT: PASS
```

---

## P9iRouter Integration

### Keywords for Explorer

```python
# MVP keywords
"как работает": explorer
"структура": explorer
"связи": explorer
"зависимости": explorer
"где находится": explorer
"найди": explorer
"trace": explorer
"explore": explorer

# Extended keywords
"глубокий поиск": explorer
"проиндексируй": explorer
"call graph": explorer
"dependency graph": explorer
"impact analysis": explorer

# Verification keywords
"верифицируй": explorer
"проверь реализацию": explorer
"verify": explorer
```

### Keywords for Verification

```python
"проверь что": verification
"верифицируй": verification
"verify implementation": verification
"run tests": verification
```

---

## Comparison

| Aspect | Claude Code | p9i MVP | p9i Extended |
|--------|-------------|---------|--------------|
| Model | haiku | MiniMax-M2.7 | MiniMax-M2.7 |
| Tools | Glob, Grep, Read, LS | Glob, Grep, Read | + explorer_* tools |
| Routing | Built-in | P9iRouter | P9iRouter |
| READ-ONLY | Yes | Yes | Yes |
| Caching | None | Redis | Redis + SQLite |
| Latency | ~200ms | ~500ms | ~50ms (cache) |

---

## Consequences

### Positive
- Fast implementation (1-2 days MVP)
- No new infrastructure (uses existing Redis)
- Complements existing agents
- READ-ONLY enforcement prevents accidents
- Verification agent catches issues early

### Negative
- No persistence between sessions (MVP)
- Large codebases may timeout
- Complex call chains hard to trace (MVP)

### Risks
| Risk | Mitigation |
|------|------------|
| Stale cache | Webhook + manual refresh |
| Cache size growth | TTL + max size limits |
| Index rebuild time | Background jobs |

---

## Related ADRs

- [ADR-007: Multi-Agent Orchestrator](ADR-007-multi-agent-orchestrator.md)
- [ADR-014: LLM-based Prompt Selection](ADR-014-llm-prompt-selection.md)

---

## References

- [Claude Code exploreAgent.ts](https://github.com/perovskikh/claude-code-sourcemap/blob/main/restored-src/src/tools/AgentTool/built-in/exploreAgent.ts)
- [Claude Code verificationAgent.ts](https://github.com/perovskikh/claude-code-sourcemap/blob/main/restored-src/src/tools/AgentTool/built-in/verificationAgent.ts)
