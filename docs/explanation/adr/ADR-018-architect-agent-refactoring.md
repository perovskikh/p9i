# ADR-018: Architect Agent Refactoring

**Status**: Proposed

**Date**: 2026-04-02

**Authors**: Claude Code Analysis + p9i Team

---

## Context

Текущий architect агент в p9i имеет ограниченную функциональность:
- `use_checkpoint=False` — не умеет создавать файлы (ADR, диаграммы)
- Нет progress tracking — пользователь не видит этапов работы
- Последовательное выполнение — нет параллельного исследования
- Ограниченный набор из 3 промптов

После анализа исходного кода Claude Code (restored-src) выявлены компоненты для интеграции.

---

## Decision

Рефакторинг architect агента с использованием паттернов из Claude Code:

### 1. Agent Task State Machine

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from datetime import datetime

class AgentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"

@dataclass
class ToolActivity:
    """Track individual tool executions"""
    tool_name: str
    input: dict
    activity_description: str
    is_search: bool = False
    is_read: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AgentProgress:
    """Aggregated progress data"""
    tool_use_count: int = 0
    token_count: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    last_activity: Optional[datetime] = None
    recent_activities: List[ToolActivity] = field(default_factory=list)
    summary: str = ""

@dataclass
class ArchitectTaskState:
    """Architect agent state with progress tracking"""
    agent_id: str
    status: AgentStatus = AgentStatus.PENDING
    progress: AgentProgress = field(default_factory=AgentProgress)
    current_phase: str = ""  # "research", "synthesis", "output"
    adr_files_created: List[str] = field(default_factory=list)
    error: Optional[str] = None
```

### 2. 3-Phase Execution Model

```
┌─────────────────────────────────────────────────────────────┐
│                    Architect Agent Flow                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Phase 1: PARALLEL RESEARCH (Explorer agents)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ Explorer │  │ Explorer │  │ Explorer │                │
│  │ deps/X   │  │ flow/Y   │  │ arch/Z   │                │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                │
│       └─────────────┼─────────────┘                       │
│                     ▼                                        │
│  Phase 2: SYNTHESIS (Architect prompt)                      │
│  ┌─────────────────────────────────────┐                    │
│  │   Architectural Blueprint JSON      │                    │
│  │   - patterns_found[]                │                    │
│  │   - architecture_decision           │                    │
│  │   - components[]                    │                    │
│  │   - implementation_map              │                    │
│  └─────────────────────────────────────┘                    │
│                      │                                       │
│                      ▼                                       │
│  Phase 3: OUTPUT (CheckpointExecutor)                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │ ADR-XXX.md │  │ diagrams/   │  │ stubs/     │        │
│  └────────────┘  └────────────┘  └────────────┘        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 3. Prompts Structure

```
prompts/agents/architect/
├── promt-architect-design.md      # Main 3-phase orchestrator
├── create_adr.md                  # ADR document generator
├── promt-architect-research.md    # Research phase prompts
├── promt-architect-synthesis.md  # Synthesis phase prompts
└── promt-architect-output.md      # Output generation prompts
```

### 4. Parallel Research Implementation

```python
async def execute_parallel_research(self, request: str, context: dict) -> List[dict]:
    """
    Execute parallel explorer agents for comprehensive analysis.
    Claude Code pattern: spawn multiple workers, collect results.
    """
    research_tasks = [
        ("dependencies", f"Analyze dependencies and imports in {context.get('target', 'main')}),
        ("data_flow", f"Trace data flow and control flow in {context.get('target', 'main')}"),
        ("patterns", f"Identify architectural patterns in {context.get('target', 'main')}"),
    ]

    results = await asyncio.gather(*[
        self.orchestrator.execute_agent("explorer", task, context)
        for _, task in research_tasks
    ])

    return results
```

---

## Consequences

### Positive

- Progress visibility — пользователь видит этапы
- Parallel research — 3x faster для анализа
- File output — создание ADR файлов
- Better architecture — обоснованные решения на данных

### Negative

- Increased complexity — больше компонентов
- CheckpointExecutor overhead — для простых запросов
- More LLM calls — parallel research умножает запросы

---

## Implementation Plan

### Phase 1: Core (1-2 days)
- [ ] Add `AgentTaskState`, `ToolActivity`, `AgentProgress` to `src/domain/entities/`
- [ ] Modify architect agent: `use_checkpoint=True`
- [ ] Create `promt-architect-design.md` с 3-phase model

### Phase 2: Progress Tracking (1 day)
- [ ] Add progress callbacks to `PromptExecutor`
- [ ] Create `ArchitectProgressTracker` service
- [ ] Wire up progress updates in orchestrator

### Phase 3: Parallel Research (1-2 days)
- [ ] Add `execute_parallel_agents()` to orchestrator
- [ ] Create research phase prompts
- [ ] Update `promt-architect-design.md` для orchestration

### Phase 4: Output Generation (1 day)
- [ ] Enhance `create_adr.md` с frontmatter и templates
- [ ] Add diagram generation prompts
- [ ] Test full flow

---

## References

- Claude Code source: `restored-src/src/tasks/LocalAgentTask.ts`
- Claude Code coordinator: `restored-src/src/coordinator/coordinatorMode.ts`
- Existing p9i architect: `src/application/agent_router.py:51-62`
- CheckpointExecutor: `src/services/checkpoint_executor.py`
