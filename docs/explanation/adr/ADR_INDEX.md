# ADR Index

| ADR # | Title | Status | Date | Focus |
|---------|--------|--------|--------|
| ADR-001 | [System Genesis & Repository Standards](ADR-001-system-genesis.md) | **Superseded** | 2026-03-13 | Foundational, 16 prompts flat |
| ADR-002 | [Tiered Prompt Architecture & MPV Integration](ADR-002-tiered-prompt-architecture-mpv-integration.md) | **Implemented** | 2026-03-19 | Tiered: 25 universal + 7 mpv + 4 pack |
| ADR-003 | [Prompt Storage Strategy](ADR-003-prompt-storage-strategy.md) | **Accepted** | 2026-03-20 | Files + Lazy Loading vs PostgreSQL |

## Legend

- **Accepted:** ADR has been approved for implementation
- **Proposed:** ADR is drafted and awaiting review
- **Deprecated:** ADR is no longer applicable (superseded by newer ADR)
- **TBD:** To be determined

## Quick Reference

### Active ADRs

#### **ADR-001: System Genesis & Repository Standards**
- **Status:** Accepted
- **Decision:** Define initial flat structure and founding principles
- **Date:** 2026-03-13
- **Focus:** Foundational architecture, repository standards
- **Content:**
  - Initial flat structure with 16 prompts (not 28)
  - Foundational principles and repository standards
  - System genesis documentation

---

#### **ADR-002: Tiered Prompt Architecture & MPV Integration**
- **Status:** ✅ IMPLEMENTED
- **Decision:** Implement 3-tier cascade + MPV 7-stage pipeline + legacy cleanup
- **Date:** 2026-03-18 (Implemented: 2026-03-19)
- **Focus:** Tiered architecture, MPV pipeline, legacy naming cleanup
- **Content:**
  - **Real System:** 31 prompts in tiered structure
  - **MPV Stage Prompts:** 7 prompts (promt-ideation → promt-finish)
  - **Plugin Packs:** k8s-pack (5), ci-cd-pack (4)
  - **3-Tier Cascade:** Core → Universal → MPV_Stage → Projects
  - **7-Stage Pipeline:** ideation → analysis → design → implementation → testing → debugging → finish
  - **Lazy Loading:** Depends() pattern + lru_cache
  - **Phase 1-4:** ✅ COMPLETE
  - **Phase 5:** ✅ COMPLETE (JWT, RBAC, HTTPS proxy)

---

### Related Documentation

- [MPV Specification](../how-to/MPV.md) - 7-Stage Pipeline & Tier Architecture
- [Legacy Architecture Analysis](../how-to/analysis-CodeShift-promt.md) - Historical reference (legacy naming)
- [Architecture Visualization](../how-to/universal_mcp_architecture_mermaid_style.svg) - Visual Diagram
- [Implementation Report](IMPLEMENTATION_REPORT_2026_03_18.md) - Detailed execution plan
- [Final Review Report](ADR-002-FINAL-REVIEW.md) - Complete review with real system analysis
- [Executive Summary](ADR-002-EXECUTIVE-SUMMARY.md) - Final executive summary
- [Memory Data](../memory/) - Project analysis and tracker data

---

**Last Updated:** 2026-03-20
**Total ADRs:** 3
**Active ADRs:** 2 (1 Proposed)
**Next ADR Number:** ADR-004
