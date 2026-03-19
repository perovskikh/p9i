# ADR-001: System Genesis & Repository Standards

## Status
**Accepted** | 2026-03-13

## Context

**Project Origin:** AI Prompt System (formerly CodeShift)
- Initial system design and foundational architecture
- First iteration of prompt management system
- MCP server with basic functionality

**Foundation Date:** 2026-03-13

**Initial Design Goals:**
1. Create a simple, flat prompt storage structure
2. Establish repository standards for prompt management
3. Enable basic MCP server functionality
4. Support multi-provider LLM integration

## Decision

### Initial Architecture (Flat Structure)

```
prompts/
├── registry.json          # Central prompt registry
├── promt-feature-add.md
├── promt-bug-fix.md
├── promt-refactoring.md
├── promt-security-audit.md
├── promt-quality-test.md
├── promt-ci-cd-pipeline.md
├── promt-onboarding.md
├── promt-project-stack-dump.md
├── promt-project-adaptation.md
├── promt-mvp-baseline-generator-universal.md
├── promt-context7-generation.md
├── promt-prompt-creator.md
├── promt-system-adapt.md
├── promt-versioning-policy.md
└── promt-adr-implementation-planner.md
```

**Total: 16 prompts in flat structure**

### Key Principles Established

1. **Flat Storage:** All prompts in single directory with registry.json
2. **Simple Loader:** Basic list/dict structure in src/storage/prompts.py
3. **MCP Server:** FastMCP with stdio transport for Claude Code
4. **Multi-Provider LLM:** Support for Anthropic, OpenRouter, ZAI, DeepSeek
5. **API Key Management:** Rate limiting (60s window) per key
6. **Audit Logging:** In-memory logging of all operations

### Initial Feature Set

| Feature | Status | Notes |
|---------|--------|-------|
| Prompt Storage | ✅ | Flat file-based |
| MCP Server | ✅ | FastMCP 3.x |
| LLM Integration | ✅ | Multi-provider |
| API Keys | ✅ | Rate limited |
| Audit Logging | ✅ | In-memory |

## Consequences

### Positive
- Simple, easy to understand structure
- Quick iteration and development
- Foundation for future expansion
- Clear prompt registry format

### Limitations Identified
- No tier separation between prompts
- No baseline protection mechanism
- No project-specific override capability
- No lazy loading (all prompts loaded at startup)
- No MPV pipeline integration

## Related ADR

- **ADR-002:** Tiered Prompt Architecture & MPV Integration
  - Supersedes flat structure with tiered architecture
  - Adds baseline lock and cascade priority
  - Implements MPV 7-stage pipeline

## Notes

- ADR-001 was retrospectively assigned after ADR-002 analysis
- Represents the "genesis" state before major architectural changes
- Kept for historical reference and understanding system evolution

---

**Created:** 2026-03-13
**Last Updated:** 2026-03-19
**Status:** Superseded by ADR-002
