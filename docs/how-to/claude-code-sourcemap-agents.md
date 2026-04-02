# Claude Code Sourcemap Agents

> **Status:** Research Complete
> **Source:** https://github.com/perovskikh/claude-code-sourcemap

---

## Overview

Claude Code Sourcemap contains a multi-agent system similar to p9i's orchestrator. This document describes the agents found in the restored source.

---

## All Found Agents

### Built-in Agents (`/src/tools/AgentTool/built-in/`)

| Агент | Назначение | Инструменты |
|-------|------------|-------------|
| **generalPurposeAgent** | Универсальный исследовательский агент | `*` (все) |
| **planAgent** | Архитектор/планировщик (read-only) | glob, grep, read |
| **exploreAgent** | Поиск специалист (read-only) | glob, grep, read, bash |
| **verificationAgent** | Верификация/тестирование | bash, run commands |
| **claudeCodeGuideAgent** | Гид по Claude Code | - |
| **statuslineSetupAgent** | Настройка статусной строки | - |

### Task Types (`/src/tasks/`)

| Тип | Описание |
|-----|----------|
| **LocalAgentTask** | Локальный фоновый агент |
| **RemoteAgentTask** | Удалённый агент (другой хост) |
| **InProcessTeammateTask** | in-process teammate с team-aware identity |
| **DreamTask** | Консолидация памяти |
| **LocalShellTask** | Локальная bash задача |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Coordinator Mode                          │
│           coordinatorMode.ts → multi-agent pipeline          │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                       ▼
┌───────────────┐    ┌─────────────────┐    ┌──────────────────┐
│ EXPLORE_AGENT │───▶│ GENERAL_PURPOSE │───▶│ VERIFICATION_    │
│ (read-only)   │    │ _AGENT          │    │ AGENT            │
│               │    │ (full access)   │    │ (runs commands)  │
└───────────────┘    └─────────────────┘    └──────────────────┘
        │                      │                       │
        └──────────────────────┴───────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │     PLAN_AGENT      │
                    │   (read-only)      │
                    └─────────────────────┘
```

---

## Key Patterns

1. **Role-Based Specialization** — каждый агент имеет ограниченные инструменты
2. **Read-Only по умолчанию** — planAgent и exploreAgent не модифицируют файлы
3. **VerificationAgent исполняет команды** — не просто читает код, а запускает тесты
4. **Coordinator Pattern** — оркестрирует параллельный workflow: Research → Synthesis → Implementation → Verification
5. **Abort Controller** — все агенты поддерживают отмену

---

## Explorer ↔ Reviewer Relationship

- **exploreAgent** — используется для исследования кодовой базы (glob, grep, read)
- **verificationAgent** — выполняет верификацию через реальные команды
- Оба **read-only** по своей природе, но **verificationAgent** может исполнять bash команды для проверки

---

## Key Files

| Файл | Назначение |
|------|------------|
| `AgentTool/loadAgentsDir.ts` | Загрузка определений агентов |
| `AgentTool/runAgent.ts` | Исполнение агента |
| `AgentTool/forkSubagent.ts` | Spawn фоновых агентов |
| `coordinator/coordinatorMode.ts` | Оркестрация multi-agent |
| `tasks/LocalAgentTask/LocalAgentTask.tsx` | Управление жизненным циклом |

---

## Comparison: Claude Code Sourcemap vs p9i ADR-016/ADR-020

### Summary Table

| Feature | Claude Code Sourcemap | p9i ADR-016 | p9i ADR-020 |
|---------|----------------------|-------------|--------------|
| **Explorer Agent** | exploreAgent.ts (read-only) | explorer (MVP/Extended/Verification) | - |
| **Reviewer/Verifier** | verificationAgent.ts | verification tool | - |
| **Coordinator Pattern** | coordinatorMode.ts | - | Coordinator/Worker pattern |
| **Agent Types** | Built-in agents + custom | p9i agent ecosystem | - |
| **Routing** | Built-in classification | P9iRouter (keyword) | - |
| **Volume Mounts** | - | - | /project mount planned |

---

### Explorer Agent Comparison

| Aspect | Claude Code | p9i ADR-016 |
|--------|-------------|-------------|
| Model | haiku/inherit | MiniMax-M2.7 |
| Tools | Glob, Grep, Read, BashOutput | explorer_search, explorer_index, explorer_call_graph |
| READ-ONLY | Yes | Yes |
| Caching | None | Redis + SQLite |
| Latency | ~200ms | ~500ms (MVP), ~50ms (cached Extended) |

**Key Difference**: p9i adds caching layer for performance

---

### Verification Agent Alignment

| Aspect | Claude Code | p9i ADR-016 |
|--------|-------------|-------------|
| Role | Red team testing | Same |
| Output | VERDICT: PASS/FAIL/PARTIAL | Same format |
| Features | Adversarial probes | Same |

✅ **Complete alignment**

---

### Architectural Alignment

| Claude Code Pattern | p9i Equivalent | Status |
|--------------------|----------------|--------|
| exploreAgent | explorer | ✅ ADR-016 implemented |
| verificationAgent | verification | ✅ In ADR-016 |
| planAgent | architect | ✅ ADR-018 |
| generalPurposeAgent | developer | ✅ Standard |
| coordinatorMode | AgentOrchestrator | ⚠️ ADR-020 proposed |
| forkSubagent | - | ❌ Not planned |

---

### Key Gaps Identified

1. **Coordinator pattern** — ADR-020 proposes solution
2. **Volume mounts** — ADR-020 addresses /project access
3. **forkSubagent** — No equivalent in p9i

---

## Related Documents

- [ADR-016: Code Explorer Agent](../explanation/adr/ADR-016-code-explorer-agent.md)
- [ADR-020: Coordinator Pattern & Volume Mounts](../explanation/adr/ADR-020-coordinator-pattern-and-volume-mounts.md)
- [Agent Interaction After ADR-15](./agent-interaction-after-adr15.md)
- [MPV Specification](./MPV.md)
