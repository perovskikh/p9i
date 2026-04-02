# p9i Agent Architecture: Implementation vs Claude Code Source

> **Status:** Research Complete
> **Date:** 2026-04-02
> **Source:** Claude Code Sourcemap (`perovskikh/claude-code-sourcemap`), p9i ADR documents

---

## Executive Summary

Анализ исходного кода Claude Code и ADR документов p9i показывает **высокую степень выравнивания** архитектуры агентов. p9i успешно реализовал основные паттерны из Claude Code с собственным twist — keyword-based routing вместо built-in классификации.

### Ключевые выводы:

| Категория | Claude Code | p9i | Статус |
|-----------|-------------|-----|--------|
| Explorer Agent | exploreAgent.ts | promt-explorer-*.md | ✅ Реализован |
| Verification Agent | verificationAgent.ts | promt-verification.md | ✅ Реализован |
| Plan/Architect Agent | planAgent.ts | promt-architect-*.md | ✅ Реализован |
| Coordinator Pattern | coordinatorMode.ts | AgentOrchestrator | ⚠️ Частично |
| Worker Spawning | forkSubagent.ts | - | ❌ Не реализован |
| Tool Permissions | built-in в tools.ts | ADR-020 Phase 3 | ⚠️ Запланирован |
| Volume Mounts | - | /project | ✅ Реализован |

---

## Part 1: Claude Code Agents Analysis

### 1.1 Built-in Agents (`/restored-src/src/tools/AgentTool/built-in/`)

| Агент | Файл | Назначение | Инструменты | Ключевые ограничения |
|-------|------|------------|-------------|---------------------|
| **generalPurposeAgent** | `generalPurposeAgent.ts` | Универсальный исследователь | `*` (все) | Нет ограничений |
| **planAgent** | `planAgent.ts` | Архитектор/планировщик | glob, grep, read | **READ-ONLY**, omit CLAUDE.md |
| **exploreAgent** | `exploreAgent.ts` | Навигация по коду | glob, grep, read, bashOutput | **READ-ONLY**, parallel calls |
| **verificationAgent** | `verificationAgent.ts` | Верификация/редтиминг | bash (run commands) | Must run actual commands |
| **claudeCodeGuideAgent** | `claudeCodeGuideAgent.ts` | Гид по Claude Code | - | - |
| **statuslineSetupAgent** | `statuslineSetup.ts` | Статусная строка | - | - |

### 1.2 Task Types (`/restored-src/src/tasks/`)

| Тип | Файл | Описание |
|-----|------|----------|
| **LocalAgentTask** | `LocalAgentTask/LocalAgentTask.tsx` | Локальный фоновый агент |
| **RemoteAgentTask** | `RemoteAgentTask/RemoteAgentTask.tsx` | Удалённый агент |
| **InProcessTeammateTask** | `InProcessTeammateTask/InProcessTeammateTask.tsx` | In-process teammate |
| **DreamTask** | `DreamTask/DreamTask.ts` | Консолидация памяти |
| **LocalShellTask** | - | Локальная bash задача |

### 1.3 Coordinator Pattern (`coordinatorMode.ts`)

```
User Request → Coordinator → Worker 1 (Research) → Worker 2 (Synthesis)
                                            ↓
              Worker 3 (Implementation) ←→ Worker 4 (Verification)
```

**Key features:**
- Spawn workers via `AGENT_TOOL_NAME`
- Continue via `SEND_MESSAGE_TOOL_NAME`
- Parallel execution core principle

---

## Part 2: p9i Agent Implementation Status

### 2.1 Prompts Directory Structure

```
prompts/agents/
├── architect/     # 6 files: design, parallel-research, create_adr, 3x explorer
├── designer/      # Empty (использует MCP tools напрямую)
├── developer/     # 1 file: promt-feature-add.md
├── explorer/      # 3 files: mvp, extended, verification
├── migration/     # 6 files: planner, implementation, review, devops, etc.
└── reviewer/      # 4 files: mvp, enhanced, security, verification
```

### 2.2 Agent Implementation Matrix

| Агент | Claude Code Source | p9i Prompts | MCP Tools | Status | ADR |
|-------|-------------------|------------|-----------|--------|-----|
| **explorer** | exploreAgent.ts | 3 файла | explorer_search, whereis, index, call_graph | ✅ Implemented | ADR-016 |
| **reviewer** | verificationAgent.ts | 4 файла | reviewer_diff, search, security, quality, verify, metrics | ✅ Implemented | ADR-017 |
| **architect** | planAgent.ts | 6 файлов | architect_parallel_research | ✅ Implemented | ADR-018 |
| **developer** | generalPurposeAgent.ts | 1 файл | - | ⚠️ Partial | - |
| **designer** | - | - | generate_tailwind, generate_shadcn, generate_textual | ❌ Not agent | - |
| **devops** | - | - | promt-ci-cd-pipeline (packs) | ❌ Not agent | - |
| **migration** | - | 6 файлов | - | ✅ Implemented | - |
| **p9i (router)** | coordinatorMode.ts | - | p9i (main tool) | ✅ Implemented | ADR-007 |

### 2.3 Implemented Components

#### Explorer (ADR-016)
- ✅ `promt-explorer-mvp.md` — Fast navigation (haiku, 3 tool calls)
- ✅ `promt-explorer-extended.md` — Deep analysis (caching)
- ✅ `promt-verification.md` — Red team (VERDICT format)
- ✅ `src/services/explorer_service.py`
- ✅ `src/services/explorer_cache.py`
- ✅ `src/services/explorer_indexer.py`
- ✅ `src/api/tools/explorer_tools.py`

#### Reviewer (ADR-017)
- ✅ `promt-reviewer-mvp.md`
- ✅ `promt-reviewer-enhanced.md`
- ✅ `promt-reviewer-security.md`
- ✅ `promt-verification.md`
- ✅ `src/services/reviewer_cache.py`
- ✅ `src/api/tools/reviewer_tools.py`
- ⚠️ Sequential (not parallel) — correctly rejected

#### Architect (ADR-018)
- ✅ `promt-architect-design.md`
- ✅ `promt-architect-parallel-research.md`
- ✅ `create_adr.md`
- ✅ `explorer-1-tech-stack.md`
- ✅ `explorer-2-code-patterns.md`
- ✅ `explorer-3-best-practices.md`
- ⚠️ AgentTaskState/AgentProgress pending

---

## Part 3: Gap Analysis

### 3.1 High Priority Gaps

| Gap | Claude Code | p9i | Severity | Solution |
|-----|-------------|-----|----------|----------|
| **forkSubagent / spawn_worker** | forkSubagent.ts | - | HIGH | ADR-020 Phase 2 |
| **Tool Permission System** | tools.ts disallowedTools | - | HIGH | ADR-020 Phase 3 |
| **Coordinator Pattern** | coordinatorMode.ts | AgentOrchestrator | MEDIUM | ADR-020 Phase 2 |
| **Read-Only Enforcement** | explicit disallowedTools | маркированы | MEDIUM | ToolPermissions |

### 3.2 Medium Priority Gaps

| Gap | Claude Code | p9i | Severity |
|-----|-------------|-----|----------|
| **Model Tiering** | haiku/inherit | MiniMax-M2.7 fixed | MEDIUM |
| **Abort Controller** | AbortController | - | MEDIUM |
| **Scratchpad for Workers** | Worker output | - | LOW |

### 3.3 Not Applicable Gaps

| Claude Code Pattern | p9i Approach | Notes |
|--------------------|---------------|-------|
| forkSubagent.ts | P9iRouter | Keyword routing instead |
| TypeScript built-in agents | Python prompts | Different stack |
| In-process teammates | MCP HTTP/stdio | Different architecture |

---

## Part 4: Architecture Comparison

### 4.1 Routing Patterns

| Aspect | Claude Code | p9i |
|--------|-------------|-----|
| **Method** | Built-in classification | P9iRouter (keyword) |
| **Priority** | Agent type → tools | IntentType priority cascade |
| **LLM Usage** | Optional | NO (keyword-based = free) |
| **Speed** | ~200ms | ~50ms (cached) |

### 4.2 Tool Permission System

**Claude Code (tools.ts):**
```typescript
disallowedTools: ["AGENT_TOOL_NAME", "FILE_EDIT_TOOL_NAME", ...]
```

**p9i (ADR-020 proposed):**
```python
class ToolPermissions:
    READ_ONLY = {"Glob", "Grep", "Read", "BashOutput"}
    READ_WRITE = READ_ONLY | {"Write", "Edit", "Bash"}
    ADMIN = READ_WRITE | {"Agent", "Task"}
```

### 4.3 Agent Definition Format

**Claude Code:**
```typescript
type AgentDefinition = {
  agentType: string
  whenToUse: string
  tools: string[] | '*'
  disallowedTools?: string[]
  getSystemPrompt: () => string
}
```

**p9i:**
```python
AGENT_KEYWORDS = {
    "explorer": ["как работает", "структура", ...],
    "reviewer": ["проверь", "ревью", ...],
}
```

---

## Part 5: Refactoring Recommendations

### 5.1 Phase 1: Coordinator Pattern (ADR-020 Phase 2)

**Add to AgentOrchestrator:**

```python
async def spawn_worker(
    self,
    task: str,
    description: str,
    subagent_type: str = "worker"
) -> str:
    """Spawn a worker agent, return task_id."""
    task_id = generate_task_id()
    self._workers[task_id] = {
        "description": description,
        "task": task,
        "status": "running"
    }
    asyncio.create_task(self.execute_agent(subagent_type, task))
    return task_id

async def continue_worker(
    self,
    task_id: str,
    message: str
) -> dict:
    """Continue a worker with new instructions."""
    worker = self._workers.get(task_id)
    if not worker:
        return {"error": "Worker not found"}
    ...
```

### 5.2 Phase 2: Tool Permission System (ADR-020 Phase 3)

**Add to agent_router.py:**

```python
class ToolPermissions:
    READ_ONLY = {"Glob", "Grep", "Read", "BashOutput"}
    READ_WRITE = READ_ONLY | {"Write", "Edit", "Bash"}
    ADMIN = READ_WRITE | {"Agent", "Task"}

async def execute_with_permissions(
    tools: set[str],
    permissions: ToolPermissions
) -> bool:
    return tools.issubset(permissions)
```

### 5.3 Phase 3: Architect State Machine (ADR-018)

**Add dataclasses:**

```python
@dataclass
class AgentTaskState:
    task_id: str
    status: TaskStatus
    progress: Optional[AgentProgress]
    tool_activity: List[ToolActivity]

@dataclass
class AgentProgress:
    token_count: int
    tool_use_count: int
    summary: str
```

### 5.4 Phase 4: Model Tiering

**Add to agent_router.py:**

```python
AGENT_MODEL_TIER = {
    "explorer": "haiku",      # Fast, read-only
    "reviewer": "haiku",      # Fast verification
    "architect": "inherit",   # Complex analysis
    "developer": "inherit",    # Full generation
}
```

---

## Part 6: Verification Matrix

### Claude Code → p9i Alignment

| Claude Code Feature | p9i Implementation | Verified |
|--------------------|---------------------|----------|
| **exploreAgent** (read-only) | explorer agent + tools | ✅ |
| **verificationAgent** (VERDICT) | promt-verification.md | ✅ |
| **planAgent** (read-only) | architect agent | ✅ |
| **generalPurposeAgent** (all tools) | developer/full_cycle | ✅ |
| **Coordinator workers** | AgentOrchestrator | ⚠️ Partial |
| **Parallel execution** | execute_parallel_agents() | ✅ |
| **Redis caching** | explorer_cache.py | ✅ |
| **Volume mounts** | /project mount | ✅ |
| **Tool restrictions** | - | ❌ |
| **forkSubagent** | - | ❌ |

---

## Part 7: ADR Implementation Status

| ADR | Status | Agents | Implementation |
|-----|--------|--------|----------------|
| **ADR-007** | ✅ Implemented | 7 agents | Multi-agent orchestrator |
| **ADR-014** | 🔄 Partial | routing | HybridRouter ✅, Embeddings ❌ |
| **ADR-016** | ✅ Accepted | explorer | MVP/Extended/Verification |
| **ADR-017** | ⚠️ Proposed | reviewer | 4 variants, sequential |
| **ADR-018** | ⚠️ Proposed | architect | Prompts done, state machine pending |
| **ADR-019** | ⚠️ Proposed | architect | Parallel research, true parallel pending |
| **ADR-020** | 🔄 Phase 1 | all | Volume mounts ✅, Coordinator pending |

### ADR-014 Details: LLM-based Prompt Selection

| Component | Status | Notes |
|-----------|--------|-------|
| HybridPromptRouter | ✅ | Rule → Semantic → LLM cascade |
| SemanticRouter | ✅ | Cosine similarity |
| PromptRegistry | ✅ | Prompt entry management |
| DefaultEmbedder | ⚠️ | Hash-based fallback (NOT OpenRouter) |
| OpenRouter bge-m3 | ❌ | Not implemented |
| Qdrant Vector Store | ❌ | Not implemented |
| Redis Embedding Cache | ❌ | Not implemented |

---

## Conclusion

p9i имеет **сильную базу** агентов вдохновлённых Claude Code. Основные реализации завершены:

1. ✅ **Explorer** — полностью соответствует Claude Code
2. ✅ **Reviewer** — VERDICT формат, adversarial testing
3. ✅ **Architect** — parallel research phase
4. ⚠️ **Coordinator Pattern** — нужен spawn_worker()
5. ❌ **Tool Permissions** — нужен ToolPermissions class
6. ❌ **forkSubagent** — нет эквивалента

**Next Steps:**
1. Реализовать ADR-020 Phase 2 (Coordinator Pattern)
2. Реализовать ADR-020 Phase 3 (Tool Permissions)
3. Добавить Model Tiering для haiku/inherit

---

## Related Documents

- [Claude Code Sourcemap Agents](./claude-code-sourcemap-agents.md)
- [Agent Interaction After ADR-15](./agent-interaction-after-adr15.md)
- [ADR-016: Code Explorer Agent](../explanation/adr/ADR-016-code-explorer-agent.md)
- [ADR-017: Reviewer Agent Refactor](../explanation/adr/ADR-017-reviewer-agent-refactor.md)
- [ADR-018: Architect Agent Refactoring](../explanation/adr/ADR-018-architect-agent-refactoring.md)
- [ADR-020: Coordinator Pattern & Volume Mounts](../explanation/adr/ADR-020-coordinator-pattern-and-volume-mounts.md)