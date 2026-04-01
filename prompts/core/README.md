# Core Prompts — Baseline System

**Version:** 1.0
**Date:** 2026-03-31
**Purpose:** Baseline prompts for AI Prompt System v2.0.0 — immutable foundation for all AI agent operations.

## Overview

This directory contains the **baseline prompts** for the AI Prompt System v2.0.0. These are the fundamental system prompts that provide the foundation for all AI agent operations.

## ⚠️ Important: Read-Only

All prompts in this directory are **immutable** and **cannot be overridden** by project-specific prompts. This ensures system stability and consistency across all projects.

## Baseline Protection

All core prompts are protected by:
- **SHA256 checksums** in `.promt-baseline-lock` file
- **Server-side enforcement** of immutability flags
- **Read-only file system permissions** on the `core/` directory

## Core Prompts

| Prompt | Version | Description | Immutable |
|--------|----------|------------|-----------|
| `promt-feature-add.md` | 1.5 | Adding new functionality to code | ✅ Yes |
| `promt-bug-fix.md` | 1.2 | Fixing bugs and debugging code | ✅ Yes |
| `promt-refactoring.md` | 1.2 | Improving code structure and quality | ✅ Yes |
| `promt-security-audit.md` | 1.2 | Security audit and vulnerability assessment | ✅ Yes |
| `promt-quality-test.md` | 1.2 | Quality assurance and testing strategies | ✅ Yes |

## Directory Structure

```
core/
├── .promt-baseline-lock      ← Cryptographic protection
├── promt-feature-add.md
├── promt-bug-fix.md
├── promt-refactoring.md
├── promt-security-audit.md
└── promt-quality-test.md
```

## Usage Guidelines

### For Core System Developers
1. **DO NOT modify** core prompts directly. Use the project's ADR process.
2. If changes are needed, create a new ADR and follow the process.
3. All changes must update the SHA256 checksums in `.promt-baseline-lock`.
4. After updating checksums, regenerate the baseline lock file.
5. Test changes thoroughly before committing.

### For All Developers
1. **Core prompts are read-only** — project-specific prompts can override universal prompts, but NOT core prompts.
2. **Override priority:** `projects → universal → core` — core prompts have lowest priority.
3. **Use `promt-prompt-creator`** to create new prompts if you need custom behavior.
4. **Do NOT create files in `core/`** — this directory is reserved for baseline prompts only.

## Verification

The system verifies baseline integrity on every startup:
1. Loads `.promt-baseline-lock` file
2. Computes SHA256 hashes for all core prompt files
3. Compares current hashes with stored hashes
4. **Action on mismatch:** Raises `SecurityError` and rejects load
5. **Action on match:** Uses cached/stored version

## Contact

If you need to modify core prompts or have questions about the baseline system:
1. Review `ADR-002: Tiered Prompt Architecture & MPV Integration`
2. Follow the established ADR process
3. Contact the system maintainers

---

**Last Updated:** 2026-03-18
**Protected By:** `ADR-002: Tiered Prompt Architecture & MPV Integration`
**Baseline Lock Version:** 1.0.0
