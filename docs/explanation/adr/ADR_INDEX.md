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
| ADR-012 | [Pre-commit Hook Installation Requirement](ADR-012-pre-commit-installation.md) | **Implemented** ✅ | 2026-03-30 | pre-commit installation, ADR validation | ADR-001 |
| ADR-014 | [LLM-based Prompt Selection with Embeddings](ADR-014-llm-prompt-selection.md) | **Partial** 🔄 | 2026-04-02 | HybridRouter ✅, Embeddings ❌ | ADR-007, ADR-013 |
| ADR-015 | [Code Explorer Agent (Original)](ADR-015-code-explorer-agent.md) | **Superseded** 📋 | 2026-04-01 | Superseded by ADR-016 | ADR-007 |
| **ADR-016** | **[Code Explorer Agent — Unified Implementation](ADR-016-code-explorer-agent.md)** | **Accepted** ✅ (Partial) | 2026-04-02 | MVP/Extended/Verification, Redis cache | ADR-007 |
| ADR-016a | [Code Explorer Agent — MVP](ADR-016a-explorer-agent-mvp.md) | **Superseded** 📋 | 2026-04-02 | Merged into ADR-016 | ADR-016 |
| ADR-016b | [Code Explorer Agent — Extended](ADR-016b-explorer-agent-extended.md) | **Superseded** 📋 | 2026-04-02 | Merged into ADR-016 | ADR-016 |
| ADR-016c | [Verification Agent](ADR-016c-verification-agent.md) | **Superseded** 📋 | 2026-04-02 | Merged into ADR-016 | ADR-016 |
| **ADR-017** | **[Reviewer Agent Refactor](ADR-017-reviewer-agent-refactor.md)** | **Proposed** 📋 | 2026-04-02 | 4-layer review system, parallel rejected | ADR-016 |
| **ADR-018** | **[Architect Agent Refactoring](ADR-018-architect-agent-refactoring.md)** | **Proposed** 📋 | 2026-04-02 | State machine, progress tracking | ADR-016 |
| **ADR-019** | **[Parallel Research Phase](ADR-019-parallel-research-phase.md)** | **Proposed** 📋 | 2026-04-02 | Three-explorer parallel research | ADR-018 |
| **ADR-020** | **[Coordinator Pattern & Volume Mounts](ADR-020-coordinator-pattern-and-volume-mounts.md)** | **Phase 1 Done** 🔄 | 2026-04-02 | Volume mounts ✅, Coordinator pending | ADR-018, ADR-019 |
## Legend

- **Implemented:** ADR has been fully implemented
- **Accepted:** ADR has been approved for implementation
- **Proposed:** ADR is drafted and awaiting review
- **Deprecated:** ADR is no longer applicable (superseded by newer ADR)
- **Superseded:** ADR has been merged into another ADR
- **Phase 1 Done:** First phase completed, subsequent phases pending

### Related Documentation

- [MPV Specification](../how-to/MPV.md) - 7-Stage Pipeline & Tier Architecture
- [Architecture Visualization](../how-to/universal_mcp_architecture_mermaid_style.svg) - Visual Diagram
- [Agent Architecture Implementation Status](../how-to/agent-architecture-implementation-status.md) - Claude Code vs p9i alignment
- [Claude Code Sourcemap Agents](../how-to/claude-code-sourcemap-agents.md) - Source analysis
- [Final Review Report](reviews/ADR-002-FINAL-REVIEW.md) - Complete review with real system analysis

---

**Last Updated:** 2026-04-02 (Verification Complete)
**Total ADRs:** 20
**Implemented:** 7 | **Proposed/Partial:** 6 | **Deprecated:** 1 | **Superseded:** 6

## Verification Report (2026-04-02)

### ✅ Verified Issues Fixed

| Issue | File | Fix |
|-------|------|-----|
| ADR-017 wrong Supersedes | ADR-017.md | Changed "ADR-013, ADR-014" → "ADR-013" |

### Verification Summary

| Check | Status |
|-------|--------|
| ADR-014 (LLM Prompt Selection) | ✅ Valid - Partial Implementation |
| ADR-016 (Code Explorer) | ✅ Valid - Accepted (Partial) |
| ADR-017 (Reviewer) | ✅ Fixed - Proposed (was wrong supersedes) |
| ADR-018 (Architect) | ✅ Valid - Proposed |
| ADR-019 (Parallel Research) | ✅ Valid - Proposed |
| ADR-020 (Coordinator) | ✅ Valid - Phase 1 Done |

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
| ADR-012 | ✅ | ✅ | Implemented ✅ |
| ADR-014 | ✅ | ✅ | Partial ✅ |
| ADR-015 | ✅ | ❌ File merged | Superseded ✅ |
| ADR-016 | ✅ | ✅ | Accepted (Partial) ✅ |
| ADR-016a | ✅ | ❌ File merged | Superseded ✅ |
| ADR-016b | ✅ | ❌ File merged | Superseded ✅ |
| ADR-016c | ✅ | ❌ File merged | Superseded ✅ |
| ADR-017 | ✅ | ✅ | Proposed ✅ |
| ADR-018 | ✅ | ✅ | Proposed ✅ |
| ADR-019 | ✅ | ✅ | Proposed ✅ |
| ADR-020 | ✅ | ✅ | Phase 1 Done ✅ |
