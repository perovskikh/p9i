# p9i Documentation

> AI Prompt System MCP Server — Universal prompt management from idea to production.

## Quick Links

| Section | Description |
|---------|-------------|
| [AI Agent Prompts](ai-agent-prompts/README.md) | Prompt registry, agents, routing |
| [ADR Index](explanation/adr/ADR_INDEX.md) | Architecture Decision Records |
| [MPV Pipeline](how-to/MPV.md) | 7-stage development pipeline |
| [Bottlenecks](how-to/BOTTLENECKS_ANALYSIS.md) | Known issues and analysis |
| [MCP Config](MCP-CONFIG.md) | MCP server configuration |
| [Env Variables](reference/env-variables.md) | Environment variables reference |

## Architecture

```
User Request → P9iRouter → AgentRouter → HybridPromptRouter → Prompt
```

**Key Components:**
- **P9iRouter** — Natural language intent classification (no LLM!)
- **AgentRouter** — Agent detection (8 specialized agents)
- **HybridPromptRouter** — Cascade routing: rule → semantic → LLM

## 8 Agents

| Agent | Purpose | Key Prompts |
|-------|---------|-------------|
| `full_cycle` | Complete pipeline | promt-feature-add |
| `architect` | Architecture, ADRs | create_adr, promt-architect-design |
| `developer` | Code generation | promt-feature-add, promt-bug-fix |
| `reviewer` | Code review | promt-llm-review, promt-security-audit |
| `designer` | UI/UX | promt-ui-generator |
| `devops` | CI/CD, K8s | promt-ci-cd-pipeline |
| `migration` | System migration | promt-migration-planner |

## MCP Tools (20+)

**Core:**
- `p9i` — Unified router (natural language intent)
- `run_prompt` / `run_prompt_chain` — Execute prompts
- `list_prompts` / `get_prompt` — Query prompts

**Project Memory:**
- `get_project_memory` / `save_project_memory` — Context management
- `adapt_to_project` — Auto-detect stack

**Auth:**
- `generate_jwt_token` / `validate_jwt_token` / `revoke_jwt_token`

## Getting Started

```bash
# Start the server
python -m src.api.server

# Or with Docker
docker compose up -d
```

## Documentation Sections

```
docs/
├── ai-agent-prompts/   # Prompt registry, agents, routing
├── explanation/         # ADR and architecture docs
├── how-to/             # Guides (MPV, bottlenecks)
├── reference/          # API reference
└── reports/            # Implementation reports
```

---

*Last Updated: 2026-03-31*
