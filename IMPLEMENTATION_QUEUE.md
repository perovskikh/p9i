# AI Prompt System — Очередь исправлений

**Сгенерировано:** 2026-03-16
**Основа:** promt-adr-implementation-planner.md

---

## Текущее состояние

### ✅ Реализовано
- FastMCP Server с 7 tools
- Docker Compose (PostgreSQL + Redis + Server)
- 28 промтов скопированы
- Memory service работает
- Auto-detection работает

### ❌ Недоработки (Critical Path)

| # | Проблема | Приоритет | Зависимости | Status |
|---|----------|-----------|-------------|--------|
| 1 | Health endpoint 404 | P0 (Critical) | Нет | TODO |
| 2 | API Keys валидация | P0 | Нет | TODO |
| 3 | PostgreSQL schema | P1 | Нет | TODO |
| 4 | Audit logging | P2 | #2 | TODO |

---

## Critical Path (Layer 0 → Layer 2)

```
Layer 0 (Foundation)
├── 1. Health endpoint — FastMCP app attribute error
│   └── Status: BLOCKED
│
Layer 1 (Core)
├── 2. API Keys middleware — валидация, permissions
│   └── Depends on: #1
├── 3. PostgreSQL schema apply
│   └── Depends on: #1, #2
│
Layer 2 (Features)
└── 4. Audit logging
    └── Depends on: #2
```

---

## План реализации (2 спринта)

### Sprint 1 (Week 1) — Foundation

| Задача | Estimated | Status |
|--------|-----------|--------|
| Исправить health endpoint (убрать mcp.app, добавить FastAPI) | 30 min | TODO |
| Реализовать базовую API Key валидацию | 2 hours | TODO |
| Обновить docker-compose с healthcheck | 30 min | TODO |

### Sprint 2 (Week 2) — Core

| Задача | Estimated | Status |
|--------|-----------|--------|
| Применить PostgreSQL schema к БД | 1 hour | TODO |
| Реализовать permissions/scopes для API Keys | 2 hours | TODO |
| Добавить rate limiting | 1 hour | TODO |
| Реализовать audit logging | 2 hours | TODO |

---

## Блокеры

1. **FastMCP версия 3.x** — изменился API (`mcp.app` → `mcp.http_app`)
2. **Нужна документация FastMCP** — для правильной интеграции health endpoint

---

## Следующий шаг

Начать с **#1 Исправить health endpoint** — самый критичный блокер.

```bash
# Команда для применения
cd ai-prompt-system
docker compose up -d --build
```