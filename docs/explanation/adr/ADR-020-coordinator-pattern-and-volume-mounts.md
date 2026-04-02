# ADR-020: Coordinator Pattern & Project Volume Mounts

**Status**: Partially Implemented (Phase 1 Complete)

**Date**: 2026-04-02

**Last Updated**: 2026-04-02 (Agent Architecture Analysis)

**Authors**: Claude Code Analysis + p9i Team

---

## Status Summary

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1: Volume Mounts** | ✅ COMPLETED | /project mount implemented |
| **Phase 2: Coordinator Pattern** | ❌ NOT IMPLEMENTED | spawn_worker/continue_worker pending |
| **Phase 3: Tool Permissions** | ❌ NOT IMPLEMENTED | ToolPermissions class pending |

---

## Context

After analyzing Claude Code source (coordinatorMode.ts, tools.ts, BashTool) and testing p9i agents, we've identified critical gaps:

### Problem 1: No Project File Access

Current state:
- Agent bash commands run in container without project files
- `ls: cannot access '/home/worker/p9i/': No such file or directory`
- Agents generate content but can't analyze actual code

### Problem 2: No Coordinator/Worker Pattern

Claude Code uses:
- **Coordinator** = supervisor spawning workers
- **Workers** = autonomous agents executing tasks
- Spawn via `AGENT_TOOL_NAME` tool
- Continue via `SEND_MESSAGE_TOOL_NAME`
- Parallel execution is core principle

p9i uses:
- AgentOrchestrator for routing
- Sequential agent execution
- No sub-agent spawning

### Problem 3: Missing Agent Alignment

**Updated based on Claude Code Sourcemap analysis (2026-04-02):**

| Agent | Claude Code Pattern | p9i Status | Gap |
|-------|---------------------|------------|-----|
| **explorer** | exploreAgent.ts (read-only) | ✅ Implemented (ADR-016) | Some MCP tools pending |
| **reviewer** | verificationAgent.ts | ✅ Implemented (ADR-017) | VERDICT format aligned |
| **architect** | planAgent.ts + coordinator | ✅ Implemented (ADR-018) | State machine pending |
| **developer** | generalPurposeAgent.ts | ⚠️ Partial | Routes to full_cycle |
| **designer** | - | ❌ Not agent | Uses MCP tools directly |
| **devops** | - | ❌ Not agent | Uses packs |
| **migration** | - | ✅ Implemented | Complete |
| **p9i (router)** | coordinatorMode.ts | ✅ Implemented | P9iRouter vs built-in |

### Problem 4: Critical Gaps from Agent Architecture Analysis

Based on comprehensive analysis of Claude Code source vs p9i implementation:

| Gap | Claude Code | p9i | Severity | Solution |
|-----|-------------|-----|----------|----------|
| **forkSubagent / spawn_worker** | forkSubagent.ts | - | HIGH | Phase 2 |
| **Tool Permission System** | disallowedTools in tools.ts | - | HIGH | Phase 3 |
| **Model Tiering (haiku/inherit)** | Model selection per agent | Fixed MiniMax | MEDIUM | Future |
| **Abort Controller** | AbortController | - | MEDIUM | Future |

---

## Decision

### 1. Add Project Volume Mount

Add to `helm/p9i/values.yaml`:

```yaml
extraVolumes:
  - name: project
    hostPath:
      path: /home/worker/p9i
      type: Directory

extraVolumeMounts:
  - name: project
    mountPath: /project
    readOnly: true  # Read-only for safety
```

For K3s, use `persistentVolumeClaim` or `hostPath` based on setup.

### 2. Implement Coordinator Pattern (Future)

Add coordinator mode to AgentOrchestrator:

```python
async def spawn_worker(
    self,
    task: str,
    description: str,
    subagent_type: str = "worker"
) -> str:
    """Spawn a worker agent, return task_id."""
    task_id = generate_task_id()
    # Store worker context
    self._workers[task_id] = {
        "description": description,
        "task": task,
        "status": "running"
    }
    # Execute worker asynchronously
    asyncio.create_task(
        self.execute_agent(subagent_type, task)
    )
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
    # Continue execution with new message
    ...
```

### 3. Add Tool Permission System

```python
class ToolPermissions:
    READ_ONLY = {"Glob", "Grep", "Read", "BashOutput"}
    READ_WRITE = READ_ONLY | {"Write", "Edit", "Bash"}
    ADMIN = READ_WRITE | {"Agent", "Task"}

async def execute_with_permissions(
    tools: set[str],
    permissions: ToolPermissions
) -> bool:
    """Check if tools are allowed for current mode."""
    return tools.issubset(permissions)
```

---

## Consequences

### Positive

- Agents can analyze actual project code
- Parallel worker execution
- Proper coordinator pattern like Claude Code
- Tool permission system for safety

### Negative

- Security considerations for volume mounts
- More complex orchestration
- Additional infrastructure configuration

---

## Implementation Plan

### Phase 1: Volume Mounts (COMPLETED ✅)
- [x] Add volume mount to Helm values (`projectPath: /home/worker/p9i`)
- [x] Update deployment configuration (deployment.yaml lines 106-114)
- [x] Docker Compose volume mounts (`./src:/app/src`, `./prompts:/app/prompts`, `./memory:/app/memory`)
- [x] Test file access from agent — verified working

**Verification:** Volume mounts confirmed in:
- `/home/worker/p9i/helm/p9i/values.yaml` line 14
- `/home/worker/p9i/helm/p9i/templates/deployment.yaml` lines 106-114
- `/home/worker/p9i/docker-compose.yml` lines 43-48

### Phase 2: Coordinator Pattern (NOT IMPLEMENTED)
- [ ] Add `spawn_worker()` to orchestrator
- [ ] Add `continue_worker()` method
- [ ] Add task state tracking (`_workers` dict)
- [ ] Update architect prompt for coordinator use
- [ ] Align with Claude Code `forkSubagent.ts` pattern

**Reference:** Claude Code uses `coordinatorMode.ts` → `workerAgent.ts` → `getCoordinatorAgents()`

### Phase 3: Tool Permissions (NOT IMPLEMENTED)
- [ ] Define permission sets (READ_ONLY, READ_WRITE, ADMIN)
- [ ] Add permission check to executor
- [ ] Update prompts for read-only mode (explorer, reviewer)
- [ ] Implement `disallowedTools` enforcement

**Reference:** Claude Code `tools.ts` has 43 tools with explicit disallowedTools arrays

### Phase 4: Model Tiering (FUTURE)
- [ ] Add haiku model for fast agents (explorer, reviewer)
- [ ] Add inherit model for complex agents (architect, developer)
- [ ] Update P9iRouter to support model selection per agent

---

## References

- Claude Code coordinatorMode.ts: Coordinator/worker pattern
- Claude Code BashTool: Command classification
- Claude Code tools.ts: 43 tools with permission system
- Claude Code forkSubagent.ts: Worker spawning pattern
- p9i ADR-018: Architect agent refactoring
- p9i ADR-019: Parallel research phase
- [Agent Architecture Implementation Status](../../how-to/agent-architecture-implementation-status.md)
