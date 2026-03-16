# Sprint 2 — Core Features Implementation

**Generated:** 2026-03-16
**Based on:** promt-feature-add.md workflow

---

## Задачи Sprint 2

| # | Задача | Estimated | Status |
|---|--------|-----------|--------|
| 1 | PostgreSQL schema application | 1 hour | IN PROGRESS |
| 2 | Permissions/scopes для API Keys | 2 hours | TODO |
| 3 | Rate limiting | 1 hour | ✅ DONE |
| 4 | Audit logging | 2 hours | TODO |

---

## 1. PostgreSQL Schema Application

### Schema Definition (в БД не применено)

```sql
-- Применить к БД через init-скрипт
CREATE TABLE IF NOT EXISTS prompts (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT '1.0.0',
    type TEXT,
    layer TEXT,
    tags TEXT[] DEFAULT '{}',
    variables JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS prompt_versions (
    id SERIAL PRIMARY KEY,
    prompt_id INTEGER REFERENCES prompts(id) ON DELETE CASCADE,
    version TEXT NOT NULL,
    content TEXT NOT NULL,
    changelog TEXT,
    eval_score INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    project_id TEXT NOT NULL,
    permissions TEXT[] DEFAULT '{}',
    rate_limit INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    api_key_id INTEGER REFERENCES api_keys(id),
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id INTEGER,
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 2. Permissions/Scopes для API Keys

### Architecture

```
API Key → Permissions → Scopes → Resources
         ├── read_prompts
         ├── run_prompt
         ├── manage_memory
         └── admin
```

### Implementation Plan

1. Расширить APIKeyManager с permissions
2. Добавить middleware для проверки scopes
3. Интегрировать с MCP tools

---

## 3. Audit Logging

### Events to log

- `prompt_executed` — when run_prompt called
- `chain_executed` — when run_prompt_chain called
- `memory_saved` — when save_project_memory called
- `api_key_validated` — when API key checked
- `rate_limit_exceeded` — when rate limit hit

---

## Implementation Commands

```bash
# Применить schema
docker exec -i ai-prompt-system-db-1 psql -U postgres -d ai_prompts < database/schema.sql

# Проверить tables
docker exec -i ai-prompt-system-db-1 psql -U postgres -d ai_prompts -c "\dt"
```