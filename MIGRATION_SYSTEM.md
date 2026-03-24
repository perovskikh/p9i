# Migration System - Рефакторинг после опыта миграции

## Overview
Система автоматической миграции для p9i MCP, построенная на основе опыта миграции Pydantic → Domain Entities.

## Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                    Migration Workflow (p9i)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────┐    ┌──────────┐    ┌─────────┐    ┌──────────┐  │
│   │ Siri    │───▶│Architect │───▶│Developer│───▶│ DevOps   │  │
│   │ (NL)    │    │  (Plan)  │    │(Implement)│ │ (Test)  │  │
│   └─────────┘    └──────────┘    └─────────┘    └──────────┘  │
│       │              │               │               │         │
│       ▼              ▼               ▼               ▼         │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │          Reviewer Agent (Verify)                        │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                 │
│                              ▼                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │          GitHub Actions (CI/CD)                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Компоненты

### 1. Промпты (prompts/agents/migration/)

| Промпт | Агент | Описание |
|--------|-------|----------|
| `promt-migration-planner.md` | Architect | Планирование миграции |
| `promt-migration-implementation.md` | Developer | Выполнение миграции |
| `promt-migration-review.md` | Reviewer | Проверка миграции |
| `promt-migration-devops.md` | DevOps | Тестирование и CI/CD |
| `promt-siri-migration-handler.md` | Siri Router | Обработка NL |

### 2. Agent Router (src/application/agent_router.py)

Добавлен агент "migration" с ключевыми словами:
- "миграц", "migrat", "переход", "migrate"
- "от old", "на domain"

### 3. GitHub Actions (`.github/workflows/migration-verify.yml`)

Автоматическая проверка при push/PR:
- ✅ Syntax check
- ✅ Import verification
- ✅ Functional tests
- ✅ Baseline verification
- ✅ Domain exceptions

## Использование

### Через Siri (естественный язык):
```
"мигрируй проект на Domain Entities"
"составь план миграции"
"проверь миграцию"
```

### Через p9i:
```
"use p9i: запусти миграцию X -> Y"
"use p9i: проверь миграцию"
```

### Через Agent Router:
```python
from src.application.agent_router import AgentRouter

router = AgentRouter()
agents = router.detect_agents("мигрируй проект на Domain Entities")
# → ['migration']
```

## Best Practices (из опыта)

### ✅ Что работает:
1. **Импортировать enum напрямую** - НЕ наследовать
2. **Добавлять backward compatibility alias** - Сразу
3. **Создавать converters** - from_storage(), to_pydantic()
4. **Тестировать в Docker** - Тот же образ что production

### ❌ Что вызывает ошибки:
1. Наследование enum: `class Tier(BaseTier)` → TypeError
2. Удаление старого кода сразу → Ломает совместимость
3. Тестирование локально ≠ Docker

## Workflow миграции

```
1. Siri → "мигрируй X на Y"
     │
     ▼
2. Migration Agent активирован
     │
     ▼
3. Architect → promt-migration-planner
     │    → Создаёт MIGRATION_PLAN.md
     ▼
4. Developer → promt-migration-implementation
     │    → Выполняет миграцию
     ▼
5. Reviewer → promt-migration-review
     │    → Проверяет импорты, совместимость
     ▼
6. DevOps → promt-migration-devops
     │    → Запускает тесты в Docker
     ▼
7. GitHub Actions → migration-verify.yml
     │    → Автоматическая проверка
     ▼
8. Готово! ✅
```

## Файлы созданные после рефакторинга

```
prompts/agents/migration/
├── promt-migration-planner.md          # Architect
├── promt-migration-implementation.md   # Developer
├── promt-migration-review.md           # Reviewer
├── promt-migration-devops.md           # DevOps
└── promt-siri-migration-handler.md     # Siri NL handler

.github/workflows/
└── migration-verify.yml                # CI/CD

src/application/
└── agent_router.py                     # Updated (migration agent)

MIGRATION_PLAN.md                       # План (из прошлой миграции)
MIGRATION_REVIEW.md                     # Ревизия + уроки
```

## Подключение к новому проекту

1. Скопировать `prompts/agents/migration/` в проект
2. Добавить миграцию в `agent_router.py`
3. Настроить GitHub Actions workflow
4. Запустить: "use p9i: мигрируй проект"