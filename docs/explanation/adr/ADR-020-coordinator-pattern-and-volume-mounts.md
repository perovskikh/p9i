# ADR-020: Coordinator Pattern & Project Volume Mounts

**Status**: Phase 2 Complete ✅

**Date**: 2026-04-02

**Last Updated**: 2026-04-05 (4-phase workflow implemented)

**Authors**: Claude Code Analysis + p9i Team

---

## Status Summary

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1: Volume Mounts** | ✅ COMPLETED | /project mount implemented |
| **Phase 2: Coordinator Pattern** | ✅ COMPLETED | 4-phase workflow + worker lifecycle |
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

### Phase 2: Coordinator Pattern (COMPLETED ✅)

**Implemented: 4-Phase Workflow Graph**

```
graph TD
    A[Фаза 1: Исследование] -->|Отчёты| B[Фаза 2: Синтез]
    B -->|Спецификация| C[Фаза 3: Реализация]
    C -->|Изменения + Коммиты| D[Фаза 4: Верификация]
    D -- Успех --> E[Задача завершена]
    D -- Ошибки --> C
```

**Components Added:**

| Component | File | Description |
|-----------|------|-------------|
| `PhaseStatus` | orchestrator.py | Enum: PENDING, IN_PROGRESS, COMPLETED, FAILED |
| `TaskPhase` | orchestrator.py | Single phase state |
| `WorkflowTask` | orchestrator.py | 4-phase task tracking |
| `create_workflow()` | orchestrator.py | Create workflow with 4 phases |
| `execute_workflow()` | orchestrator.py | Execute with auto-retry on Implementation |

**Implementation:**

```python
# orchestrator.py
class PhaseStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class WorkflowTask:
    task_id: str
    name: str
    target: str
    phases: List[TaskPhase]  # [Research, Synthesis, Implementation, Verification]
    status: str  # pending, in_progress, completed, failed

async def create_workflow(name, target, project_path) -> Dict
async def execute_workflow(workflow_id, auto_continue=True) -> Dict
```

**Phase Transitions:**

| Phase | Agent | Auto-Retry | Output |
|-------|-------|------------|--------|
| 1. Research | explorer | No | Tech Stack + Patterns + Quality reports |
| 2. Synthesis | architect | No | Architectural specification |
| 3. Implementation | developer | **Yes** (1 retry) | Code changes + commits |
| 4. Verification | reviewer | No | Verification report (VERDICT) |

### Enhanced Multi-Agent Design (Feedback Loop)

**Полный цикл взаимодействия Координатора и Рабочих агентов:**

```
                          ┌─────────────────────┐
                          │     Координатор     │
                          └──────────▲──────────┘
                                     │
                                     │
┌─────────────────────┐           ┌─────────────────────┐
│   Исследование      │──────────▶│      Синтез        │
│   (Рабочие агенты)  │           │   (Координатор)     │
│                     │           │                     │
│ • Изучить кодовую   │           │ • Прочитать         │
│   базу              │           │   результаты        │
│ • Найти файлы       │           │ • Осмыслить проблему │
│ • Понять проблему   │           │ • Составить         │
│   (параллельно)     │           │   спецификации      │
└──────────┬──────────┘           └──────────▲──────────┘
           │                                 │
           │                                 │
           │  Обратная связь                 │  Спецификации
           │                                 │
           ▼                                 ▼
┌─────────────────────┐           ┌─────────────────────┐
│   Верификация       │◀──────────│    Реализация       │
│   (Рабочие агенты)  │           │   (Рабочие агенты)  │
│                     │           │                     │
│ • Проверить, что    │           │ • Внести целевые    │
│   изменения         │           │   изменения         │
│   работают          │           │ • Закоммитить       │
│                     │           │                     │
└─────────────────────┘           └─────────────────────┘

                          ↑───────────────────────────────↑
                               Коммит кода → новая итерация
```

**Ключевые особенности:**

| Компонент | Роль | Поведение |
|-----------|------|-----------|
| **Координатор** | Синтез | Только Synthesis - "осмыслить проблему, составить спецификации" |
| **Рабочие агенты** | Research, Implementation, Verification | Параллельное выполнение в каждой фазе |
| **Обратная связь** | Verification → Research | Если верификация неуспешна → новый цикл исследование |

**Итеративный цикл:**

```
Research → Synthesis → Implementation → Verification
    ↑                                        │
    └────────────── Новый цикл ──────────────┘
```

**Реализация в коде:**

```python
# Feedback loop в execute_workflow()
if phase.name == "verification" and phase.status == FAILED and auto_continue:
    # Вернуться к Research для нового цикла
    logger.warning(f"Workflow {workflow_id}: Verification failed, starting new iteration...")
    # Reset phases for new iteration
    for p in workflow.phases:
        p.status = PhaseStatus.PENDING
        p.output = ""
        p.error = ""
    workflow.current_phase = 0  # Back to Research
    workflow.phase_iteration += 1
    continue  # Начать новую итерацию
```

**Параметры:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `auto_continue` | True | Если True - включает feedback loop |
| `max_iterations` | 3 | Максимум циклов Research→Verification |

**Reference:** Claude Code `coordinatorMode.ts` → 4-phase workflow pattern

### Integration with Context7, GitHub, Claude Cookbooks

**Complete Architecture with External Integrations:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MULTI-AGENT COORDINATOR + INTEGRATIONS                 │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │     Координатор     │
                    └──────────▲──────────┘
                               │
    ┌─────────────────────┐    │    ┌─────────────────────┐
    │   Исследование      │────┼───▶│      Синтез        │
    │   (Рабочие агенты)  │    │    │   (Координатор)     │
    │                      │    │    │                      │
    │ • Context7 ─────────┼────┘    │ • GitHub Issues     │
    │ • GitHub Repos      │         │ • Claude Cookbooks  │
    │ • Claude Cookbooks  │         │   Swarm Pattern     │
    └──────────┬──────────┘         └──────────▲──────────┘
               │                                 │
               │                                 │
               ▼                                 ▼
┌─────────────────────┐           ┌─────────────────────┐
│   Верификация       │◀──────────│    Реализация       │
│   (Рабочие агенты)  │           │   (Рабочие агенты)  │
│                      │           │                      │
│ • GitHub CI Check    │           │ • GitHub PR         │
│ • Context7 Verify   │           │ • Claude Cookbooks  │
│ • Claude Cookbooks  │           │   Implementation    │
└─────────────────────┘           └─────────────────────┘
```

#### Context7 Integration

**Usage Point: Research Phase (Step 1)**

| Context7 Lookup | Purpose |
|-----------------|---------|
| `"software architecture analysis best practices 2026"` | Contemporary patterns |
| `"API documentation patterns"` | REST/gRPC standards |
| `"error handling best practices"` | Exception handling |
| `"security patterns"` | Auth, validation |

**Implementation:**

```python
# In parallel research - Step 1
context7_findings = await context7_query(
    "software architecture analysis best practices 2026"
)
# Pass to all 3 explorers as "Principles Used"
```

#### GitHub Integration

**Full Cycle: Issue → Implementation → PR → Verification**

| GitHub Tool | Phase | Usage |
|-------------|-------|-------|
| `github_mcp_list_repos` | Research | Repository analysis |
| `github_mcp_list_issues` | Research | Check existing issues |
| `github_mcp_create_issue` | Synthesis | Create feature/issue |
| `github_mcp_create_pr` | Implementation | Create PR with changes |
| `github_mcp_list_issues` | Verification | Check related issues |

**Workflow:**

```
Research ──────► GitHub Issues (list, create)
      │
      ▼
Synthesis ─────► Create Issue (track feature)
      │
      ▼
Implementation ───► Create PR (code changes)
      │
      ▼
Verification ─────► Check CI status, Merge PR
```

#### Claude Cookbooks - Multi-Agent Swarm Pattern

**Agent State File (YAML Frontmatter):**

```yaml
---
agent_name: database-implementation
task_number: 4.2
pr_number: 5678
coordinator_session: team-leader
enabled: true
dependencies: ["Task 3.5", "Task 4.1"]
additional_instructions: "Use PostgreSQL, not MySQL"
---

# Task Assignment: Database Schema Implementation
```

**WorkflowTask Integration:**

```python
@dataclass
class WorkflowTask:
    task_id: str
    name: str
    target: str
    phases: List[TaskPhase]
    # Claude Cookbooks Swarm Pattern
    coordinator_session: str = ""  # Team coordinator
    task_number: str = ""          # Task in sprint
    pr_number: str = ""            # Linked PR
    dependencies: List[str] = []   # Blocked by other tasks
```

### Integration Points Summary

| Integration | Phase | MCP Tools | Purpose |
|-------------|-------|-----------|---------|
| **Context7** | Research | `context7_lookup`, `context7_query` | Best practices 2026 |
| **GitHub** | All phases | `github_mcp_*` | Issues, PRs, CI |
| **Claude Cookbooks** | All phases | Agent state files | Swarm coordination |

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
