# ADR-020: Coordinator Pattern & Project Volume Mounts

**Status**: Proposed

**Date**: 2026-04-02

**Authors**: Claude Code Analysis + p9i Team

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

| Agent | Claude Code Pattern | p9i Status |
|-------|---------------------|-------------|
| explorer | Code navigation | ✅ Implemented |
| reviewer | Verification | ✅ Implemented |
| architect | Research → Synthesis | ⚠️ Partial |
| developer | Implementation | ⚠️ Needs file access |
| designer | UI generation | ⚠️ Limited |
| devops | Infrastructure | ⚠️ Limited |

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

### Phase 1: Volume Mounts (1 day)
- [ ] Add volume mount to Helm values
- [ ] Update deployment configuration
- [ ] Test file access from agent

### Phase 2: Coordinator Pattern (2-3 days)
- [ ] Add `spawn_worker()` to orchestrator
- [ ] Add `continue_worker()` method
- [ ] Add task state tracking
- [ ] Update architect prompt for coordinator use

### Phase 3: Tool Permissions (1 day)
- [ ] Define permission sets
- [ ] Add permission check to executor
- [ ] Update prompts for read-only mode

---

## References

- Claude Code coordinatorMode.ts: Coordinator/worker pattern
- Claude Code BashTool: Command classification
- Claude Code tools.ts: 43 tools with permission system
- p9i ADR-018: Architect agent refactoring
- p9i ADR-019: Parallel research phase
