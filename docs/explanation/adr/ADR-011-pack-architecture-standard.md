# ADR-011: Pack Architecture Standard

## Status
**Proposed** | 2026-03-24

## Context

p9i currently has two implementation patterns:
1. **Pack-based** - Domain-specific prompts in `prompts/packs/` with trigger-based routing
2. **Direct MCP tools** - Domain logic embedded in `src/api/server.py` and `src/infrastructure/`

This creates inconsistency:
- k8s-pack, ci-cd-pack, pinescript-v6 use pack format
- browser, github, figma, docs integrations are direct MCP tools
- uiux-pack exists but overlaps with `src/infrastructure/uiux/tools.py`

## Decision

We will standardize on **pack-based architecture** for all domain-specific integrations.

### Pack Definition

A pack is a self-contained plugin that includes:
1. **pack.json** - Manifest with metadata, triggers, and prompt list
2. **prompts/*.md** - Prompt templates for the domain
3. **data/*.json** - Optional reference data (color palettes, icon sets, etc.)

```
pack-name/
├── pack.json          # Manifest
├── prompts/
│   ├── prompt-1.md
│   └── prompt-2.md
└── data/
    └── reference.json  # Optional
```

### Pack Manifest Schema

```json
{
  "name": "pack-name",
  "version": "1.0.0",
  "description": "Domain description",
  "tier": 3,
  "author": "9Mirrors-Lab",
  "mcp_requires": [],
  "prompts": [
    "prompts/prompt-1.md",
    "prompts/prompt-2.md"
  ],
  "triggers": {
    "keyword1, keyword2": "prompts/prompt-1.md",
    "keyword3": "prompts/prompt-2.md"
  },
  "dependencies": [],
  "tags": ["tag1", "tag2"],
  "created_at": "2026-03-24"
}
```

### Pack Discovery & Routing

1. **PackLoader** (`src/storage/packs.py`) scans `prompts/packs/*/pack.json`
2. **Trigger matching** happens in `ai_prompts()` before INTENT_MAP
3. Pack prompts are loaded from `prompts/packs/{pack}/prompts/*.md`

### Integration Points

| Component | Location | Responsibility |
|-----------|----------|----------------|
| PackLoader | `src/storage/packs.py` | Load manifests, find triggers |
| ai_prompts() | `src/api/server.py` | Route to pack prompts via triggers |
| PromptExecutor | `src/services/executor.py` | Execute pack prompts via LLM |

### What Should Be a Pack

**Yes - Pack:**
- Domain-specific prompt collections
- Keywords/triggers for natural language routing
- Reference data (colors, icons, templates)

**No - Not a Pack:**
- Core infrastructure (LLM adapters, JWT, RBAC)
- Generic orchestration (run_prompt, run_interview, decompose)
- Internal agents (architect, developer, reviewer)

## Implementation Plan

### Phase 1: Standardize Existing Packs

| Pack | Status | Notes |
|------|--------|-------|
| k8s-pack | ✅ OK | Already follows standard |
| ci-cd-pack | ✅ OK | Already follows standard |
| pinescript-v6 | ✅ OK | Already follows standard |
| uiux-pack | ⚠️ Needs MCP tool integration | MCP tools should use pack prompts |

### Phase 2: Convert to Packs

| Integration | New Pack | Priority |
|------------|----------|----------|
| browser tools | browser-pack | High |
| github tools | github-pack | High |
| figma tools | (integrate with uiux-pack) | Medium |
| context7/docs | docs-pack | Medium |

### Phase 3: Deprecate Direct Integration

1. Remove domain-specific keywords from INTENT_MAP in `ai_prompts()`
2. Migrate to pack triggers
3. MCP tools should delegate to pack prompts, not implement logic directly

## Consequences

### Positive
- Consistent architecture for all domain integrations
- Easier to add new domains
- Clear separation of concerns
- Pack prompts can be versioned and baseline-verified

### Negative
- Migration effort for existing integrations
- Some MCP tools may need refactoring to delegate to packs

## References

- ADR-002: Tiered Prompt Architecture
- ADR-004: Deep Project Integration
- ADR-005: UI/UX Integration
- ADR-007: Multi-Agent Orchestrator
