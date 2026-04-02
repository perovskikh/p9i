# ADR-014: LLM-based Prompt Selection with Embeddings

## Metadata

| Field | Value |
|-------|-------|
| **Number** | ADR-014 |
| **Status** | Proposed (Partially Implemented in p9i) |
| **Date** | 2026-04-01 |
| **Last Updated** | 2026-04-02 |
| **Author** | p9i team |
| **Supersedes** | — |
| **Reviewed by** | — |

## Status Summary

### Что реализовано в p9i

| Component | Status | Notes |
|-----------|--------|-------|
| **HybridPromptRouter** | ✅ Implemented | Rule-based + Semantic + LLM cascade |
| **SemanticRouter** | ✅ Implemented | Cosine similarity matching |
| **PromptRegistry** | ✅ Implemented | Prompt entry management |
| **DefaultEmbedder** | ⚠️ Fallback | Hash-based, NOT OpenRouter bge-m3 |
| **In-memory caching** | ✅ Implemented | 5-minute TTL |
| **Rule-based router** | ✅ Implemented | Keyword matching |

### Что НЕ реализовано

| Component | ADR-014 Plan | Status |
|-----------|--------------|--------|
| **OpenRouter Embeddings** | bge-m3 model | ❌ Not implemented (DefaultEmbedder fallback) |
| **Qdrant Vector Store** | **Local Helm** (NOT cloud!) | ❌ Not implemented |
| **Redis Embedding Cache** | 7-day TTL | ❌ Not implemented |
| **API Endpoints** | /api/v1/search | ❌ Not implemented |

---

## Context

### Проблема

Текущая система p9i использует **P9iRouter** для маршрутизации запросов на основе ключевых слов (keyword-based routing). Это решение работает быстро и бесплатно, но имеет ограничения:

1. **Нет семантического понимания** — запрос "создай кнопку" и "добавь компонент интерфейса" могут маршрутизироваться по-разному
2. **Ограниченный search** — невозможно искать промты по смыслу
3. **Зависимость от точных ключевых слов** — опечатка или синоним ломает маршрутизацию

### Обоснование

Для улучшения качества поиска и маршрутизации необходимо внедрить **RAG-пайплайн** с использованием эмбеддингов для семантического поиска промтов.

---

## Decision

### Current p9i Architecture (Implemented)

```
┌─────────────────────────────────────────────────────────────┐
│                    P9iRouter (Keyword-based)                 │
│            NO LLM for routing - FREE & FAST                  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                 HybridPromptRouter                            │
│         (Rule-based → Semantic → LLM Fallback)               │
└──────────┬─────────────────────┬────────────────────────────┘
           │                     │
┌──────────▼──────────┐ ┌────────▼─────────────────────────────┐
│  RuleBasedRouter   │ │  SemanticRouter                       │
│  (Keyword match)   │ │  (Cosine similarity)                  │
└────────────────────┘ └──────────────────────────────────────┘
           │                     │
           │           ┌─────────▼─────────┐
           │           │  DefaultEmbedder  │
           │           │  (Hash-based)     │
           │           │  ⚠️ NOT OpenRouter│
           │           └───────────────────┘
           │
           └─────────┬───────────┘
                     │
           ┌─────────▼─────────┐
           │  In-Memory Cache  │
           │  (5 min TTL)      │
           └───────────────────┘
```

### Missing from ADR-014 Plan

```
┌─────────────────────────────────────────────────────────────┐
│                    ADR-014 Plan (NOT IMPLEMENTED)            │
└─────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                 Retrieval Service                             │
│            (Semantic Search + Caching)                        │
└──────────┬─────────────────────┬────────────────────────────┘
           │                     │
┌──────────▼──────────┐ ┌────────▼─────────────┐
│  Embedding Service │ │   Vector Store      │
│   (OpenRouter)     │ │   (Qdrant)          │ ❌ NOT IMPLEMENTED
└────────────────────┘ └─────────────────────┘
           │                     │
           └─────────┬───────────┘
                     │
           ┌─────────▼─────────┐
           │   Redis Cache     │ ❌ NOT IMPLEMENTED
           │   (7-day TTL)     │
           └───────────────────┘
```

---

## Implementation: p9i Cascade Router

### 1. HybridPromptRouter (`src/application/router/cascade/hybrid.py`)

**Status:** ✅ Implemented

```python
class HybridPromptRouter:
    """
    Hybrid router that combines rule-based, semantic, and LLM routing.

    Routing cascade:
      1. Rule-based (fast path) — if confidence >= 0.9
      2. Semantic (medium path) — if confidence >= 0.7
      3. LLM (slow path) — as last resort
    """
```

### 2. SemanticRouter (`src/application/router/cascade/semantic.py`)

**Status:** ✅ Implemented (uses DefaultEmbedder)

```python
class SemanticRouter(BaseRouter[RoutingResult]):
    """Semantic routing using embeddings with cosine similarity."""

    def __init__(self, embedder: EmbedderProtocol | None = None, threshold: float = 0.7):
        self._embedder = embedder or DefaultEmbedder()
        self._threshold = threshold
```

### 3. DefaultEmbedder (Fallback)

**Status:** ⚠️ Simple hash-based, NOT OpenRouter

```python
class DefaultEmbedder:
    """Simple hash-based embedding fallback."""

    def embed(self, text: str) -> list[float]:
        """Simple hash-based embedding fallback."""
        words = text.lower().split()
        vec = [0.0] * 64
        for i, word in enumerate(words[:64]):
            vec[i % 64] += hash(word) % 1000
        # Normalize
        magnitude = math.sqrt(sum(x * x for x in vec))
        if magnitude > 0:
            vec = [x / magnitude for x in vec]
        return vec
```

---

## Claude Code Comparison

### Claude Code Sourcemap Routing

Claude Code uses **keyword classification only** — no semantic search, no embeddings.

| Aspect | Claude Code | p9i Current | p9i + ADR-014 |
|--------|-------------|-------------|---------------|
| **Routing Type** | Built-in keyword | P9iRouter (keyword) | HybridPromptRouter |
| **Semantic Search** | ❌ No | ⚠️ Limited | ✅ Full (bge-m3) |
| **Vector Store** | ❌ No | ❌ No | ✅ Qdrant |
| **Embeddings** | ❌ No | ⚠️ DefaultEmbedder (hash) | ✅ OpenRouter bge-m3 |
| **LLM for Routing** | N/A | Optional fallback | Optional fallback |
| **Caching** | ❌ No | In-memory 5min | ✅ Redis 7-day |
| **Search API** | Built-in commands | MCP tools | ✅ /api/v1/search |

### Claude Code НЕ имеет:

```
❌ Semantic search — только keyword classification
❌ Vector embeddings — никаких
❌ Vector database — никакой
❌ External API для search — только встроенные команды
```

---

## Why p9i Will Be BETTER Than Claude Code

### После реализации ADR-014 полный стек:

```
┌─────────────────────────────────────────────────────────────┐
│                   p9i + ADR-014 Stack                        │
├─────────────────────────────────────────────────────────────┤
│  User Query                                                   │
│       │                                                       │
│       ▼                                                       │
│  ┌─────────────────────────────────────────────┐            │
│  │  P9iRouter (keyword) → fast path           │            │
│  └──────────────────┬──────────────────────────┘            │
│                    │                                          │
│       ┌────────────▼────────────┐                           │
│       │  HybridPromptRouter      │                           │
│       │  Rule (0.9) → Semantic   │                          │
│       │  (0.7) → LLM fallback    │                           │
│       └────────────┬────────────┘                           │
│                    │                                          │
│       ┌────────────▼────────────┐                           │
│       │  SemanticRouter         │                           │
│       │  bge-m3 embeddings      │  ←─ OpenRouter FREE TIER │
│       └────────────┬────────────┘                           │
│                    │                                          │
│       ┌────────────▼────────────┐                           │
│       │  Qdrant Vector Store    │  ←─ Persistent storage   │
│       │  Cosine similarity      │                           │
│       └────────────┬────────────┘                           │
│                    │                                          │
│       ┌────────────▼────────────┐                           │
│       │  Redis 7-day cache     │  ←─ Low latency          │
│       └─────────────────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

### Technical Advantages

| Feature | Claude Code | p9i + ADR-014 | Winner |
|---------|------------|----------------|--------|
| **Semantic Search** | ❌ | ✅ bge-m3 | p9i |
| **Vector Storage** | ❌ | ✅ Qdrant | p9i |
| **7-day Cache** | ❌ | ✅ Redis | p9i |
| **API Endpoint** | ❌ | ✅ /api/v1/search | p9i |
| **Multi-lingual** | N/A | ✅ bge-m3 supports RU | p9i |
| **Setup Complexity** | Zero | Medium | Claude Code |

### Cost Analysis (OpenRouter Free Tier)

| Operation | Cost | Limit |
|-----------|------|-------|
| bge-m3 embeddings | FREE | 100 req/day |
| Semantic search | FREE | 100 req/day |
| Total | **$0** | Для MVP достаточно |

### Latency Comparison

| Scenario | Claude Code | p9i + ADR-014 |
|----------|-------------|----------------|
| First query | ~50ms | ~200ms (embedding + Qdrant) |
| Cached query | N/A | ~10ms (Redis hit) |
| After 7-day | N/A | Fresh embed |

---

## Conclusion: YES, We Will Be Better

> **Если мы реализуем ADR-014 (bge-m3 + Qdrant + Redis), p9i превзойдёт Claude Code Sourcemap для semantic prompt search.**

### Что мы получим:

1. ✅ **Semantic Search** — Claude Code вообще не имеет
2. ✅ **Vector Storage** — persistent nearest-neighbor search
3. ✅ **7-day Redis Cache** — 低 latency, снижает cost
4. ✅ **HTTP API** — для внешних клиентов
5. ✅ **Multi-lingual** — bge-m3 поддерживает русский

### Единственный trade-off:

| Claude Code | p9i + ADR-014 |
|-------------|---------------|
| Zero config | Need to deploy Qdrant + Redis |
| Simple | 3 additional services |

### Recommendation:

**Implement Phase 2 ADR-014** — это даст нам превосходство над Claude Code в semantic search capability.

---

## API Contract (ADR-014 Plan)

### Endpoints

#### POST /api/v1/search

```json
// Request
{
  "query": "создай кнопку с shadow effect",
  "filters": {
    "category": "ui",
    "language": "ru",
    "complexity": "simple"
  },
  "limit": 10,
  "include_scores": true
}

// Response
{
  "results": [
    {
      "id": "uuid",
      "title": "UI Button Generator",
      "content": "Сгенерируй кнопку...",
      "score": 0.89,
      "metadata": {
        "category": "ui",
        "language": "ru"
      }
    }
  ],
  "total": 5,
  "query_time_ms": 45
}
```

#### POST /api/v1/prompts (для индексации)

```json
{
  "title": "UI Button Generator",
  "content": "Сгенерируй кнопку с заданным стилем...",
  "category": "ui",
  "language": "ru",
  "tags": ["button", "css", "tailwind"]
}
```

---

## Qdrant: Local Deployment (REPLACING Cloud)

### Why Local Qdrant?

| Aspect | Qdrant Cloud | Local Qdrant |
|--------|-------------|--------------|
| **API Key** | Required | ❌ Not needed |
| **Cost** | $25+/month | **$0** |
| **Data Location** | External | **Local (same cluster)** |
| **Latency** | ~50ms | **~5ms** |
| **Control** | Limited | **Full** |
| **Backup** | Managed | **Your responsibility** |

### Qdrant Helm Chart

**Source:** [qdrant/qdrant-helm](https://github.com/qdrant/qdrant-helm)

```bash
# Install Qdrant via Helm
helm repo add qdrant https://qdrant.github.io/qdrant-helm
helm repo update
helm upgrade -i qdrant qdrant/qdrant -n p9i --create-namespace
```

### Qdrant Helm Values (production-ready)

```yaml
# k8s/qdrant/values.yaml
replicaCount: 1

image:
  repository: docker.io/qdrant/qdrant
  tag: v1.7.4
  pullPolicy: IfNotPresent

persistence:
  enabled: true
  accessModes: ["ReadWriteOnce"]
  size: 10Gi
  storageClassName: local-path  # Use local-path or your storage class

resources:
  limits:
    cpu: "1"
    memory: 2Gi
  requests:
    cpu: "250m"
    memory: 512Mi

service:
  type: ClusterIP
  ports:
    - name: http
      port: 6333
      targetPort: 6333
    - name: grpc
      port: 6334
      targetPort: 6334

config:
  cluster:
    enabled: true
```

### Kubernetes Manifest

```yaml
# k8s/qdrant/Chart.yaml
apiVersion: v2
name: qdrant
version: 1.0.0
appVersion: "1.7.4"
dependencies:
  - name: qdrant
    version: "1.0.0"
    repository: "https://qdrant.github.io/qdrant-helm"
```

### Environment Variables (UPDATED)

```bash
# OpenRouter (Embeddings) — FREE tier
OPENROUTER_API_KEY=sk-or-v1-xxx  # Get from openrouter.ai
EMBEDDING_MODEL=bge-m3
EMBEDDING_DIMENSIONS=1024

# Qdrant (LOCAL via Helm) — NO API KEY NEEDED
QDRANT_URL=http://qdrant.p9i.svc.cluster.local:6333
QDRANT_COLLECTION=prompts

# Redis (Cache)
REDIS_HOST=redis
REDIS_PORT=6379
EMBEDDING_CACHE_TTL=604800    # 7 days
SEARCH_CACHE_TTL=300           # 5 minutes
```

### Architecture After Changes

```
┌─────────────────────────────────────────────────────────────┐
│                   p9i + ADR-014 Stack                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Kubernetes Cluster (p9i namespace)                  │   │
│  │                                                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │   │
│  │  │    p9i      │  │   qdrant    │  │   redis   │  │   │
│  │  │   (MCP)     │──│  (vector)   │  │  (cache)  │  │   │
│  │  │              │  │   :6333     │  │   :6379   │  │   │
│  │  └─────────────┘  └─────────────┘  └───────────┘  │   │
│  │         │                  │                 │        │   │
│  └─────────│──────────────────│─────────────────│────────┘   │
│            │                  │                 │             │
│            └──────────────────┴─────────────────┘             │
│                          │                                   │
│              ┌───────────▼───────────┐                      │
│              │  OpenRouter API       │                      │
│              │  (bge-m3 embeddings) │                      │
│              │  FREE tier: 100/day   │                      │
│              └───────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: MVP (2-3 weeks) — PARTIALLY COMPLETE

| Component | Status | Notes |
|-----------|--------|-------|
| **HybridPromptRouter** | ✅ Done | Rule-based + Semantic + LLM cascade |
| **SemanticRouter** | ✅ Done | Cosine similarity |
| **PromptRegistry** | ✅ Done | Prompt entry management |
| **In-memory caching** | ✅ Done | 5-minute TTL |

**Not implemented:**
- [ ] OpenRouter embeddings (bge-m3)
- [ ] Qdrant vector store
- [ ] Redis embedding cache
- [ ] API endpoints

### Phase 2: Enhanced (3-4 weeks)

1. [ ] **Qdrant Local via Helm** — Deploy to k8s (NO cloud, NO API key)
    - File: `k8s/qdrant/values.yaml` ✅ Created
2. [ ] **OpenRouter Embedding Provider** — Replace DefaultEmbedder with real bge-m3
3. [ ] **Redis Embedding Cache** — 7-day TTL (already in p9i stack)
4. [ ] **API Endpoints** — /api/v1/search, /api/v1/prompts

### Phase 3: Scale (future)

1. [ ] Re-ranking — cross-encoder for precision
2. [ ] Metrics — recall@k, MRR, NDCG
3. [ ] Qdrant replication for HA

---

## Consequences

### Positive

- Семантический поиск вместо keyword-based
- Поддержка синонимов и опечаток
- Better user experience с "похожими промтами"
- Foundation для recommendation system

### Negative

- Дополнительная latency (p95 ~200ms vs <10ms)
- API costs (OpenRouter + Qdrant)
- Operational complexity (vector DB)
- Время на initial indexing всех промтов

### Risks

| Risk | Mitigation |
|------|------------|
| API costs при масштабировании | Кэширование + мониторинг |
| Embedding quality для русского | bge-m3 поддерживает ru |
| Vendor lock-in | Abstraction layer |

---

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Semantic search accuracy** | >80% relevance | User feedback survey |
| **Search latency p95** | <200ms | APM dashboard |
| **Cache hit rate** | >30% | Redis metrics |
| **Coverage** | 100% prompts indexed | Vector store count |
| **Embedding cost** | <$0.001 per query | Cost tracking |

**Verification:** Monthly review via analytics dashboard

---

## Reconsidered Alternatives

### 1. Keyword-based routing (existing P9iRouter)

| Aspect | Verdict |
|--------|---------|
| **Why rejected** | No semantic understanding, breaks on typos/synonyms |
| **Trade-off** | Fast & free, but limited accuracy |

### 2. Pure LLM-based routing (every query → LLM classifier)

| Aspect | Verdict |
|--------|---------|
| **Why rejected** | High latency (+2-3s), high cost per request |
| **Trade-off** | Most accurate, but business infeasible at scale |

### 3. BM25 / TF-IDF keyword search

| Aspect | Verdict |
|--------|---------|
| **Why rejected** | No semantic understanding, same limitations as keyword routing |
| **Trade-off** | Simple implementation, but poor for natural language |

**Final choice rationale:** Hybrid approach (embeddings + optional LLM fallback) balances speed, cost, and accuracy. Embeddings provide fast semantic matching while caching keeps costs low.

---

## Related Documents

- [ADR-007: Multi-Agent Orchestrator](ADR-007-multi-agent-orchestrator.md)
- [ADR-013: Code Quality Improvements](ADR-013-code-review-improvements.md)

---

## Status History

| Version | Date | Status |
|---------|------|--------|
| 1.0 | 2026-04-01 | Proposed |
| 1.1 | 2026-04-01 | Updated: Added Success Criteria, Reconsidered Alternatives |

---

**ADR Version:** 1.1
**Created:** 2026-04-01
**Last Updated:** 2026-04-01
**Status:** Proposed
**Review Date:** 2026-04-08
**Deciders:** p9i team
