# ADR-015: Code Explorer Agent — Deep Code Analysis Capabilities

## Status

**Proposed** | 2026-04-01

## Context

### Problem Statement

Claude Code has a specialized `code-explorer` agent that provides deep codebase analysis by tracing execution paths, mapping architecture layers, and documenting dependencies. This enables developers to understand how specific features work by tracing implementation from entry points to data storage.

p9i currently lacks these deep code analysis capabilities. The existing agents (`architect`, `developer`, `reviewer`, `designer`, `devops`) provide good coverage for generation and review tasks, but cannot answer questions like:

- "How does authentication flow through this codebase?"
- "What are all the entry points to this API?"
- "Which modules depend on the legacy payment processor?"
- "Show me the data flow from user input to database save"
- "What could break if I change this utility function?"

### Reference: Claude Code code-explorer Agent

The code-explorer agent provides:

| Capability | Description |
|------------|-------------|
| **Feature Discovery** | Find entry points (APIs, UI, CLI), locate core implementation files |
| **Code Flow Tracing** | Follow call chains from entry to output, trace data transformations |
| **Architecture Analysis** | Map abstraction layers, identify design patterns, document interfaces |
| **Implementation Details** | Key algorithms, error handling, performance considerations |
| **Dependency Documentation** | External/internal dependencies, cross-cutting concerns |

**Tools Used:** Glob, Grep, Read, LS, WebFetch, WebSearch

### Strategic Fit

This ADR aligns with ADR-007 (Multi-Agent Orchestrator) by adding a new specialized agent for deep code analysis. The Code Explorer Agent complements rather than replaces existing agents:

| Agent | Primary Focus | Code Explorer Enhancement |
|-------|---------------|---------------------------|
| `architect` | System design, ADRs | Architecture layer mapping, pattern recognition |
| `developer` | Code generation | Entry point identification, call chain understanding |
| `reviewer` | Code review, security | Execution tracing, impact analysis, security vulnerability deep scan |
| `designer` | UI/UX | Component dependency visualization |
| `devops` | CI/CD, K8s | Dependency graph for deployment |

---

## Decisions

### Architecture Pattern: Event-Driven Microservices

**Chosen Pattern:** `event_driven_microservices_with_shared_infrastructure`

**Rationale:** Code Explorer requires:
- CPU-intensive parsing (AST generation, analysis)
- Low-latency operations (search, graph queries)
- Async processing (indexing, batch analysis)

Event-driven microservices enable:
- Independent scaling of components
- Loose coupling between services
- Horizontal growth with increasing codebase size

---

### Core Components

#### 1. API Gateway

**Technology:** FastAPI + Redis caching + nginx

**Responsibilities:**
- Authentication & authorization (JWT, API keys)
- Rate limiting and quotas per user/team
- Request routing to appropriate services
- Response aggregation from multiple sources
- Caching layer for frequent queries

**Scaling:** Horizontal (stateless, 3-5 replicas)

---

#### 2. Code Indexer Service

**Technology:** Python + Tree-sitter + LSP clients + PostgreSQL

**Responsibilities:**
- Repository cloning and management
- Language detection and file parsing (AST generation)
- Symbol extraction (functions, classes, imports)
- Metadata indexing for search
- Incremental index updates via webhooks
- Cross-file reference tracking

**Scaling:** Horizontal (worker-based, 2-4 workers per language)

**Interfaces:**
- gRPC: `indexer.IndexService.IndexRepository`
- REST: `POST /api/v1/repositories`
- Events: `code.index.requested`, `code.index.completed`, `code.changed`

---

#### 3. Search Service

**Technology:** FastAPI + Qdrant/Milvus + Redis + sentence-transformers

**Responsibilities:**
- Hybrid search (keyword + semantic)
- Embedding generation and storage
- Search result ranking and scoring
- Query understanding and expansion
- Faceted search (by language, file type, date)
- Search suggestions and autocomplete

**Scaling:** Horizontal (replicas with sharded vector DB)

**Interfaces:**
- REST: `/api/v1/search`
- Events: `search.executed`, `search.analytics`

---

#### 4. Dependency Graph Service

**Technology:** Python + Neo4j/RedisGraph + NetworkX

**Responsibilities:**
- Graph construction from indexed code
- Graph storage with versioning
- Traversal queries (BFS, DFS)
- Impact analysis (forward/backward reachability)
- Cyclic dependency detection
- Graph diffing between commits

**Scaling:** Vertical (graph DB scales with data) + horizontal (query replicas)

**Interfaces:**
- REST: `/api/v1/graph/*`
- Events: `graph.updated`, `graph.impact.calculated`

---

#### 5. Execution Tracer Service

**Technology:** Python + Joern + custom AST analyzers + NetworkX

**Responsibilities:**
- Entry point identification (API handlers, CLI entrypoints)
- Data flow analysis (sources → transformations → sinks)
- Control flow graph generation
- Taint analysis for security
- Path finding between arbitrary code points
- Call graph construction

**Scaling:** Horizontal (partitioned by repository)

**Interfaces:**
- REST: `/api/v1/trace/*`
- Events: `trace.completed`, `trace.hotspot.detected`

---

#### 6. Analysis Orchestrator

**Technology:** Python + Temporal/Arvo + Redis

**Responsibilities:**
- Multi-step analysis workflow orchestration
- Parallel execution coordination
- Result aggregation and deduplication
- Retry logic and error handling
- Progress tracking for long-running analyses
- Caching and memoization of intermediate results

**Scaling:** Horizontal (multiple orchestrator instances)

---

#### 7. Security Scanner Service

**Technology:** Python + Semgrep + custom rules + CodeQL wrapper

**Responsibilities:**
- Vulnerability pattern matching
- Taint analysis (user input → sink)
- OWASP/CWE rule enforcement
- Secrets detection
- Dependency vulnerability checking
- Security report generation

**Scaling:** Horizontal (parallel file scanning)

**Interfaces:**
- REST: `/api/v1/security/scan`
- Events: `security.issue.found`

---

#### 8. Code Analysis Agent (Primary Deliverable)

**Technology:** Python + LangChain/LlamaIndex + Claude/GPT-4 API

**Responsibilities:**
- Natural language code queries
- Context-aware analysis results synthesis
- Architecture explanation and documentation
- Code review with deep understanding
- Recommendation generation
- Multi-hop reasoning across code

**Scaling:** Horizontal (stateless agent replicas)

**Interfaces:**
- REST: `/api/v1/agent/*`
- WebSocket: `/ws/agent/chat`

---

### Data Flows

```
code_indexing:
Webhook (git push) → API Gateway → Code Indexer → Tree-sitter/LSP parsing
                 → PostgreSQL metadata + Graph DB edges + Vector DB embeddings

search_query:
User query → API Gateway → Search Service → Vector DB (semantic) + PostgreSQL (metadata)
         → Ranked results → User

impact_analysis:
Code change → API Gateway → Analysis Orchestrator → Dependency Graph Service
           → Reachability query → Impact report

security_scan:
Trigger (PR/webhook) → Analysis Orchestrator → Execution Tracer → Security Scanner
                     → SAST patterns → Vulnerability report

agent_query:
Natural language → API Gateway → Code Analysis Agent
                → [Search + Graph + Tracer] orchestrations
                → Synthesized response
```

---

### Event Flows

```json
{
  "indexing_pipeline": "code.changed → code.index.requested → code.indexing.started → code.indexed → code.search.updated",
  "analysis_pipeline": "analysis.requested → analysis.orchestrated → [trace.completed, graph.updated, scan.completed] → analysis.finished",
  "notification_pipeline": "security.issue.found → notification.created → user.notified"
}
```

---

### Infrastructure Requirements

| Component | Technology | Scaling |
|-----------|------------|---------|
| **Compute** | Kubernetes (EKS/GKE) | HPA enabled |
| **Relational DB** | PostgreSQL 15 (RDS) | 100GB SSD, read replicas |
| **Graph DB** | Neo4j / RedisGraph | 500GB NVMe |
| **Vector DB** | Qdrant / Milvus | 200GB NVMe |
| **Cache** | Redis Cluster | 3 nodes, 16GB each |
| **Messaging** | Apache Kafka | 3+ brokers |
| **Object Storage** | S3/GCS | Large artifacts |
| **Monitoring** | Prometheus + Grafana + Jaeger + Loki | Sidecar + central |

---

## Implementation Phases

### Phase 1: Foundation & Core Indexing (2-3 months)

**Team:** 3-4 engineers (1 ML, 2 backend, 1 DevOps)

**Goals:**
- Basic code indexing pipeline for Python and JavaScript
- Cross-file reference tracking
- Simple keyword search
- Infrastructure bootstrap (K8s, PostgreSQL, Redis)

**Deliverables:**
- [ ] Code Indexer Service with Tree-sitter parsing
- [ ] PostgreSQL schema for code metadata
- [ ] Basic REST API for repository management
- [ ] Search API with keyword matching
- [ ] CI/CD pipeline with staging environment

**Success Criteria:**
- Successfully index repositories up to 10k files
- Cross-file references correctly tracked
- Search returns relevant results within 500ms
- Indexing throughput > 100 files/second

---

### Phase 2: Search & Graph Services (2-3 months)

**Team:** 2-3 engineers (1 ML, 1 backend, 1 frontend)

**Goals:**
- Semantic search with embeddings
- Dependency graph visualization
- Impact analysis capabilities

**Deliverables:**
- [ ] Vector DB integration (Qdrant/Milvus)
- [ ] Hybrid search (keyword + semantic)
- [ ] Graph DB integration (Neo4j/RedisGraph)
- [ ] Basic visualization API
- [ ] Impact analysis endpoint

---

### Phase 3: Execution Tracer & Security (3-4 months)

**Team:** 2-3 engineers (static analysis expertise)

**Goals:**
- Data flow analysis
- Security vulnerability scanning
- Entry point identification

**Deliverables:**
- [ ] Execution Tracer Service
- [ ] Taint analysis for security
- [ ] Security Scanner with Semgrep
- [ ] Call graph generation
- [ ] Path finding between code points

---

### Phase 4: Code Analysis Agent (2-3 months)

**Team:** 2 engineers (ML + backend)

**Goals:**
- Natural language code queries
- LLM-powered analysis synthesis
- WebSocket chat interface

**Deliverables:**
- [ ] Code Analysis Agent
- [ ] WebSocket chat interface
- [ ] Multi-hop reasoning
- [ ] Context-aware recommendations

---

## Prioritized Feature Backlog

| Priority | Feature | Complexity | Impact |
|----------|---------|------------|--------|
| 1 | Semantic Search (embeddings) | Medium | High |
| 2 | Cross-File Analysis | Medium | High |
| 3 | Dependency Graph | Medium | High |
| 4 | Impact Analysis | High | Very High |
| 5 | Execution Path Tracer | High | High |
| 6 | Security Vulnerability Scanner | Medium | High |
| 7 | Architecture Pattern Recognition | Medium | Medium |
| 8 | Code Health Metrics Dashboard | Low | Medium |

---

## Alternatives Considered

### 1. Extend Existing reviewer Agent

**Pros:** No new agent, simpler orchestration
**Cons:** Overloads reviewer with too many responsibilities, violates single responsibility principle

### 2. Use External Code Analysis Tools (Joern, Semgrep)

**Pros:** Proven technology, less custom code
**Cons:** Tight coupling, harder to customize, limited LLM integration

### 3. Build Monolithic Service

**Pros:** Simpler deployment, less operational overhead
**Cons:** Cannot scale components independently, tight coupling, single point of failure

---

## Consequences

### Positive

- **Deep code understanding:** Developers can trace how data flows through the codebase
- **Improved architecture decisions:** architect agent gains better context
- **Enhanced security:** Security scanner catches vulnerabilities earlier
- **Faster onboarding:** New team members understand codebase faster
- **Reduced bugs:** Impact analysis prevents breaking changes

### Negative

- **Infrastructure complexity:** More services to deploy and maintain
- **Operational overhead:** Graph DB and Vector DB require specialized knowledge
- **Indexing latency:** Initial indexing takes time for large codebases
- **Resource costs:** More infrastructure = higher cloud costs

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Graph DB performance at scale | Medium | High | Start with RedisGraph, upgrade to Neo4j if needed |
| Embedding quality varies by language | Medium | Medium | Start with Python/JS, expand later |
| Index maintenance complexity | High | Medium | Incremental updates via webhooks only |
| LLM hallucinations in analysis | Low | High | Human-in-the-loop for critical decisions |

---

## Open Questions

1. **Multi-tenancy:** Should repositories from different organizations share infrastructure or be isolated?
2. **Index versioning:** How to handle code that changes between analysis and review?
3. **Language support priority:** Python/JS first, or prioritize languages used by majority of users?
4. **Pricing model:** Per-repo pricing, per-user pricing, or usage-based?

---

## Related ADRs

- [ADR-007: Multi-Agent Orchestrator](ADR-007-multi-agent-orchestrator.md) — Existing agent framework
- [ADR-014: LLM-based Prompt Selection](ADR-014-llm-prompt-selection.md) — Embedding technology

---

## References

- [Claude Code code-explorer agent](https://github.com/anthropics/claude-code/blob/main/plugins/feature-dev/agents/code-explorer.md)
- [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) — Parser tool
- [Joern](https://joern.io/) — Static analysis platform
- [Semgrep](https://semgrep.dev/) — Static analysis tool
- [Qdrant](https://qdrant.tech/) — Vector similarity search engine
- [Neo4j](https://neo4j.com/) — Graph database
