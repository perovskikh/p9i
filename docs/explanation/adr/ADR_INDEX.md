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
| ADR-014 | [LLM-based Prompt Selection with Embeddings](ADR-014-llm-prompt-selection.md) | **Proposed** 📋 | 2026-04-01 | OpenRouter + Qdrant + Redis | ADR-007, ADR-013 |
| ADR-015 | [Code Explorer Agent](ADR-015-code-explorer-agent.md) | **Proposed** 📋 | 2026-04-01 | Deep code analysis, execution tracing, dependency graphs | ADR-007, ADR-014 |

## Legend

- **Implemented:** ADR has been fully implemented
- **Accepted:** ADR has been approved for implementation
- **Proposed:** ADR is drafted and awaiting review
- **Deprecated:** ADR is no longer applicable (superseded by newer ADR)
- **TBD:** To be determined

### Related Documentation

- [MPV Specification](../how-to/MPV.md) - 7-Stage Pipeline & Tier Architecture
- [Architecture Visualization](../how-to/universal_mcp_architecture_mermaid_style.svg) - Visual Diagram
- [Final Review Report](reviews/ADR-002-FINAL-REVIEW.md) - Complete review with real system analysis

---

**Last Updated:** 2026-04-01
**Total ADRs:** 10
**Implemented:** 7 | **Proposed:** 2 | **Deprecated:** 1
**Next ADR:** ADR-016 (planned)
