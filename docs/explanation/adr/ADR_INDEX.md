# ADR Index

| ADR # | Title | Status | Date | Focus | Related |
|---------|--------|--------|--------|--------|---------|
| ADR-001 | [System Genesis & Repository Standards](ADR-001-system-genesis.md) | **Deprecated** | 2026-03-13 | Foundational, superseded by ADR-002 | — |
| ADR-002 | [Tiered Prompt Architecture & MPV Integration](ADR-002-tiered-prompt-architecture-mpv-integration.md) | **Implemented** ✅ | 2026-03-19 | Tiered: core + universal + packs | ADR-003, MPV |
| ADR-003 | [Prompt Storage Strategy](ADR-003-prompt-storage-strategy.md) | **Implemented** ✅ | 2026-03-20 | Files + Lazy Loading vs PostgreSQL | ADR-002 |
| ADR-004 | [Deep-Project Integration - Prompt Orchestration](ADR-004-deep-project-integration.md) | **Implemented** ✅ | 2026-03-22 | AI Interview, Decomposition, DAG | ADR-007 |
| ADR-005 | [UI/UX Integration Strategy](ADR-005-ui-ux-integration.md) | **Implemented** ✅ | 2026-03-22 | TailwindCSS, shadcn, Textual, Tauri | ADR-006 |
| ADR-006 | [Figma Integration Strategy](ADR-006-figma-integration.md) | **Implemented** ✅ | 2026-03-22 | Figma API, design-to-code, tokens | ADR-005 |
| ADR-007 | [Multi-Agent Orchestrator](ADR-007-multi-agent-orchestrator.md) | **Implemented** ✅ | 2026-03-24 | 7 agents, Siri voice, browser, dedup guard | ADR-004 |
| ADR-011 | [Pack Architecture Standard](ADR-011-pack-architecture-standard.md) | **Implemented** ✅ | 2026-04-03 | Pack standard, github-pack, browser-pack | ADR-002 |
| ADR-012 | [Pre-commit Hook Installation Requirement](ADR-012-pre-commit-installation.md) | **Implemented** ✅ | 2026-03-30 | pre-commit installation, ADR validation | ADR-001 |
| ADR-013 | [Code Review Improvements](ADR-013-code-review-improvements.md) | **Implemented** ✅ | 2026-03-31 | Parallel review checks, quality gates | ADR-007, ADR-017 |
| ADR-014 | [Semantic Search with Optional Feature Flag](ADR-014-semantic-search.md) | **Partial** 🔄 | 2026-04-04 | HybridPromptRouter ✅, Embeddings ❌ | ADR-007, ADR-013 |
| ADR-015 | [Code Explorer Agent (Original)](ADR-015-code-explorer-agent.md) | **Superseded** 📋 | 2026-04-01 | Superseded by ADR-016 | ADR-007 |
| **ADR-016** | **[Code Explorer Agent — Unified Implementation](ADR-016-code-explorer-agent.md)** | **Accepted** ✅ (Partial) | 2026-04-02 | MVP/Extended/Verification, Redis cache | ADR-007 |
| ADR-016a | [Code Explorer Agent — MVP](ADR-016a-explorer-agent-mvp.md) | **Superseded** 📋 | 2026-04-02 | Merged into ADR-016 | ADR-016 |
| ADR-016b | [Code Explorer Agent — Extended](ADR-016b-explorer-agent-extended.md) | **Superseded** 📋 | 2026-04-02 | Merged into ADR-016 | ADR-016 |
| ADR-016c | [Verification Agent](ADR-016c-verification-agent.md) | **Superseded** 📋 | 2026-04-02 | Merged into ADR-016 | ADR-016 |
| **ADR-017** | **[Reviewer Agent Refactor](ADR-017-reviewer-agent-refactor.md)** | **Proposed** 📋 | 2026-04-02 | 4-layer review system, parallel rejected | ADR-016 |
| **ADR-018** | **[Architect Agent Refactoring](ADR-018-architect-agent-refactoring.md)** | **Implemented** ✅ | 2026-04-03 | State machine, progress tracking, 3-phase model | ADR-016 |
| **ADR-019** | **[Parallel Research Phase](ADR-019-parallel-research-phase.md)** | **Proposed** 📋 | 2026-04-02 | Three-explorer parallel research | ADR-018 |
| **ADR-020** | **[Coordinator Pattern & Volume Mounts](ADR-020-coordinator-pattern-and-volume-mounts.md)** | **Phase 2 Done** 🔄 | 2026-04-03 | Volume mounts ✅, Coordinator ✅, Tool Permissions ✅ | ADR-018, ADR-019 |
| **ADR-021** | **[Code Review Fixes](ADR-021-code-review-fixes.md)** | **Implemented** ✅ | 2026-04-04 | Reviewer fixes, verification agent | ADR-017 |
| **ADR-022** | **[Multi-Project SaaS Architecture](ADR-022-multi-project-saas-architecture.md)** | **Proposed** 📋 | 2026-04-03 | Projects, SFTP, API keys | ADR-007 |
## Legend

- **Implemented:** ADR has been fully implemented
- **Accepted:** ADR has been approved for implementation
- **Proposed:** ADR is drafted and awaiting review
- **Deprecated:** ADR is no longer applicable (superseded by newer ADR)
- **Superseded:** ADR has been merged into another ADR
- **Phase 2 Done:** First phase completed, subsequent phases pending

### Related Documentation

- [MPV Specification](../how-to/MPV.md) - 7-Stage Pipeline & Tier Architecture
- [Architecture Visualization](../how-to/universal_mcp_architecture_mermaid_style.svg) - Visual Diagram
- [Agent Architecture Implementation Status](../how-to/agent-architecture-implementation-status.md) - Claude Code vs p9i alignment
- [Claude Code Sourcemap Agents](../how-to/claude-code-sourcemap-agents.md) - Source analysis
- [Final Review Report](reviews/ADR-002-FINAL-REVIEW.md) - Complete review with real system analysis

---

**Last Updated:** 2026-04-05 (Multi-Agent Workflow + Quality Analysis added)
**Total ADRs:** 18
**Implemented:** 7 | **Proposed/Partial:** 6 | **Deprecated:** 1 | **Superseded:** 4

### ADR Quality Scores (2026-04-05)

| Score Range | ADRs | Notes |
|-------------|------|-------|
| 80-100 | ADR-007, ADR-021 | ✅ Production ready |
| 70-79 | ADR-016, ADR-018 | ⚠️ Mostly complete |
| 60-69 | ADR-014, ADR-020 | ⚠️ Partial implementation |
| 40-59 | ADR-017, ADR-019, ADR-022 | ❌ Need implementation |

## Verification Report (2026-04-02)

### ✅ Verified Issues Fixed

| Issue | File | Fix |
|-------|------|-----|
| ADR-017 wrong Supersedes | ADR-017.md | Changed "ADR-013, ADR-014" → "ADR-013" |

### Verification Summary

| Check | Status |
|-------|--------|
| ADR-011 (Pack Standard) | ✅ Implemented - 6 packs |
| ADR-014 (LLM Prompt Selection) | ✅ Valid - Partial Implementation |
| ADR-016 (Code Explorer) | ✅ Valid - Accepted (Partial) |
| ADR-017 (Reviewer) | ✅ Fixed - Proposed (was wrong supersedes) |
| ADR-018 (Architect) | ✅ Implemented |
| ADR-019 (Parallel Research) | ✅ Valid - Proposed |
| ADR-020 (Coordinator) | ✅ Valid - Phase 2 Done |
| ADR-021 (Code Review Fixes) | ✅ Implemented |

### ADR Files vs Index

| ADR | In Index | File Exists | Status Match |
|-----|----------|-------------|-------------|
| ADR-001 | ✅ | ✅ | Deprecated ✅ |
| ADR-002 | ✅ | ✅ | Implemented ✅ |
| ADR-003 | ✅ | ✅ | Implemented ✅ |
| ADR-004 | ✅ | ✅ | Implemented ✅ |
| ADR-005 | ✅ | ✅ | Implemented ✅ |
| ADR-006 | ✅ | ✅ | Implemented ✅ |
| ADR-007 | ✅ | ✅ | Implemented ✅ |
| ADR-011 | ✅ | ✅ | Implemented ✅ |
| ADR-012 | ✅ | ✅ | Implemented ✅ |
| ADR-014 | ✅ | ✅ | Partial ✅ |
| ADR-015 | ✅ | ❌ File merged | Superseded ✅ |
| ADR-016 | ✅ | ✅ | Accepted (Partial) ✅ |
| ADR-016a | ✅ | ❌ File merged | Superseded ✅ |
| ADR-016b | ✅ | ❌ File merged | Superseded ✅ |
| ADR-016c | ✅ | ❌ File merged | Superseded ✅ |
| ADR-017 | ✅ | ✅ | Proposed ✅ |
| ADR-018 | ✅ | ✅ | Implemented ✅ |
| ADR-019 | ✅ | ✅ | Proposed ✅ |
| ADR-020 | ✅ | ✅ | Phase 2 Done ✅ |
| ADR-021 | ✅ | ✅ | Implemented ✅ |
| ADR-022 | ✅ | ✅ | Proposed ✅ |

---

## ADR Quality Analysis (2026-04-05)

| ADR | Status | Quality Score | Gap |
|-----|--------|--------------|-----|
| **ADR-007** Multi-Agent Orchestrator | ✅ Implemented | 85/100 | 7 agents, needs coordinator pattern |
| **ADR-014** Semantic Search | ⚠️ Partial | 60/100 | HybridRouter ✅, Embeddings ❌ |
| **ADR-016** Code Explorer | ✅ Accepted | 70/100 | MVP done, Extended/Verification pending |
| **ADR-017** Reviewer Refactor | 📋 Proposed | 40/100 | Only draft, NOT implemented |
| **ADR-018** Architect Refactoring | ✅ Implemented | 75/100 | State machine done, needs parallel research integration |
| **ADR-019** Parallel Research | ✅ Implemented | 75/100 | `execute_parallel_research()` integrated in orchestrator |
| **ADR-020** Coordinator Pattern | ✅ Phase 2 | 85/100 | Volume mounts ✅, 4-phase workflow ✅, Worker lifecycle ✅ |
| **ADR-021** Code Review Fixes | ✅ Implemented | 80/100 | Done |
| **ADR-022** Multi-Project SaaS | ⚠️ Phase 1-3 | 50/100 | MCP tools incomplete |

## Multi-Agent Workflow (Claude Code Pattern)

```
        [ ИССЛЕДОВАНИЕ ]
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
[Explorer] [Explorer] [Explorer]  ← Параллельные Worker'ы
 Tech Stack  Patterns  Quality
    │         │         │
    └─────────┼─────────┘
              ▼
        [ СИНТЕЗ ]
              │
              ▼
     [ КООРДИНАТОР ] ← Центральный роутер
              │
              ▼
        [ РЕАЛИЗАЦИЯ ]
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
[Worker] [Worker] [Worker]  ← Параллельные Worker'ы
    │         │         │
    └─────────┼─────────┘
              ▼
        [ ВЕРИФИКАЦИЯ ]
```

### Phase 1: Research (Parallel Workers)

| Worker | Focus | Current State |
|--------|-------|---------------|
| Explorer 1 | Tech Stack Analysis | ✅ Complete |
| Explorer 2 | Code Patterns & Structure | ✅ Complete |
| Explorer 3 | Best Practices & Quality | ✅ Complete |

### Phase 2: Synthesis + Coordinator

- **Synthesizer**: Architect Agent combines all explorer findings
- **Coordinator**: Routes to correct implementation path (ADR-020 Phase 2)

### Phase 3: Implementation (Parallel Workers)

| Worker | Tasks | Dependencies |
|--------|-------|--------------|
| Worker 1 | Core Infrastructure (ADR-007, ADR-014 core) | ADR-020 Phase 2 |
| Worker 2 | Enhancement (ADR-018 integration, ADR-019) | ADR-020 Phase 2 |
| Worker 3 | Multi-Project (ADR-022 MCP tools) | ADR-020 Phase 2 |

### Phase 4: Verification

- Reviewer Agent validates each ADR implementation
- Security audit readiness check
- Integration tests

## Implementation Priority Matrix

| Priority | ADR | Action | Worker Type | Status |
|----------|-----|--------|-------------|--------|
| ~~P0~~ | ~~ADR-019~~ | ~~Integrate parallel research into orchestrator~~ | ~~architect~~ | ✅ **DONE** |
| **P0** | ADR-020 Phase 2 | Coordinator pattern enhancements | architect | 🔄 In Progress |
| **P1** | ADR-014 | Add real embeddings (Jina/Qdrant) | developer | ⏳ Pending |
| **P1** | ADR-022 | Complete MCP tools | developer | ⏳ Pending |
| **P2** | ADR-017 | Implement 4-layer review system | reviewer | ⏳ Pending |
| **P2** | ADR-020 Phase 3 | Tool Permissions integration | devops | ⏳ Pending |

## Execution Order (2026-04-05)

### Phase 1: Foundation

| Priority | ADR | Why First | Implementation | Key Files |
|----------|-----|-----------|----------------|-----------|
| **1.1** | ADR-007 Multi-Agent Orchestrator | Base infrastructure - all other ADRs depend on it | ✅ Implemented | `src/services/orchestrator.py` |
| **1.2** | ADR-022 Multi-Project SaaS | Database models + service layer complete | ⚠️ Phase 1-3 Done, MCP pending | `src/storage/models/project.py`, `src/services/project_service.py` |
| **1.3** | ADR-020 Phase 1 | Project file access - enables agents to analyze code | ✅ Implemented | `helm/values.yaml`, `docker-compose.yml` |

### Phase 2: Core Features

| Priority | ADR | Why Second | Implementation | Key Files |
|----------|-----|-----------|----------------|-----------|
| **2.1** | ADR-019 Parallel Research | 3-phase parallel research model | ✅ Implemented `execute_parallel_research()` | `orchestrator.py:execute_parallel_research()` |
| **2.2** | ADR-020 Phase 2 Coordinator | 4-phase workflow (Research→Synthesis→Implementation→Verification) | ✅ Implemented | `orchestrator.py:create_workflow(),execute_workflow()` |
| **2.3** | ADR-014 Semantic Search | Foundation for intelligent routing | ⚠️ HybridRouter ✅, Embeddings ❌ | `cascade/hybrid.py`, `cascade/semantic.py` |

### Phase 3: Enhancement

| Priority | ADR | Why Third | Implementation | Key Files |
|----------|-----|-----------|----------------|-----------|
| **3.1** | ADR-020 Phase 3 Permissions | Security hardening | ⚠️ Class exists, NOT integrated | `domain/entities/tool_permissions.py` |
| **3.2** | ADR-022 Phase 2 Session | Project isolation | ❌ Not implemented | — |

### Dependencies Graph

```
ADR-007 ──┬──► ADR-019 (Parallel Research)
          │
          └──► ADR-020 Phase 2 (Coordinator)
                     │
                     └──► ADR-020 Phase 3 (Permissions)

ADR-022 ──┬──► ADR-020 Phase 1 (Volume Mounts) ✅
          │
          └──► ADR-014 (Semantic Search) [independent]
```

### Recommended Execution Order

```
1. ✅ ADR-019 (Parallel Research)    → DONE: execute_parallel_research() integrated
2. ✅ ADR-020 Phase 2 (Coordinator) → DONE: 4-phase workflow (Research→Synthesis→Implementation→Verification)
3. ADR-014 (Embeddings)          → Pending: Add real embeddings provider (Jina/Qdrant)
4. ADR-022 MCP Tools              → Pending: Complete project management endpoints
```

### Context7 Best Practices (Claude Code)

- ✅ `/feature-dev`: 7-phase workflow with parallel agents
- ✅ Layered Architecture: commands → agents → skills → lib
- ✅ Code Architect Agent: Pattern Analysis + Build Sequence
- ✅ Proactive Review: agent reviews own output
- ✅ Interactive Questions: AskUserQuestion for complex decisions

### Critical Gaps

| Gap | ADR | Impact | Status |
|-----|-----|--------|--------|
| ~~Parallel research not integrated~~ | ~~ADR-019~~ | ~~Can't do 3-way parallel exploration~~ | ✅ **FIXED** |
| ~~Coordinator not aligned with Claude Code~~ | ~~ADR-020 Phase 2~~ | ~~Missing forkSubagent.ts pattern~~ | ✅ **FIXED** |
| Embeddings use fallback (hash-based) | ADR-014 | Semantic search quality degraded | ⏳ Pending |
| ToolPermissions not integrated | ADR-020 Phase 3 | Security hardening incomplete | ⏳ Pending |
| Project MCP tools incomplete | ADR-022 | Multi-project SaaS incomplete | ⏳ Pending |
