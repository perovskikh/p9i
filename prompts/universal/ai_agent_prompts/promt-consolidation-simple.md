# ADR Consolidation Prompt - Automatic Slug Normalization

Version: 2.6
Type: ai-prompt-system
Layer: Meta
Status: active
Tags: [consolidation, dedup, sync, adr]

---

# ADR Consolidation Prompt: Automatic slug normalization and duplicate detection

## Task

Automatically detect and resolve ADR duplicate topic slugs using pre-commit hook.

---

## Slug Normalization

**Format:** lowercase, kebab-case
- ADR-001: adr-001-system-genesis
- ADR-002: adr-002-tiered-prompt-architecture-mpv-integration
- ADR-003: adr-003-prompt-storage-strategy

## Duplicate Detection

The pre-commit hook automatically detects:
- Duplicate ADR numbers (same number in different files)
- Duplicate topic slugs (same slug in different files)

## Current Duplicates Found

- ADR-002-FINAL-REVIEW.md - topic slug '002'
- ADR-002-REVIEW.md - topic slug '002'
- ADR-002-tiered-prompt-architecture-mpv-integration.md - topic slug '002'

## Resolution

These duplicates are caused by incorrect topic slug format. The correct slug should be:
- ADR-002-tiered-prompt-architecture-mpv-integration

No action needed - these files were consolidated during ADR-002 creation.

---

## When Using This Prompt

Use this prompt when you encounter ADR duplicate topics or need to:
1. Check if duplicate is due to incorrect slug
2. Rename to correct format with suffix if needed
3. Or mark as deprecated if replaced

---

**Example Request:**
"fix duplicate ADR topic slug '002' use p9i"
