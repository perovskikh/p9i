# ADR-014: LLM-based Prompt Selection with Embeddings

## Статус решения
**Proposed** | 2026-04-01

## Прогресс реализации
📋 На рассмотрении

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

### Выбор архитектуры

**Паттерн:** Modular Service with Event-Driven Optional Layer

```
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                             │
│                  (Auth, Rate Limiting)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                 Retrieval Service                             │
│            (Semantic Search + Caching)                        │
└──────────┬─────────────────────┬────────────────────────────┘
           │                     │
┌──────────▼──────────┐ ┌────────▼─────────────┐
│  Embedding Service │ │   Vector Store      │
│   (OpenRouter)     │ │   (Qdrant)          │
└────────────────────┘ └─────────────────────┘
           │                     │
           └─────────┬───────────┘
                     │
           ┌─────────▼─────────┐
           │   Cache Layer    │
           │   (Redis + LRU)   │
           └───────────────────┘
```

### Компоненты

#### 1. Embedding Service

**Провайдер:** OpenRouter API (bge-m3 модель)

```python
# src/infrastructure/adapters/embedding/openrouter.py
class OpenRouterEmbeddingProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "bge-m3"  # Multi-lingual, 1024 dims

    async def embed(self, text: str) -> list[float]:
        # OpenRouter API call for embeddings
```

**Environment Variables:**
```bash
OPENROUTER_API_KEY=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
EMBEDDING_MODEL=bge-m3
EMBEDDING_DIMENSIONS=1024
```

#### 2. Vector Store

**Провайдер:** Qdrant Cloud

```python
# src/infrastructure/adapters/vector/qdrant.py
class QdrantVectorStore:
    def __init__(self, endpoint: str, api_key: str, collection: str):
        self.client = QdrantClient(url=endpoint, api_key=api_key)
        self.collection = collection
```

**Configuration:**
```bash
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.-J-iMKsmYUx-QCe3vPid4JFoWnAcEpNqhmX1t_7jft8
QDRANT_CLUSTER_ENDPOINT=https://738f7f72-5173-4601-b005-8bece5a4ea9a.europe-west3-0.gcp.cloud.qdrant.io
QDRANT_COLLECTION=prompts
```

**Collection Schema:**
```json
{
  "vectors": {
    "size": 1024,
    "distance": "Cosine"
  },
  "payload": ["prompt_id", "title", "content", "category", "language", "tags"]
}
```

#### 3. Cache Layer

**Backend:** Redis (существующий)

```python
# src/infrastructure/cache/embedding_cache.py
class EmbeddingCache:
    def __init__(self, redis_client, ttl: int = 604800):  # 7 days
        self.redis = redis_client
        self.ttl = ttl

    def get_embedding(self, text_hash: str) -> Optional[list[float]]:
        key = f"emb:{text_hash}"
        cached = self.redis.get(key)
        return json.loads(cached) if cached else None
```

**Cache Configuration:**
```bash
EMBEDDING_CACHE_TTL=604800    # 7 days in seconds
SEARCH_CACHE_TTL=300          # 5 minutes in seconds
```

#### 4. Retrieval Service

**Search Flow:**
```
User Query → Embedding Service → Vector Store → Top-K Results → Client
              (cache hit?)           (HNSW)
```

---

## API Contract

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

## Environment Variables

```bash
# OpenRouter (Embeddings)
OPENROUTER_API_KEY=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
EMBEDDING_MODEL=bge-m3
EMBEDDING_DIMENSIONS=1024

# Qdrant (Vector Store)
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.-J-iMKsmYUx-QCe3vPid4JFoWnAcEpNqhmX1t_7jft8
QDRANT_CLUSTER_ENDPOINT=https://738f7f72-5173-4601-b005-8bece5a4ea9a.europe-west3-0.gcp.cloud.qdrant.io
QDRANT_COLLECTION=prompts

# Redis (Cache)
REDIS_HOST=redis
REDIS_PORT=6379
EMBEDDING_CACHE_TTL=604800
SEARCH_CACHE_TTL=300
```

---

## Implementation Phases

### Phase 1: MVP (2-3 weeks)

1. **Embedding Service** — OpenRouter integration
2. **Vector Store** — Qdrant collection setup
3. **Basic Search API** — semantic search endpoint
4. **Cache** — Redis caching for embeddings

### Phase 2: Enhanced (3-4 weeks)

1. **Re-ranking** — cross-encoder for precision
2. **Metrics** — recall@k, MRR, NDCG
3. **Hybrid Search** — dense + BM25

### Phase 3: Scale (future)

1. **Self-hosted embeddings** — cost reduction
2. **A/B testing framework**

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

## Related Documents

- [ADR-007: Multi-Agent Orchestrator](ADR-007-multi-agent-orchestrator.md)
- [ADR-013: Code Quality Improvements](ADR-013-code-review-improvements.md)
- [Research: LLM-based Prompt Selection](./research/llm-prompt-selection-research.md)

---

## Status History

| Version | Date | Status |
|---------|------|--------|
| 1.0 | 2026-04-01 | Proposed |

---

**ADR Version:** 1.0
**Created:** 2026-04-01
**Status:** Proposed
**Review Date:** 2026-04-08
**Deciders:** p9i team
