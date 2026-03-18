# Universal Prompt System

A self-contained, project-agnostic AI agent prompt system that adapts to any codebase with a single prompt.

## Quick Start

```bash
# Add as git submodule
git submodule add https://github.com/your-org/universal-prompt-system.git prompts

# Or clone directly
git clone https://github.com/your-org/universal-prompt-system.git prompts
```

## Structure

```
prompts/
├── universal-adapter.md    # Main adaptation prompt
├── quickstart.md           # Integration guide
├── config.yaml             # Project configuration template
├── README.md               # This file
└── examples/               # Language-specific examples
    ├── python.md
    ├── nodejs.md
    ├── go.md
    ├── clean-project.md
    ├── microservices.md
    └── ai-ml.md
```

## Usage

1. **One-time setup:** Copy `config.yaml` to your project root and configure
2. **Adaptation:** Run the prompt with your project context
3. **Iterate:** Use generated artifacts for onboarding/development

## Documentation

- [Quickstart Guide](quickstart.md) — How to integrate
- [Universal Adapter](universal-adapter.md) — Main prompt
- [Examples](examples/) — Language-specific adaptation examples
- [Configuration](config.yaml) — YAML config reference

## Compatibility

| Feature | Status |
|---------|--------|
| Claude Code | ✓ Supported |
| Cursor | ✓ Supported |
| GitHub Copilot | ✓ Supported |
| OpenAI Assistants | ✓ Supported |

---

**Version:** 1.0
**Date:** 2026-03-15
**License:** MIT
