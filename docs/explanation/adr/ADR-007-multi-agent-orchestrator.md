# ADR-007: Multi-Agent Orchestrator Architecture

## Статус решения
**Implemented** ✅ | 2026-03-24 | Merged to main (PR #2)

## Прогресс реализации
✅ Полностью реализован (7 агентов)

## Context

Need to implement a multi-agent system where specialized AI agents work together through shared memory, managed by a central router (Siri-like interface).

## Decision

We will implement a multi-agent orchestration system with:

### Agent Types

| Agent | Prompts | Function |
|-------|---------|----------|
| **Architect** | promt-architect-design, create_adr, promt-architect-review | System design, ADRs |
| **Developer** | promt-feature-add, promt-bug-fix, promt-refactoring | Code generation |
| **Reviewer** | promt-llm-review, promt-security-audit, promt-quality-test | Code review, security |
| **Designer** | promt-ui-generator, generate_tailwind, generate_shadcn | UI/UX generation |
| **DevOps** | promt-ci-cd-pipeline, promt-onboarding | CI/CD, deployment |

### Architecture

```
                    ┌─────────────────┐
                    │   p9i Siri    │  ← Central Router
                    └────────┬────────┘
                             │
    ┌────────────────────────┼────────────────────────┐
    │                        │                        │
    ▼                        ▼                        ▼
┌─────────┐           ┌─────────────┐           ┌─────────────┐
│Architect│           │  Developer   │           │  Reviewer   │
│ Agent   │           │   Agent     │           │   Agent     │
└────┬────┘           └──────┬──────┘           └──────┬──────┘
     │                       │                        │
     └───────────────────────┼────────────────────────┘
                             │
                             ▼
                   ┌─────────────────┐
                   │  Shared Memory  │  ← Project Context
                   │  (MemoryService) │
                   └─────────────────┘
```

### Workflow Examples

**Simple request:**
```
User: "Добавь функцию логирования"
→ p9i_siri → Developer Agent → Result
```

**Complex request:**
```
User: "Создай систему авторизации"
→ p9i_siri → Architect Agent (design)
           → Developer Agent (code)
           → Reviewer Agent (security check)
           → Result with all outputs
```

## Implementation

### 1. Agent Prompts Structure
```
prompts/agents/
├── architect/
│   ├── promt-architect-design.md
│   ├── promt-architect-review.md
│   └── create_adr.md
├── developer/
│   ├── promt-feature-add.md
│   ├── promt-bug-fix.md
│   └── promt-refactoring.md
├── reviewer/
│   ├── promt-llm-review.md
│   ├── promt-security-audit.md
│   └── promt-quality-test.md
└── designer/
    └── promt-ui-generator.md
```

### 2. MCP Tools

| Tool | Description |
|------|-------------|
| `p9i_siri` | Central router for all requests |
| `architect_design` | Architect agent - system design |
| `create_adr` | Create ADR document |
| `developer_code` | Developer agent - code generation |
| `reviewer_check` | Reviewer agent - code review |
| `designer_ui` | Designer agent - UI generation |

### 3. AgentOrchestrator Class

```python
class AgentOrchestrator:
    """Central router managing agent interactions through memory"""

    def __init__(self):
        self.agents = {...}
        self.memory = MemoryService()

    async def route(self, request: str) -> dict:
        """Route request to appropriate agents"""
```

## Consequences

- **Positive:** Specialized agents for each domain
- **Positive:** Shared memory for context continuity
- **Positive:** Central router for easy interaction
- **Negative:** More complex orchestration
- **Negative:** Requires careful prompt engineering

## Alternatives Considered

- Single agent with all prompts (rejected - no specialization)
- No shared memory (rejected - loses context)
- Direct tool calls only (rejected - loses natural language)

## See Also
- [ADR-004: Deep-Project Integration](ADR-004-deep-project-integration.md) — Orchestration pipeline
- [ADR-005: UI/UX Integration](ADR-005-ui-ux-integration.md) — Designer agent tools
- [ADR-006: Figma Integration](ADR-006-figma-integration.md) — Design resources

---
*Last Updated: 2026-03-24*
