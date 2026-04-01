# AI Agent Prompts — p9i

> p9i MCP Server prompt registry and guide.

## Overview

p9i is an MCP (Model Context Protocol) server for managing AI prompts through their full lifecycle: from idea to production implementation. The system uses a **cascade routing architecture** to select the right prompt based on user intent.

## Architecture

The routing system follows: **Intent → Agent → Prompt**

```
User Request
    │
    ▼
┌─────────────────────────────────────────┐
│  P9iRouter (Natural Language Router)    │
│  - Keyword classification (no LLM!)     │
│  - Context-aware overrides              │
│  - Priority: COMMAND > PROMPT > AGENT   │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  AgentRouter (Agent Detection)           │
│  - 8 specialized agents                 │
│  - Keyword matching + semantic fallback  │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  HybridPromptRouter (Prompt Selection)   │
│  Cascade: Rule → Semantic → LLM         │
└─────────────────────────────────────────┘
```

## Agents

| Agent | Trigger Keywords | Purpose |
|-------|------------------|---------|
| `full_cycle` | реализуй, внедри, сделай, e2e | Complete pipeline (idea→impl→test→docs) |
| `architect` | спроектируй, архитектура, adr, design | System design, ADRs |
| `developer` | создай, добавь, напиши, код | Code generation, features |
| `reviewer` | проверь, ревью, аудит, тест, исправь | Code review, security |
| `designer` | дизайн, ui, ux, интерфейс | UI/UX design |
| `devops` | ci, cd, deploy, docker, k8s | CI/CD, deployment |
| `migration` | миграция, migrat, переход | System migration |

## Prompt Tiers

### Core (Immutable Baseline)

Located: `prompts/core/`

| Prompt | Purpose |
|--------|---------|
| `promt-feature-add.md` | Adding new functionality |
| `promt-bug-fix.md` | Fixing bugs |
| `promt-refactoring.md` | Code restructuring |
| `promt-security-audit.md` | Security assessment |
| `promt-quality-test.md` | Quality assurance |

### Universal

Located: `prompts/universal/`

Contains:
- `ai_agent_prompts/` — General purpose prompts
- `mpv_stages/` — 7-stage MPV pipeline

### Plugin Packs

Located: `prompts/packs/`

| Pack | Triggers | Purpose |
|------|----------|---------|
| `k8s-pack` | deploy, k8s, pod, helm | Kubernetes operations |
| `ci-cd-pack` | github, actions, ci, cd | CI/CD pipelines |
| `uiux-pack` | tailwind, shadcn, colors, typography | Design system |
| `pinescript-v6` | pinescript, tradingview | TradingView scripts |

### Agent-Specific

Located: `prompts/agents/`

| Agent | Prompts |
|-------|---------|
| `architect` | create_adr, promt-architect-design |
| `developer` | promt-feature-add |
| `reviewer` | promt-llm-review |
| `migration` | promt-migration-planner, promt-migration-implementation, promt-migration-review |

## MCP Tools

| Tool | Description |
|------|-------------|
| `p9i` | **Unified router** — Natural language intent detection |
| `run_prompt` | Execute single prompt |
| `run_prompt_chain` | Execute multi-stage chain |
| `list_prompts` | List available prompts |
| `get_prompt` | Get prompt by name |
| `get_project_memory` | Retrieve project context |
| `save_project_memory` | Store project context |

## Routing Priority

```
1. COMMAND (/help, /exit, /clear)
2. PROMPT_CMD (/prompt list, /prompt save)
3. PACK (k8s, ci-cd, uiux packs)
4. AGENT_TASK (multi-agent orchestration)
5. NL_QUERY (simple queries)
6. SYSTEM (init p9i, adapt to project)
```

## Context-Aware Routing

The router uses context-aware disambiguation:

- `"проверь архитектуру"` → `architect` (not `reviewer`)
- `"проверь код"` → `reviewer`

This is achieved by checking for architecture-related keywords alongside action keywords.

## Quick Start

```bash
# Claude Code MCP integration
# The p9i project already has .mcp.json configured:
cat /home/worker/p9i/.mcp.json

# To enable in Claude Code:
# 1. Navigate to the p9i project directory when starting Claude Code
# 2. Or add "p9i" to enabledMcpjsonServers in ~/.claude/settings.json:
{
  "enabledMcpjsonServers": ["p9i"]
}
```

## Documentation

| Document | Description |
|----------|-------------|
| [ADR Index](explanation/adr/ADR_INDEX.md) | Architecture Decision Records |
| [MPV Pipeline](how-to/MPV.md) | 7-stage development pipeline |
| [Bottlenecks](how-to/BOTTLENECKS_ANALYSIS.md) | Known issues |

---

*Last Updated: 2026-03-31*
