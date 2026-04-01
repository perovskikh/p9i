# ADR-004: Deep-Project Integration - Prompt Orchestration Engine

## Статус решения
**Implemented** ✅ | 2026-03-24

## Прогресс реализации
✅ Полностью реализован

## Context

**Source:** [piercelamb/deep-project](https://github.com/piercelamb/deep-project) - Claude Code plugin for AI-assisted project decomposition.

**Problem:** p9i currently operates as a static "prompt library" without intelligent decomposition, dependency management, or workflow orchestration.

## Decision

We will integrate key features from deep-project to transform p9i into a dynamic "prompt orchestration engine."

### Features to Integrate

| Feature | Implementation |
|---------|----------------|
| **AI-Powered Interview** | `run_interview` - Q&A for intent clarification |
| **Smart Decomposition** | `decompose_prompt` - split complex goals into sub-prompts |
| **Dependency Mapping** | Workflow DAG - define execution order |
| **Automated Spec Generation** | `generate_spec` - auto-generate prompt manifests |
| **Resume Capability** | Checkpointing - pause/resume session state |

### Schema Enhancement

```json
{
  "id": "prompt_001",
  "type": "atomic | composite | workflow",
  "dependencies": ["prompt_000"],
  "requires_interview": true,
  "state": "completed | pending | paused"
}
```

### New MCP Tools

1. **`run_interview`** - AI interview to clarify requirements
2. **`decompose_prompt`** - decompose complex goals into chain
3. **`generate_spec`** - auto-generate documentation
4. **`checkpoint_save/load`** - session state management

## Consequences

- Architecture shifts from flat files to graph-based prompt relationships
- New prompt types: atomic, composite, workflow
- Dependencies enable proper execution ordering
- Checkpointing provides fault tolerance

## Alternatives Considered

- Keep static library model (rejected - limits expressiveness)
- Full deep-project clone (overkill - we need prompt-specific features)

## See Also
- [ADR-007: Multi-Agent Orchestrator](ADR-007-multi-agent-orchestrator.md) — Agent system built on this
- [MPV Pipeline](../how-to/MPV.md) — 7-stage pipeline

---
*Last Updated: 2026-03-24*
