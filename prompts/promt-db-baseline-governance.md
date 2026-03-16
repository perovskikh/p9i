# AI Agent Prompt: DB Baseline Governance для CodeShift

**Version:** 1.2
**Date:** 2026-03-06
**Purpose:** Контроль изменений схемы БД через единственный источник правды — SQL baseline

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Operational |
| **Время выполнения** | 30–60 мин |
| **Домен** | Data — управление схемой БД |

**Пример запроса:**

> «Используя `promt-db-baseline-governance.md`, внеси изменения в
> `scripts/utils/init-saas-database.sql`, синхронизируй SQLAlchemy-модели
> и проверь безопасность SQL.»

**Ожидаемый результат:**
- `scripts/utils/init-saas-database.sql` обновлён (canonical schema)
- SQLAlchemy-модели синхронизированы с baseline
- Нет Alembic-миграций (удалены в 2026-02-08)
- Проверка безопасности SQL (injection, privileges) пройдена

---

## Когда использовать

- При добавлении новой таблицы или поля в схему БД
- При изменении существующих constraints или индексов
- При синхронизации SQLAlchemy-моделей с реальной схемой
- При проверке расхождений между моделями и SQL baseline

> **Alembic запрещён** (удалён 2026-02-08). Только прямое изменение
> `scripts/utils/init-saas-database.sql` + `make init-saas-db`.

---

## Mission Statement

Ты — AI-агент, ответственный за **управление изменениями схемы базы данных** в проекте CodeShift.
Твоя задача — обеспечить, что все изменения схемы БД вносятся корректно, через единственный
канонический источник, и соответствуют ADR-решениям.

**Контекст:**
- Alembic удалён 2026-02-08
- Legacy контур `k8s/` с inline SQL схемой удалён
- Единственный источник правды: `scripts/utils/init-saas-database.sql`
- Применение: `make init-saas-db`

**Примеры задач, которые решает этот промпт:**
- Добавление новой таблицы в схему БД
- Изменение структуры существующей таблицы
- Добавление индексов, constraints
- Проверка соответствия схемы коду (models)
- Валидация SQL на безопасность

**Ожидаемый результат:**
- Изменения внесены только в `scripts/utils/init-saas-database.sql`
- Схема синхронизирована с Python моделями
- Проверена SQL инъекция безопасность
- ADR `telegram-bot-saas-platform` обновлён (если релевантно)

---

## Контракт синхронизации системы

Этот промпт управляется из единой точки: `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`.

Обязательные инварианты:
- Канонический источник схемы: `scripts/utils/init-saas-database.sql`
- Legacy `k8s/postgres-saas.yaml` — только исторический контекст, не модифицировать
- Изменения применяются через `make init-saas-db`
- ADR `telegram-bot-saas-platform` содержит решения по структуре БД

---

## Назначение

Этот промпт управляет изменениями схемы БД только через канонический SQL baseline с валидацией совместимости SaaS-платформы.

## Входы

- Запрос на изменение структуры/ограничений БД
- Канонический baseline: `scripts/utils/init-saas-database.sql`
- Связанные Python-модели/репозитории и тесты

## Выходы

- Актуализированный SQL baseline и согласованные изменения в коде
- Результаты проверки совместимости и rollback-план
- Документированный change-set без расхождения источников истины

## Ограничения / инварианты

- Следовать ограничениям I-1..I-9 и Constraints C1–C10 из meta-prompt
- ADR-ссылки и зависимости фиксировать по topic slug
- Поддерживать dual-status/чеклист для ADR-зависимых DB-решений
- Использовать `verify-all-adr.sh` и `verify-adr-checklist.sh` при архитектурных изменениях
- Context7 gate обязателен для SQL best practices и миграционных решений
- Запрещено использовать legacy schema как active source
- Соблюдать Anti-Legacy и update in-place

## Workflow шаги

1. Discovery: определить необходимость и влияние изменения схемы
2. Design: сформировать безопасный SQL-патч и стратегию отката
3. Sync: синхронизировать SQL baseline и Python-слой
4. Validation: прогнать тесты и верификацию архитектурных инвариантов

## Проверки / acceptance criteria

- Изменение отражено в `scripts/utils/init-saas-database.sql` как в едином источнике истины
- Согласованность с приложением подтверждена тестами
- Нет активных ссылок на legacy БД-манифесты как на текущую схему

## Связи с другими промптами

- До: `promt-verification.md` (если изменение влияет на архитектуру)
- После: `promt-index-update.md` (если обновлялись ADR), `promt-bug-fix.md` (если выявлены дефекты миграции)

---

## Project Context

### Database Architecture

```
PostgreSQL (SaaS)
├── Host: POSTGRES_SAAS_HOST (env var)
├── Port: POSTGRES_SAAS_PORT (env var)
├── Database: POSTGRES_SAAS_DB (env var)
├── User: POSTGRES_SAAS_USER (env var)
└── Password: POSTGRES_SAAS_PASSWORD (env var)

Schema Source:
└── scripts/utils/init-saas-database.sql (ЕДИНСТВЕННЫЙ ИСТОЧНИК)
```

### Текущие таблицы (из baseline SQL)

| Table | Purpose |
|---|---|
| `users` | Telegram users, auth info |
| `plans` | Subscription plans (free/basic/pro/enterprise) |
| `subscriptions` | User subscriptions, status, dates |
| `payments` | Payment records, YooKassa integration |
| `user_instances` | K8s instances per user |
| `webhook_logs` | Webhook audit trail |

### Python Models

```
telegram-bot/app/
├── models/
│   ├── user.py
│   ├── subscription.py
│   ├── payment.py
│   └── instance.py
└── database/
    └── session.py
```

---

## Шаг 0: Понять требование к изменению

### 0.1. Получить задачу

```
Запроси у пользователя:
1. Что нужно изменить в схеме? (новая таблица / изменение существующей / индекс / constraint)
2. Какая бизнес-логика стоит за изменением?
3. Есть ли связь с Python моделями?
```

### 0.2. Классифицировать изменение

| Тип | Риск | Примеры |
|---|---|---|
| **Additive** | 🟢 Низкий | Новая таблица, новая колонка (nullable), новый индекс |
| **Modificative** | 🟡 Средний | Изменение типа колонки, добавление NOT NULL |
| **Destructive** | 🔴 Высокий | DROP TABLE, DROP COLUMN, изменение PK |

---

## Шаг 1: Анализ текущего состояния

### 1.1. Прочитать текущую схему

```bash
# Канонический источник
cat scripts/utils/init-saas-database.sql

# Проверить структуру
grep -E "CREATE TABLE|ALTER TABLE|CREATE INDEX" scripts/utils/init-saas-database.sql
```

### 1.2. Проверить Python модели

```bash
# Найти связанные модели
ls telegram-bot/app/models/
grep -rn "class.*Model\|Table\|Column" telegram-bot/app/models/ --include="*.py"
```

### 1.3. Проверить существующие constraints

```bash
# Foreign keys, unique constraints
grep -E "REFERENCES|UNIQUE|PRIMARY KEY|CONSTRAINT" scripts/utils/init-saas-database.sql
```

---

## Шаг 2: Context7 — SQL Best Practices

### 2.1. Запрос к Context7

```
Запрос к Context7:
- Технология: PostgreSQL
- Задача: [тип изменения схемы]
- Что получить: best practices, migration patterns, performance considerations
```

**Примеры запросов:**

| Изменение | Context7 Query |
|---|---|
| Новая таблица | `postgresql create table best practices naming conventions indexes` |
| Добавление колонки | `postgresql alter table add column default value migration` |
| Индекс | `postgresql index types btree gin gist performance selectivity` |
| Foreign key | `postgresql foreign key on delete cascade restrict deferrable` |

---

## Шаг 3: Подготовка изменения

### 3.1. Написать SQL

**Template для новой таблицы:**
```sql
-- ============================================
-- Table: [table_name]
-- Purpose: [описание]
-- Created: YYYY-MM-DD
-- ADR: telegram-bot-saas-platform
-- ============================================

CREATE TABLE IF NOT EXISTS [table_name] (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- business columns
    [column_name] [TYPE] [CONSTRAINTS],
    -- foreign keys
    CONSTRAINT fk_[relation] FOREIGN KEY ([column]) 
        REFERENCES [other_table]([column]) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_[table]_[column] ON [table_name]([column]);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_[table]_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER [table]_updated_at
    BEFORE UPDATE ON [table_name]
    FOR EACH ROW
    EXECUTE FUNCTION update_[table]_timestamp();
```

**Template для изменения существующей таблицы:**
```sql
-- ============================================
-- Alter: [table_name]
-- Change: [описание изменения]
-- Date: YYYY-MM-DD
-- ============================================

-- Add column (nullable first, then maybe set default/not null)
ALTER TABLE [table_name] 
    ADD COLUMN IF NOT EXISTS [column_name] [TYPE] DEFAULT [value];

-- Add index
CREATE INDEX IF NOT EXISTS idx_[table]_[column] ON [table_name]([column]);

-- Add constraint
ALTER TABLE [table_name]
    ADD CONSTRAINT [constraint_name] [CONSTRAINT_TYPE] ([columns]);
```

### 3.2. Проверить SQL безопасность

| Check | Requirement |
|---|---|
| SQL Injection | Нет динамически собираемых запросов |
| Idempotency | `IF NOT EXISTS` / `IF EXISTS` |
| Privilege | Не GRANT SUPERUSER |
| Data safety | Backup before destructive operations |

---

## Шаг 4: Синхронизация с Python моделями

### 4.1. Обновить/создать модель

```python
# telegram-bot/app/models/[entity].py

from sqlalchemy import Column, String, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from app.database.base import Base

class [Entity](Base):
    __tablename__ = "[table_name]"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    
    # business columns
    [column_name] = Column([Type], nullable=[True/False])
    
    # relationships
    [relation] = relationship("[OtherEntity]", back_populates="[back_ref]")
```

### 4.2. Проверить соответствие SQL ↔ Python

| SQL | Python Model | Match |
|---|---|---|
| `id UUID PRIMARY KEY` | `id = Column(UUID, primary_key=True)` | ✅ |
| `name VARCHAR(255) NOT NULL` | `name = Column(String(255), nullable=False)` | ✅ |
| `REFERENCES users(id)` | `user_id = Column(ForeignKey("users.id"))` | ✅ |

---

## Шаг 5: Применение изменений

### 5.1. Обновить baseline SQL

```bash
# Редактировать единственный источник правды
nano scripts/utils/init-saas-database.sql

# ИЛИ через скрипт-редактор
# Добавить новый SQL в конец файла (сохраняя порядок зависимостей)
```

### 5.2. Применить через make

```bash
# Применить изменения к БД
make init-saas-db

# Проверить применение
make db-status  # если есть такой target
```

### 5.3. Проверить результат

```bash
# Подключиться к БД и проверить
kubectl exec -it -n codeshift-saas deploy/postgres-saas -- \
    psql -U $POSTGRES_SAAS_USER -d $POSTGRES_SAAS_DB -c "\d+ [table_name]"

# Или через make
make db-shell  # если есть такой target
```

---

## Шаг 6: Тестирование

### 6.1. Unit tests для моделей

```bash
cd telegram-bot
poetry run pytest tests/test_models.py -v
poetry run pytest tests/test_database.py -v
```

### 6.2. Integration tests

```bash
# Проверить что приложение работает с новой схемой
make bot-restart
make bot-logs | head -50
```

### 6.3. Rollback plan

```markdown
## Rollback Plan

Если изменение вызвало проблемы:

1. Для additive changes (новая таблица/колонка):
   - Можно оставить, приложение совместимо
   
2. Для modificative changes:
   - Восстановить backup
   - Применить предыдущую версию init-saas-database.sql
   
3. Для destructive changes:
   - ОБЯЗАТЕЛЬНО backup перед применением
   - Восстановить из backup
```

---

## Шаг 7: Документирование

### 7.1. Commit message

```
db(schema): [краткое описание изменения]

[Подробное описание]

Tables affected: [table1, table2]
Type: [Additive/Modificative/Destructive]
ADR-related: telegram-bot-saas-platform
```

### 7.2. Обновить ADR (если требуется)

Если изменение схемы связано с чеклистом ADR `telegram-bot-saas-platform`:

```bash
# Найти ADR
ADR_FILE=$(find docs/explanation/adr -name "ADR-*-telegram-bot-saas-platform*.md" | head -1)

# Обновить чеклист если релевантно
# [ ] DB schema for [feature]
```

---

## Чеклист DB Schema Change

- [ ] Требование к изменению понято
- [ ] Тип изменения классифицирован (Additive/Modificative/Destructive)
- [ ] Текущая схема изучена
- [ ] Context7 запрос выполнен
- [ ] SQL написан с IF NOT EXISTS (idempotent)
- [ ] Python модели синхронизированы
- [ ] Изменение внесено ТОЛЬКО в `scripts/utils/init-saas-database.sql`
- [ ] `make init-saas-db` выполнен
- [ ] Unit tests проходят
- [ ] Integration tests проходят
- [ ] Rollback plan задокументирован
- [ ] Commit message соответствует стандарту
- [ ] ADR обновлён (если релевантно)

---

## Anti-patterns

| Anti-pattern | Правильный подход |
|---|---|
| Изменение схемы в legacy `k8s/postgres-saas.yaml` (исторический контур) | Только `scripts/utils/init-saas-database.sql` |
| Миграции через Alembic | Alembic удалён, baseline-only |
| Raw SQL в Python коде | ORM (SQLAlchemy) для queries |
| DROP без backup | Всегда backup перед destructive |
| Schema drift (SQL ≠ models) | Синхронизировать SQL и Python models |

---

## Ресурсы

| Ресурс | Путь | Назначение |
|---|---|---|
| **Каноничный schema** | `scripts/utils/init-saas-database.sql` | Single source of truth |
| **SQLAlchemy models** | `telegram-bot/app/database.py` | ORM definitions |
| **ADR-файлы** | `docs/explanation/adr/ADR-*.md` | Architecture constraints |
| **Скрипт верификации** | `scripts/verify-all-adr.sh` | Validation |
| **Правила проекта** | `.github/copilot-instructions.md` | Dual SQL schema warning |
| **Официальная документация** | `docs/official_document/` | **READ-ONLY** эталон |
| **Meta-prompt** | `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md` | Source of truth |

---

## Связанные промпты

| Промпт | Когда использовать |
|---|---|
| `promt-feature-add.md` | Если schema change для нового функционала |
| `promt-security-audit.md` | Проверка SQL injection, credentials |
| `promt-verification.md` | После изменений схемы |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.2 | 2026-03-06 | Добавлены секции Gate I: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`. |
| 1.1 | 2026-02-25 | Добавлены `## Чеклист`, `## Связанные промпты`; Alembic removed note. |
| 1.0 | 2026-02-24 | Первая версия: DB baseline governance через SQL-файл. |

---

**Prompt Version:** 1.2
**Date:** 2026-03-06
