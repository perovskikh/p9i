# p9i Onboarding Prompt

**Version:** 1.0
**Date:** 2026-04-01
**Purpose:** Адаптация разработчика к p9i проекту

> NOTE: This prompt is adapted for p9i - MCP server for AI prompt management.

## Triggers
- "онбординг", "onboard", "адаптация"
- First time setup of p9i development

## p9i Architecture Overview

```
p9i/
├── src/
│   ├── api/              # FastMCP server (20+ tools)
│   ├── application/      # Use cases, Agent routing, P9iRouter
│   ├── domain/           # Entities, Business rules
│   ├── infrastructure/   # LLM adapters (MiniMax, GLM, DeepSeek)
│   ├── services/         # Business logic (executor, orchestrator)
│   ├── storage/          # Prompt loading, Database
│   └── middleware/       # JWT, RBAC
├── prompts/              # 85+ markdown prompts
│   ├── core/            # Baseline (SHA256 locked)
│   ├── universal/        # 40+ agent prompts
│   └── packs/           # Plugin packs (k8s, ci-cd, uiux)
├── helm/p9i/            # K8s/Helm deployment
├── k8s/                 # K3s manifests
└── scripts/             # Automation scripts
```

## Quick Start

```bash
# Development
make dev                  # docker compose up

# Build & Deploy
docker build -t p9i .
make deploy              # helm upgrade in K3s

# Testing
pytest                   # All tests
pytest tests/test_storage.py  # Specific tests
```

## Key Technologies

| Component | Technology |
|---|---|
| MCP Server | FastMCP |
| LLM Providers | MiniMax-M2.7, GLM-4.7, DeepSeek |
| Database | PostgreSQL |
| Cache | Redis |
| Deployment | K3s + Helm |
| Transport | streamable-http, stdio |

## Key Files

| File | Purpose |
|---|---|
| `src/api/server.py` | Main MCP server entry point |
| `src/application/p9i_router.py` | Intent classification & routing |
| `src/services/orchestrator.py` | Multi-agent orchestration |
| `src/storage/prompts_v2.py` | Tiered prompt loading |
| `Makefile` | Development & deployment commands |

## ADR System

ADRs (Architecture Decision Records) are in `docs/explanation/adr/`.

Key ADRs for p9i:
- ADR-007: Multi-Agent Orchestrator
- ADR-014: Embeddings for prompt deduplication

Verify ADR compliance:
```bash
./scripts/verify-all-adr.sh
./scripts/verify-adr-checklist.sh
```

## Development Workflow

1. **Clone & Setup**
   ```bash
   git clone https://github.com/p9i/p9i.git
   cd p9i
   cp .env.example .env
   # Add API keys to .env
   ```

2. **Run MCP Server**
   ```bash
   make dev
   # Or locally:
   pip install -e .
   MCP_TRANSPORT=streamable-http python -m src.api.server
   ```

3. **Run Tests**
   ```bash
   pytest
   pytest --cov=src  # With coverage
   ```

4. **Contribute**
   - Follow existing code style
   - Add tests for new features
   - Update ADR if architecture changes
   - Pre-commit hooks run automatically

## Common Tasks

| Task | Command |
|---|---|
| Add new prompt | Create in `prompts/universal/` |
| Add new MCP tool | Add to `src/api/server.py` |
| Fix bug | `promt-bug-fix` agent |
| Add feature | `promt-feature-add` agent |
| Code review | `promt-llm-review` agent |

## Questions?

- Check `README.md` for quick reference
- Check `docs/explanation/adr/` for architecture decisions
- Use `p9i /help` for available commands
