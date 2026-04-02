# ADR-016b: Code Explorer Agent — Extended (1-2 Weeks)

## Status
**Proposed** | 2026-04-02

## Context

### Problem Statement

MVP explorer agent (ADR-016a) provides basic navigation but lacks:
- **Persistence**: Index is rebuilt every session
- **Performance**: Large codebases require full scan each time
- **Deep analysis**: Cannot track cross-module dependencies

### What This ADR Adds Over MVP

| Feature | MVP | Extended |
|---------|-----|----------|
| Index persistence | ❌ | ✅ SQLite/Redis cache |
| Incremental updates | ❌ | ✅ Webhook-based invalidation |
| Cross-module analysis | ❌ | ✅ Import graph |
| Performance | ~500ms/query | ~50ms/cache hit |
| Session memory | ❌ | ✅ Exploration context |

---

## Decisions

### 1. Architecture Pattern

**Pattern**: `CachedLayeredIndex`

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
│               │   Cache Manager     │                   │
│               │  (Redis + SQLite)   │                   │
│               └──────────┬──────────┘                    │
└──────────────────────────┼──────────────────────────────┘
                           ▼
               ┌─────────────────────┐
               │   File Index        │
               │  (symbols, imports) │
               └─────────────────────┘
```

### 2. Cache Layer Design

#### 2.1 Cache Types

| Cache | Storage | TTL | Invalidation |
|-------|---------|-----|--------------|
| File index | SQLite | 24h | Manual/webhook |
| Grep results | Redis | 1h | File change |
| Symbol map | SQLite | 24h | File change |
| Session context | Redis | Session | Manual clear |

#### 2.2 Cache Schema

```sql
-- File index cache
CREATE TABLE file_index (
    project_path TEXT PRIMARY KEY,
    files_json TEXT,           -- JSON array of {path, size, mtime}
    symbols_json TEXT,         -- JSON array of {file, symbols[]}
    last_indexed TIMESTAMP,
    index_version INTEGER
);

-- Symbol cache (function/class definitions)
CREATE TABLE symbols (
    file_path TEXT,
    symbol_name TEXT,
    symbol_type TEXT,          -- 'function', 'class', 'const'
    line_number INTEGER,
    PRIMARY KEY (file_path, symbol_name)
);

-- Import graph
CREATE TABLE imports (
    from_file TEXT,
    to_module TEXT,
    import_type TEXT,          -- 'import', 'from', 'require'
    PRIMARY KEY (from_file, to_module)
);
```

#### 2.3 Cache Invalidation

```python
# Webhook handler for git push
async def invalidate_cache(project_path: str, changed_files: List[str]):
    """Invalidate cache for changed files."""
    for file in changed_files:
        # Delete symbol entries for this file
        await db.execute(
            "DELETE FROM symbols WHERE file_path LIKE ?",
            (f"{file}%",)
        )
        # Mark index for refresh
        await redis.sadd("index:stale", file)

    # Schedule background reindex
    await redis.enqueue("explorer:reindex", project_path)
```

---

### 3. Explorer Agent Prompt (Extended)

**File**: `prompts/agents/explorer/promt-explorer-extended.md`

**Key Features:**
- **Model**: haiku (fast) or inherit (complex analysis)
- **READ-ONLY MODE**: Strict prohibition on file modifications
- **Forbidden Tools**: Same as MVP + cache management

```markdown
=== CRITICAL: READ-ONLY MODE - NO FILE MODIFICATIONS ===

This is a READ-ONLY exploration task. You are STRICTLY PROHIBITED from:
- Creating new files (no Write, touch, or file creation of any kind)
- Modifying existing files (no Edit operations)
- Deleting files (no rm or deletion)
- Moving or copying files (no mv or cp)
- Using redirect operators (>, >>, |) or heredocs to write to files
- Running ANY commands that change system state

Your role is EXCLUSIVELY to search and analyze existing code.
```

### Enhanced Tool Usage

| Tool | Use Case | Cache |
|------|----------|-------|
| Glob | Find files by pattern | Indexed |
| Grep | Search code content | Cached results |
| Read | Read file content | Fresh (small files) |
| BashOutput | Read-only shell | N/A |
| **CacheLookup** | Get indexed symbols | **Primary** |

### Cache Management

1. **Freshness Check**
   ```
   IF cache_valid(file, mtime) THEN
       RETURN cached_result
   ELSE
       result = scan_file(file)
       UPDATE cache
       RETURN result
   ```

2. **Index Rebuild Triggers**
   - Manual: "rebuild index"
   - Webhook: git push с изменениями
   - TTL expiry: 24 hours

3. **Exploration Context**
   ```
   Session contains:
   - Last explored files (navigation history)
   - Current focus (active module)
   - Open questions (unresolved finds)
   ```

### Enhanced Exploration Patterns

1. **Deep Entry Point Discovery**
   - Scan for main files, routes, handlers
   - Build entry point graph
   - Mark critical paths

2. **Cross-Module Call Chains**
   - Follow imports across files
   - Build complete call graph
   - Detect cycles (report them)

3. **Architecture Layer Mapping**
   - Detect domain boundaries
   - Map module dependencies
   - Identify shared/core modules

### Output Format (Enhanced)

```markdown
## 📍 Entry Points
| File | Line | Type | Critical Path |
|------|------|------|---------------|
| `main.py:12` | CLI | Yes → |

## 🔗 Call Graph (Depth: 3)
```
main.py::main()
  └─→ app.py::create_app()
       ├─→ routes.py::setup_routes()
       │    └─→ auth.py::init_middleware()
       └─→ db.py::connect()
```

## 📊 Architecture Layers
```
src/
├── api/          # Routes, middleware
├── services/     # Business logic
├── models/        # Data layer
└── core/         # Shared utilities (→ all layers)
```

## 💾 Cache Status
- Index: Fresh (2 hours ago)
- 127 files indexed
- 1,456 symbols cached
```

### Constraints
- Max 5 tool calls per query (cache-optimized)
- Max file size: 5000 lines (summarize larger)
- Timeout: 60 seconds (allows deep analysis)
- Cache hit: <50ms response
```

---

### 4. P9iRouter Integration (Extended)

**Extended Keywords** (in addition to MVP):

```python
# === EXPLORER EXTENDED ===
"deep search": (IntentType.AGENT_TASK, "explorer"),
"глубокий поиск": (IntentType.AGENT_TASK, "explorer"),
"проиндексируй": (IntentType.AGENT_TASK, "explorer"),
"переиндексируй": (IntentType.AGENT_TASK, "explorer"),
"reindex": (IntentType.AGENT_TASK, "explorer"),
"refresh index": (IntentType.AGENT_TASK, "explorer"),
"построить граф": (IntentType.AGENT_TASK, "explorer"),
"call graph": (IntentType.AGENT_TASK, "explorer"),
"dependency graph": (IntentType.AGENT_TASK, "explorer"),
"impact analysis": (IntentType.AGENT_TASK, "explorer"),
"анализ связей": (IntentType.AGENT_TASK, "explorer"),
"что зависит от": (IntentType.AGENT_TASK, "explorer"),
"затронет": (IntentType.AGENT_TASK, "explorer"),
```

---

### 5. Service Components

#### 5.1 ExplorerService

```python
class ExplorerService:
    """Main service for code exploration."""

    def __init__(self, cache: CacheManager):
        self.cache = cache
        self.indexer = FileIndexer()
        self.graph_builder = CallGraphBuilder()

    async def find_entry_points(self, project_path: str) -> List[EntryPoint]:
        """Find all entry points in project."""
        # Check cache first
        cached = await self.cache.get("entry_points", project_path)
        if cached:
            return cached

        # Build index
        files = await self.indexer.scan(project_path)
        entry_points = []
        for file in files:
            eps = await self._find_eps_in_file(file)
            entry_points.extend(eps)

        # Cache result
        await self.cache.set("entry_points", project_path, entry_points)
        return entry_points

    async def build_call_graph(self, start_file: str, max_depth: int = 5):
        """Build call graph from entry point."""
        # Uses cache for symbol lookups
        # Builds graph incrementally
        pass
```

#### 5.2 CacheManager

```python
class CacheManager:
    """Manages exploration cache with Redis + SQLite."""

    async def get(self, key: str, project: str) -> Optional[Any]:
        """Get cached result (Redis primary, SQLite backup)."""
        redis_key = f"explorer:{project}:{key}"
        cached = await self.redis.get(redis_key)
        if cached:
            return json.loads(cached)

        # Fallback to SQLite
        row = await self.db.fetchone(
            "SELECT result_json FROM cache WHERE key = ? AND project = ?",
            (key, project)
        )
        if row:
            return json.loads(row["result_json"])
        return None

    async def set(self, key: str, project: str, value: Any, ttl: int = 3600):
        """Set cached result (Redis + SQLite)."""
        redis_key = f"explorer:{project}:{key}"
        await self.redis.setex(redis_key, ttl, json.dumps(value))

        # SQLite backup
        await self.db.execute(
            "INSERT OR REPLACE INTO cache (key, project, result_json, updated_at) VALUES (?, ?, ?, ?)",
            (key, project, json.dumps(value), datetime.now())
        )
```

#### 5.3 FileIndexer

```python
class FileIndexer:
    """Indexes project files for fast exploration."""

    async def scan(self, project_path: str) -> List[FileInfo]:
        """Scan project and build file index."""
        files = []
        async for entry in self._walk(project_path):
            if entry.is_file() and self._should_index(entry):
                files.append(FileInfo(
                    path=entry.path,
                    size=entry.size,
                    mtime=entry.mtime,
                    symbols=await self._extract_symbols(entry)
                ))
        return files

    async def _extract_symbols(self, file: FileInfo) -> List[Symbol]:
        """Extract function/class definitions."""
        # Uses AST parsing for Python, tree-sitter for JS/TS
        pass
```

---

### 6. Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| File Index | SQLite | Persistent symbol storage |
| Query Cache | Redis | Fast result retrieval |
| Background Jobs | Redis Queue | Index rebuilds |
| Locking | Redis | Concurrent access |

---

## Implementation Plan

### Week 1: Cache Architecture

| Day | Task | Deliverable |
|-----|------|-------------|
| 1-2 | SQLite schema + FileIndexer | Basic indexing works |
| 3 | Redis cache layer | Cache get/set/invalidate |
| 4 | Integration with explorer prompt | Cache-aware exploration |
| 5 | Webhook handler | Git push invalidation |

### Week 2: Performance & Polish

| Day | Task | Deliverable |
|-----|------|-------------|
| 6 | Call graph builder | Cross-module analysis |
| 7 | Response format refinement | Enhanced output |
| 8 | Performance testing | Benchmark against MVP |
| 9 | Edge case handling | Large files, binary, errors |
| 10 | Documentation + examples | Usage guide |

---

## Comparison: MVP vs Extended

| Aspect | ADR-016a MVP | ADR-016b Extended |
|--------|--------------|-------------------|
| Implementation | 1-2 days | 1-2 weeks |
| Index storage | None | SQLite + Redis |
| Avg query latency | ~500ms | ~50ms (cache hit) |
| Large codebase support | Poor | Good |
| Cross-module analysis | Limited | Full call graph |
| Session persistence | None | Full context |
| Infrastructure | None | SQLite + Redis |

---

## Consequences

### Positive
- Fast repeated queries (cache hit)
- Large codebase support
- Cross-module understanding
- Persistent exploration context

### Negative
- More complex infrastructure
- Cache invalidation challenges
- Additional dependencies (SQLite, Redis)

### Risks
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Stale cache | Medium | Webhook + manual refresh |
| Cache size growth | Medium | TTL + max size limits |
| Index rebuild time | Low | Background jobs |

---

## Related ADRs

- [ADR-016a: Explorer Agent — MVP](ADR-016a-explorer-agent-mvp.md)
- [ADR-007: Multi-Agent Orchestrator](ADR-007-multi-agent-orchestrator.md)

---

## References

- [Claude Code code-explorer agent](https://github.com/anthropics/claude-code/blob/main/plugins/feature-dev/agents/code-explorer.md)
- [SQLite](https://sqlite.org/) — Embedded database
- [Redis](https://redis.io/) — Cache layer
