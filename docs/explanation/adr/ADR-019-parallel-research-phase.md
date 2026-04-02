# ADR-019: Parallel Research Phase for Architect Agent

## Status
Proposed | 2025-01-23

## Context

### Current Architecture

The current architect agent follows a **sequential research pattern**, where a single explorer agent investigates all architectural concerns one after another:

```
┌─────────────────────────────────────────────────────────────┐
│                    Architect Agent                          │
│                                                             │
│  ┌─────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │  Query  │───▶│   Single    │───▶│   Architecture      │  │
│  │parsing  │    │  Explorer   │    │   Recommendation    │  │
│  └─────────┘    │  (Sequential│    │                     │  │
│                 │   Research)  │    │                     │  │
│                 └─────────────┘    └─────────────────────┘  │
│                        │                                     │
│                        ▼                                     │
│              ┌─────────────────┐                             │
│              │  Tech Stack     │                             │
│              │  Code Patterns  │                             │
│              │  Best Practices │                             │
│              │  (All sequentially)│                           │
│              └─────────────────┘                             │
└─────────────────────────────────────────────────────────────┘
```

### Identified Problems

1. **Linear Time Complexity**: Research time grows linearly with the number of architectural concerns
2. **No Parallelism**: Independent research topics are processed sequentially
3. **Single Point of Failure**: One explorer agent handles all failure cases
4. **Limited Coverage**: Single perspective on complex architectural decisions
5. **Latency Bottleneck**: User waits for complete sequential research before receiving any insights

### Requirements

- Reduce overall research time through parallelization
- Maintain high-quality architectural recommendations
- Enable independent exploration of different concern domains
- Preserve coherent synthesis of findings

---

## Decision

### Proposed Solution: Three-Explorer Parallel Research Pattern

Implement a **parallel research phase** using three specialized explorer agents that simultaneously investigate different architectural dimensions:

```
┌─────────────────────────────────────────────────────────────────────┐
│                       Architect Agent                               │
│                                                                     │
│  ┌─────────┐                                                        │
│  │  Query  │                                                        │
│  │parsing  │                                                        │
│  └────┬────┘                                                        │
│       │                                                             │
│       ▼                                                             │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │              PARALLEL RESEARCH PHASE                        │     │
│  │                                                              │     │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │     │
│  │  │  Explorer 1     │  │  Explorer 2     │  │ Explorer 3  │  │     │
│  │  │  ───────────    │  │  ───────────    │  │ ─────────── │  │     │
│  │  │  Tech Stack     │  │  Code Patterns  │  │ Best        │  │     │
│  │  │  Analysis       │  │  & Structure    │  │ Practices   │  │     │
│  │  │                 │  │                 │  │ & Patterns  │  │     │
│  │  └────────┬────────┘  └────────┬────────┘  └──────┬──────┘  │     │
│  │           │                    │                   │         │     │
│  │           └────────────────────┼───────────────────┘         │     │
│  │                                ▼                              │     │
│  │                    ┌───────────────────┐                      │     │
│  │                    │  SYNTHESIS PHASE │                      │     │
│  │                    │  (Sequential)    │                      │     │
│  │                    └─────────┬─────────┘                      │     │
│  └──────────────────────────────┼───────────────────────────────┘     │
│                                 │                                     │
│                                 ▼                                     │
│                    ┌─────────────────────┐                            │
│                    │   Architecture      │                            │
│                    │   Recommendation    │                            │
│                    └─────────────────────┘                            │
└─────────────────────────────────────────────────────────────────────┘
```

### Explorer Agent Specializations

| Explorer | Domain Focus | Key Responsibilities |
|----------|--------------|---------------------|
| **Explorer 1** | Technology Stack | Language features, framework capabilities, dependencies, tooling |
| **Explorer 2** | Code Patterns & Structure | Architectural patterns, design patterns, module organization |
| **Explorer 3** | Best Practices | Performance optimization, security, maintainability, testing |

### File Structure

```
prompts/
├── architect/
│   ├── promt-architect-parallel-research.md    # Main orchestration prompt
│   ├── explorer-1-tech-stack.md                # Tech stack research prompt
│   ├── explorer-2-code-patterns.md             # Code patterns research prompt
│   └── explorer-3-best-practices.md            # Best practices research prompt
```

### Research Flow

1. **Parallel Execution**: All three explorers run simultaneously
2. **Independent Context**: Each explorer maintains its own research context
3. **Structured Output**: Each explorer produces structured findings
4. **Sequential Synthesis**: Architect agent synthesizes all findings in order

---

## Consequences

### Positive

- **3x faster research phase** through true parallelization
- **Improved coverage** with specialized focus per explorer
- **Better fault isolation** — one explorer failure doesn't block others
- **Richer perspectives** — multiple independent analyses
- **Maintained quality** — synthesis ensures coherent recommendations
- **Extensibility** — easy to add more explorers for additional domains

### Negative

- **Increased complexity** — orchestration layer for parallel execution
- **Higher resource usage** — three LLM calls instead of one
- **Potential redundancy** — some overlap in research topics
- **Context management** — need to aggregate multiple contexts
- **Synchronization overhead** — need to wait for all explorers before synthesis

### Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Inconsistent findings across explorers | Clear domain boundaries in prompts |
| Missing cross-domain insights | Synthesis phase explicitly looks for connections |
| Timeout if one explorer hangs | Individual timeout per explorer |
| Conflicting recommendations | Synthesis phase resolves conflicts with clear rationale |

---

## Implementation Notes

### promt-architect-parallel-research.md Structure

```markdown
# Architect Agent - Parallel Research Orchestration

## Role
You are the Architect Agent orchestrator...

## Research Phase
Launch THREE parallel research agents:

1. [Explorer 1: Tech Stack](explorer-1-tech-stack.md)
2. [Explorer 2: Code Patterns](explorer-2-code-patterns.md)
3. [Explorer 3: Best Practices](explorer-3-best-practices.md)

## Synthesis Phase
After receiving all explorer results:
1. Merge findings by category
2. Identify conflicts and resolve
3. Generate unified recommendations
```

### Success Metrics

- Research phase latency reduced by 60-70%
- Quality score maintained at >90% vs sequential baseline
- Architectural recommendation coverage improved by 25%

---

## Related ADRs

- ADR-001: Initial Architect Agent Design
- ADR-015: Explorer Agent Architecture
- ADR-018: Multi-Agent Orchestration Patterns
