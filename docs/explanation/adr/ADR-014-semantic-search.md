# ADR-014: Semantic Search with Optional Feature Flag

## Metadata

| Field | Value |
|-------|-------|
| **Number** | ADR-014 |
| **Status** | Partially Implemented |
| **Date** | 2026-04-01 |
| **Last Updated** | 2026-04-04 |
| **Author** | p9i team |
| **Supersedes** | — |
| **Reviewers** | TBD |

---

## Status Summary (as of 2026-04-04)

### Реализовано ✅

| Компонент | Статус | Примечания |
|-----------|--------|-----------|
| **HybridPromptRouter** | ✅ Готово | Rule-based + Semantic + LLM cascade |
| **SemanticRouter** | ✅ Готово | Cosine similarity matching |
| **PromptRegistry** | ✅ Готово | Prompt entry management |
| **In-memory caching** | ✅ Готово | 5-minute TTL |
| **Rule-based router** | ✅ Готово | Keyword matching |

### НЕ реализовано ❌

| Компонент | Статус | Примечания |
|-----------|--------|-----------|
| **Real Embeddings** | ❌ | DefaultEmbedder (hash-based fallback) |
| **Qdrant Vector Store** | ❌ | В .env есть ключи, код не написан |
| **Redis Embedding Cache** | ❌ | 7-day TTL не реализован |
| **API Endpoints** | ❌ | /api/v1/search не создан |

---

## Context

### Проблема

Текущая система p9i использует **P9iRouter** для маршрутизации запросов на основе ключевых слов (keyword-based routing). Это решение работает быстро и бесплатно, но имеет ограничения:

1. **Нет семантического понимания** — запрос "создай кнопку" и "добавь компонент интерфейса" могут маршрутизироваться по-разному
2. **Ограниченный поиск** — невозможно искать промты по смыслу
3. **Зависимость от точных ключевых слов** — опечатка или синоним ломает маршрутизацию

### Обоснование

Для улучшения качества поиска и маршрутизации необходимо внедрить **семантический поиск** с использованием эмбеддингов.

### Constraints (Важные!)

1. **ДОЛЖЕН быть опциональным** — toggle через `SEMANTIC_SEARCH_ENABLED`
2. **НЕ должен ломать существующее** — graceful fallback на keyword search
3. **Должен быть cost-effective** — минимизировать API costs
4. **Current implementation incomplete** — планы были, кода нет

---

## Decision

### Architecture: Optional Semantic Search с Feature Flag

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Optional Semantic Search Architecture                      │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────┐
                    │     SEMANTIC_SEARCH_ENABLED=false    │◄── DEFAULT
                    │     (Current Behavior - 100% Work)  │
                    └─────────────────┬───────────────────┘
                                        │
                    ┌─────────────────▼───────────────────┐
                    │        P9iRouter only                │
                    │   (Keyword-based routing)            │
                    └─────────────────────────────────────┘

                    ┌─────────────────────────────────────┐
                    │     SEMANTIC_SEARCH_ENABLED=true     │
                    │     (Optional Feature)              │
                    └─────────────────┬───────────────────┘
                                        │
                    ┌─────────────────▼───────────────────┐
                    │      HybridPromptRouter              │
                    │  (Semantic + Keyword Fallback)       │
                    └─────────────────┬───────────────────┘
                                        │
          ┌─────────────────────────────┼─────────────────────────────┐
          │                             │                             │
          ▼                             ▼                             ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Jina AI        │     │    Qdrant       │     │   Keyword        │
│   Embedder       │     │   Vector Store  │     │   Fallback       │
│   (optional)     │     │   (optional)    │     │   (always)      │
└──────────────────┘     └──────────────────┘     └──────────────────┘
          │                             │                             │
          └─────────────────────────────┼─────────────────────────────┘
                                        │
                         ┌─────────────▼─────────────┐
                         │  Redis Cache (7-day)     │
                         │  (when enabled)          │
                         └─────────────────────────┘
```

---

## Environment Variables

```bash
# =============================================================================
# Semantic Search (ADR-014) - Optional Feature
# =============================================================================

# Master toggle - when false, all semantic features are disabled
SEMANTIC_SEARCH_ENABLED=false  # Default: false (current behavior - works!)

# Embedding Provider (only when SEMANTIC_SEARCH_ENABLED=true)
JINA_API_KEY=                  # Get from https://jina.ai/api-keys
EMBEDDING_MODEL=jina-embeddings-v3
EMBEDDING_DIMENSIONS=1024

# Vector Store (optional - only when SEMANTIC_SEARCH_ENABLED=true)
# If not set, uses in-memory embeddings with keyword fallback
QDRANT_ENABLED=false
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
QDRANT_CLUSTER_ENDPOINT=https://738f7f72-5173-4601-b005-8bece5a4ea9a.europe-west3-0.gcp.cloud.qdrant.io
QDRANT_COLLECTION=prompts

# Cache (optional - uses Redis if available)
EMBEDDING_CACHE_ENABLED=true
EMBEDDING_CACHE_TTL=604800  # 7 days in seconds

# Search Mode
SEMANTIC_SEARCH_MODE=semantic  # semantic | keyword | hybrid
SEMANTIC_SIMILARITY_THRESHOLD=0.7
```

---

## Directory Structure

```
src/infrastructure/semantic_search/
├── __init__.py
├── ports.py                    # Protocol definitions
├── config.py                   # Configuration management
├── adapters/
│   ├── __init__.py
│   ├── base.py                # Base adapter classes
│   ├── jina_embedder.py        # Jina AI embedder
│   ├── qdrant_store.py         # Qdrant vector store
│   ├── redis_cache.py          # Redis caching layer
│   └── keyword_fallback.py     # Keyword search fallback
├── factory.py                  # Adapter factory
├── service.py                  # Main semantic search service
└── router_integration.py       # Integration with P9iRouter
```

---

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)

**Goal**: Implement base infrastructure without breaking existing code

```python
# src/infrastructure/semantic_search/ports.py
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, List, Optional

class SearchMode(str, Enum):
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"

@dataclass(frozen=True)
class SearchQuery:
    text: str
    top_k: int = 5
    filters: Optional[dict] = None
    similarity_threshold: Optional[float] = None

@dataclass(frozen=True)
class SearchResult:
    chunk_id: str
    content: str
    score: float
    metadata: dict

class EmbedderProtocol(Protocol):
    async def embed(self, texts: List[str]) -> List[List[float]]: ...
    async def embed_single(self, text: str) -> List[float]: ...
    def get_dimension(self) -> int: ...

class SemanticSearchPort(Protocol):
    async def search(self, query: SearchQuery) -> List[SearchResult]: ...
    def is_enabled() -> bool: ...
    def get_mode() -> SearchMode: ...
```

### Phase 2: Adapters (Week 2)

**Goal**: Implement Jina embedder and Qdrant store adapters

### Phase 3: Service Layer (Week 3)

**Goal**: Implement SemanticSearchService with fallback

### Phase 4: Integration (Week 4)

**Goal**: Integrate with existing P9iRouter

---

## Backwards Compatibility

### Когда SEMANTIC_SEARCH_ENABLED=false (По умолчанию)

```python
# Текущее поведение - ничего не меняется
router = P9iRouter()
result = router.route("создай кнопку")  # Keyword-based routing
```

### Когда SEMANTIC_SEARCH_ENABLED=true

```python
# Новое поведение - семантическая маршрутизация
router = HybridPromptRouter()  # или расширение существующего
result = await router.route("создай кнопку")  # Semantic + fallback
```

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Qdrant API costs | Medium | Only enable when needed, use cache |
| Jina API costs | Low | ~$0.013 per 1M tokens, cache aggressively |
| Latency increase | Medium | Use cache, async operations |
| Breaking existing routing | Low | Feature flag default=false |
| Missing API keys | Low | Graceful fallback to keyword search |

---

## Configuration Reference

### Minimal Config (Semantic Search Enabled)

```bash
SEMANTIC_SEARCH_ENABLED=true
JINA_API_KEY=jina_xxxxxxxxxxxxx
```

### Full Config (All Features)

```bash
SEMANTIC_SEARCH_ENABLED=true
JINA_API_KEY=jina_xxxxxxxxxxxxx
EMBEDDING_MODEL=jina-embeddings-v3
QDRANT_ENABLED=true
QDRANT_API_KEY=xxxxx
QDRANT_CLUSTER_ENDPOINT=https://xxxxx.qdrant.io
EMBEDDING_CACHE_ENABLED=true
EMBEDDING_CACHE_TTL=604800
SEMANTIC_SEARCH_MODE=hybrid
SEMANTIC_SIMILARITY_THRESHOLD=0.7
```

---

## Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Create `src/infrastructure/semantic_search/` directory
- [ ] Implement `ports.py` with protocol definitions
- [ ] Implement `config.py` with environment variable wrappers

### Phase 2: Adapters
- [ ] Implement `JinaEmbedderAdapter`
- [ ] Implement `QdrantVectorStoreAdapter`
- [ ] Implement `RedisCacheAdapter`
- [ ] Implement `KeywordFallbackAdapter`

### Phase 3: Service
- [ ] Implement `SemanticSearchService` with fallback logic
- [ ] Implement graceful degradation when disabled

### Phase 4: Integration
- [ ] Extend `P9iRouter` to support optional semantic search
- [ ] Add health checks
- [ ] Write integration tests

---

## Current Implementation Status

### HybridPromptRouter (`src/application/router/cascade/hybrid.py`)

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

### SemanticRouter (`src/application/router/cascade/semantic.py`)

**Status:** ✅ Implemented (uses DefaultEmbedder)

```python
class SemanticRouter(BaseRouter[RoutingResult]):
    """Semantic routing using embeddings with cosine similarity."""

    def __init__(self, embedder: EmbedderProtocol | None = None, threshold: float = 0.7):
        self._embedder = embedder or DefaultEmbedder()
        self._threshold = threshold
```

### DefaultEmbedder (Fallback)

**Status:** ⚠️ Hash-based, NOT real embeddings

```python
class DefaultEmbedder:
    """Simple hash-based embedding fallback."""

    def embed(self, text: str) -> list[float]:
        """Simple hash-based embedding fallback."""
        words = text.lower().split()
        vec = [0.0] * 64
        for i, word in enumerate(words[:64]):
            vec[i % 64] += hash(word) % 1000
        magnitude = math.sqrt(sum(x * x for x in vec))
        if magnitude > 0:
            vec = [x / magnitude for x in vec]
        return vec
```

---

## Consequences

### Positive

- Семантический поиск вместо keyword-based
- Поддержка синонимов и опечаток
- Better user experience с "похожими промтами"
- Foundation для recommendation system

### Negative

- Дополнительная latency (p95 ~200ms vs <10ms)
- API costs (Jina + Qdrant)
- Operational complexity (vector DB)
- Время на initial indexing всех промтов

---

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Semantic search accuracy** | >80% relevance | User feedback survey |
| **Search latency p95** | <200ms | APM dashboard |
| **Cache hit rate** | >30% | Redis metrics |
| **Coverage** | 100% prompts indexed | Vector store count |
| **Embedding cost** | <$0.001 per query | Cost tracking |

---

## Related Documents

- [ADR-007: Multi-Agent Orchestrator](ADR-007-multi-agent-orchestrator.md)
- [ADR-013: Code Quality Improvements](ADR-013-code-review-improvements.md)
- [ADR-022: Multi-Project SaaS Architecture](ADR-022-multi-project-saas-architecture.md)

---

## Status History

| Version | Date | Status |
|---------|------|--------|
| 1.0 | 2026-04-01 | Proposed |
| 1.1 | 2026-04-01 | Updated: Added Success Criteria, Reconsidered Alternatives |
| 1.2 | 2026-04-04 | Updated: Unified with ADR-023, added Feature Flag architecture |

---

**ADR Version:** 1.2
**Created:** 2026-04-01
**Last Updated:** 2026-04-04
**Status:** Partially Implemented
**Review Date:** 2026-04-11
**Deciders:** p9i team
