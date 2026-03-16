# AI Agent Prompt: ADR Template Migration to Dual-Status Format

**Version:** 1.4
**Date:** 2026-02-25
**Purpose:** Миграция всех существующих ADR-файлов из OLD-формата к новому dual-status шаблону (ADR-template.md v2) с синхронизацией очереди внедрения (Critical Path + Layer 0 → 5)

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Operational |
| **Время выполнения** | 60–120 мин (batch) |
| **Домен** | Migration — миграция ADR к dual-status |

**Пример запроса:**

> «Используя `promt-adr-template-migration.md`, выполни batch-миграцию
> ADR к dual-status шаблону и синхронизируй индекс/очередь.»

**Ожидаемый результат:**
- Все ADR содержат `## Статус решения` + `## Прогресс реализации` + `## Чеклист реализации`
- `promt-index-update.md` запущен после миграции
- `promt-verification.md` пройден для верификации корректности

---

## Когда использовать

- При обнаружении ADR без dual-status
- При начальной миграции репозитория к новому формату ADR
- После введения нового поля в ADR-template — batch update существующих

> **Разовая операция:** после полной миграции нужен редко.
> Новые ADR сразу создаются в dual-status формате через `promt-feature-add.md`.

---

## Mission Statement

Ты — AI-агент, специализирующийся на **миграции существующих ADR-файлов** проекта CodeShift
к новому dual-status формату. Твоя задача — преобразовать каждый ADR, **сохранив весь контент**,
привести структуру к единому шаблону `ADR-template.md` и подготовить данные для
построения очереди внедрения по зависимостям ADR.

> **⚠️ ГЛАВНОЕ ПРАВИЛО:** Миграция — это **структурная трансформация**, НЕ переписывание.
> Существующий контент (Контекст, Решение, Последствия, код, Mermaid, таблицы) **ДОЛЖЕН быть сохранён ДОСЛОВНО**.
> Изменяются ТОЛЬКО метаданные (статус) и структура чеклиста.

**Ожидаемый результат (обязательный):**
- Каждый ADR после миграции содержит корректные `## Статус решения` + `## Прогресс реализации`
- Для каждого ADR заполнены metadata поля `topic slug`, `Layer`, `Зависимости ADR` (по актуальному графу)
- Реальный прогресс рассчитан через `scripts/verify-adr-checklist.sh`, а не вручную
- Обновление `index.md` включает секцию очереди внедрения (Critical Path + Layers)
- Использованы Context7 + `docs/official_document/` (READ-ONLY) для терминологии и best practices

---

## Контракт синхронизации системы

Этот промпт управляется из единой точки: `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`.

Обязательные инварианты синхронизации:
- Миграция сохраняет контент ADR, изменяя только структуру/метаданные
- Dual-status обязателен для каждого мигрированного ADR
- Topic slug используется как primary ID
- Context7 и `docs/official_document/` используются для унификации терминологии
- После миграции обязательна синхронизация через `verification` и `index-update`

---

## Context: Почему нужна миграция

### Проблема (v1 → v2)

Старая система использовала **одно поле** `**Статус:** ✅ Принято`, которое конфликтовало
два понятия: «решение принято» и «реализация завершена». Это привело к тому, что
ADR-017 (telegram-bot-saas-platform) отображался в index.md как **✅ Реализовано**
при реальном прогрессе **~37%** (11/29 пунктов чеклиста).

### Новый формат (v2 — dual-status)

Каждый ADR теперь содержит **два отдельных поля**:

```markdown
## Статус решения
[Proposed | Accepted | Rejected | Deprecated | Superseded by ADR-YYY]

## Прогресс реализации
<!-- Определяется из чеклиста: 🔴 Не начато | 🟡 Частично (~N%) | 🟢 Полностью -->
🟢 Полностью
```

---

## Назначение

Этот промпт выполняет миграцию ADR к актуальному dual-status шаблону и синхронизирует артефакты индекса/очереди внедрения.

## Входы

- Запрос на миграцию одного или нескольких ADR
- Файлы `docs/explanation/adr/ADR-*.md` и `docs/explanation/adr/ADR-template.md`
- Данные из `scripts/verify-all-adr.sh` и `scripts/verify-adr-checklist.sh`

## Выходы

- Обновлённые ADR в целевом шаблоне dual-status
- Синхронизированные статус/прогресс/чеклист и метаданные topic slug
- Отчёт по миграции и верификации

## Ограничения / инварианты

- Следовать ограничениям I-1..I-9 и Constraints C1–C10 из meta-prompt
- Использовать topic slug как первичный идентификатор ADR
- Поддерживать dual-status и согласованность `## Чеклист реализации`
- Для верификации использовать `verify-all-adr.sh` и `verify-adr-checklist.sh`
- Context7 gate обязателен для нормализации решений миграции
- Соблюдать Anti-Legacy и update in-place (без `*-v2.md`, `*-final.md`, `*-new.md`)

## Workflow шаги

1. Discovery: определить ADR-кандидаты и разрывы шаблона
2. Migration: привести ADR к целевому формату dual-status
3. Sync: обновить связанные индексы/очередь и ссылки
4. Validation: прогнать скрипты верификации и зафиксировать результат

## Проверки / acceptance criteria

- Каждый мигрированный ADR содержит `## Статус решения`, `## Прогресс реализации`, `## Чеклист реализации`
- Прогресс в ADR согласован с `verify-adr-checklist.sh`
- Нет новых legacy/дублирующих файлов

## Связи с другими промптами

- До: `promt-verification.md` (базовый аудит)
- После: `promt-index-update.md`, `promt-consolidation.md` (при необходимости)

---

## Project Context

### О проекте
**CodeShift** — multi-tenant SaaS платформа (VS Code в браузере через Telegram Bot, K8s, YooKassa).

### ADR Topic Registry
ADR идентифицируются по **topic slug** (не по номеру). Поиск: `ls docs/explanation/adr/ADR-*-{slug}*.md`

### Официальная документация (READ-ONLY)
`docs/official_document/` — read-only эталон терминологии, архитектурных паттернов и примеров.
Никогда не изменять файлы в этой директории.

### Ключевые ресурсы
| Ресурс | Путь |
|--------|------|
| Шаблон (v2) | `docs/explanation/adr/ADR-template.md` |
| Скрипт проверки чеклистов | `scripts/verify-adr-checklist.sh` |
| Скрипт структурной верификации | `scripts/verify-all-adr.sh` |
| ADR индекс | `docs/explanation/adr/index.md` |

---

## Шаг 0: Подготовка

### 0.0. Исследование с Context7 (ОБЯЗАТЕЛЬНО)

Перед миграцией выполнить запрос к Context7 для унификации терминов и best practices миграции:

```text
Запрос к Context7:
- Тема: architecture decision records migration + dependency graph prioritization
- Что получить: best practices по dual-status, dependency DAG, critical path prioritization
- Что применить: правила для миграции metadata и построения очереди внедрения
```

Если Context7 временно недоступен, используй fallback:
1) `docs/official_document/` (read-only),
2) актуальные ADR и Mermaid-граф в `docs/explanation/adr/index.md`,
3) скрипты `verify-adr-checklist.sh` и `verify-all-adr.sh`.

### 0.1. Прочитать шаблон

```bash
cat docs/explanation/adr/ADR-template.md
```

Запомнить целевую структуру: `## Статус решения` → `## Прогресс реализации` → `## Дата` → ... → `## Чеклист реализации` (4 категории).

### 0.2. Получить текущий прогресс

```bash
./scripts/verify-adr-checklist.sh --format short
```

Это даст точный прогресс каждого ADR (full/partial/none + процент).

### 0.3. Определить порядок миграции

Рекомендуемый порядок:
1. **Critical Path ADR** (по актуальному графу зависимостей)
2. ADR из нижних слоёв Layer 0 → Layer 2 (foundation/blockers)
3. ADR из Layer 3 → Layer 5 по приоритету `partial` перед `none`

Правило приоритизации:
- сначала мигрировать ADR-блокеры, от которых зависят другие;
- не начинать массовую миграцию Layer N+1, если в Layer N не завершены критические ADR по качеству миграции.

---

## Шаг 1: Миграция одного ADR

Для КАЖДОГО ADR выполни следующие подшаги:

### 1.1. Прочитать файл целиком

```bash
cat docs/explanation/adr/ADR-NNN-{slug}.md
```

### 1.2. Определить OLD-формат статуса

Существуют два варианта:

**Вариант A — inline (в метаданных):**
```markdown
# ADR-NNN: Title

**Статус:** ✅ Принято
**Дата:** 2026-02-08
```

**Вариант B — heading:**
```markdown
# ADR-NNN: Title

## Статус
✅ Принято

## Дата
2026-02-08
```

### 1.3. Извлечь значение статуса

Из OLD-формата определить:

| Старое значение | Новый `## Статус решения` |
|-----------------|--------------------------|
| `✅ Принято`, `Accepted`, `Принято` | `Accepted` |
| `Proposed`, `⏳ Proposed`, `Draft` | `Proposed` |
| `Superseded by ADR-XXX` | `Superseded by ADR-XXX` |
| `Deprecated`, `Отклонено` | `Deprecated` |
| `Completed` | `Accepted` |
| `Rejected` | `Rejected` |

Если есть строка `**Supersedes:** ADR-XXX` — **сохранить** её как есть (это отдельное поле, не статус).

### 1.4. Определить прогресс реализации

Использовать вывод `./scripts/verify-adr-checklist.sh --topic {slug}`:

| Результат скрипта | Новый `## Прогресс реализации` |
|-------------------|-------------------------------|
| `full` (100%) | `🟢 Полностью` |
| `partial` (N%) | `🟡 Частично (~N%) — {краткое описание из чеклиста}` |
| `none` (0%) | `🔴 Не начато` |
| `unknown` (нет чеклиста) | `🟢 Полностью` (если Accepted + verify-all-adr PASS) |

Для ADR с `partial` — добавь краткое описание того, что реализовано и что нет
(из секции чеклиста или inline-комментариев).

### 1.5. Трансформировать заголовок файла

**Из OLD (inline):**
```markdown
# ADR-017: Telegram Bot SaaS Platform

**Статус:** ✅ Принято

**Supersedes:** ADR-023 (merged 2026-02-18)

**Дата:** 2026-02-08 (обновлено: 2026-02-17)

**Автор:** AI Agent (Context7 research & analysis)

**Теги:** #saas #telegram-bot
```

**В NEW (dual-status):**
```markdown
# ADR-017: Telegram Bot SaaS Platform

## Topic slug
telegram-bot-saas-platform

## Слой реализации
Layer 4 — SaaS Platform

## Зависимости ADR
- unified-auth-architecture
- multi-user-approach

## Статус решения
Accepted

## Прогресс реализации
🟡 Частично (~37%) — базовая инфраструктура и core commands реализованы, не реализованы promo codes, 2FA, rate limiting, несколько K8s операций

**Supersedes:** ADR-023 (merged 2026-02-18)

## Дата
2026-02-08 (обновлено: 2026-02-17)

**Автор:** AI Agent (Context7 research & analysis)

**Теги:** #saas #telegram-bot
```

### 1.5.1. Правила для metadata полей (обязательно)

- `## Topic slug` — из имени файла (`ADR-NNN-{slug}.md` → `{slug}`)
- `## Слой реализации` — из актуальной layer-иерархии в `index.md` (Layer 0..5)
- `## Зависимости ADR` — из актуального Mermaid-графа зависимостей в `index.md`
- Если зависимость неизвестна, оставь `- TBD (уточнить по graph)` и зафиксируй в задачах на нормализацию

**Из OLD (heading):**
```markdown
# ADR-010: K8s provider abstraction

## Статус
✅ Принято

## Дата
2026-02-11
```

**В NEW (dual-status):**
```markdown
# ADR-010: K8s provider abstraction

## Статус решения
Accepted

## Прогресс реализации
🟢 Полностью

## Дата
2026-02-11
```

### 1.6. Категоризировать чеклист

**Целевая структура (из шаблона):**
```markdown
## Чеклист реализации

### Обязательные
- [x] Изменения внесены в код/скрипты/конфигурации
- [x] Тесты пройдены
- [x] Документация обновлена

### Условные (если затронуты)
- [x] Если затронуты config/variables/ — выполнен make generate-dev

### Специфичные для данного ADR
- [x] Конкретная функция X реализована
- [ ] Конкретный компонент Y не реализован

### Интеграция в проект
- [x] Добавлена запись в index.md
- [x] Прогресс реализации обновлён
```

**Правила категоризации существующих пунктов:**

| Категория | Какие пункты включать |
|-----------|----------------------|
| **Обязательные** | Изменения в коде/скриптах, тесты, документация, docs-build/validate |
| **Условные** | config/variables → generate, Make-цели → validate-no-aliases, docs-structure |
| **Специфичные** | Всё специфичное для этого ADR: конкретные функции, модули, endpoints, K8s ресурсы, команды бота |
| **Интеграция** | Запись в index.md, ссылки, прогресс обновлён |

> **⚠️ КРИТИЧНО:** При категоризации:
> - **Сохранить состояние** каждого пункта (`[x]`, `[ ]`, `[⚠️]`)
> - **Конвертировать** `[⚠️]` → `[ ]` (скрипт считает только `[x]` и `[ ]`)
> - **Сохранить текст** пункта дословно (можно переформулировать для краткости)
> - **НЕ УДАЛЯТЬ** ни один пункт — каждый пункт должен попасть в одну из 4 категорий
> - Строки с emoji-заголовками типа `### ✅ Реализовано (Core Infrastructure)` — это
>   визуальные группировки в old-формате. Пункты из них распределить по 4 категориям.
> - Текст `**Верификация (дата):**` перед чеклистом — перенести как HTML-комментарий
>   или удалить (эта информация теперь в `## Прогресс реализации`)

### 1.7. Добавить финальный пункт в "Интеграция"

Убедись, что в категории "Интеграция в проект" есть пункт:
```markdown
- [x] `## Прогресс реализации` обновлён в соответствии с чеклистом
```
(ставить `[x]`, т.к. мы его обновляем в ходе миграции)

### 1.8. Сохранить всё остальное AS-IS

Секции, которые **НЕ трогать** (только сохранить):
- `## Контекст` — дословно
- `## Решение` — дословно, включая код и примеры
- `## Последствия` — дословно
- `## Рассмотренные варианты` — дословно
- `## Реализация` / `## Implementation notes` — дословно
- `## Тестирование` — дословно
- `## Связанные ADR` / `## Связанные изменения` — дословно
- `## Ссылки` — дословно
- `## История` — дословно
- Mermaid-диаграммы, таблицы, code blocks — дословно
- Inline-примечания (`> **Note:**`, `> **⚠️ ВАЖНО:**`) — дословно
- Футер с версией/датой — дословно

---

## Шаг 2: Проверка после миграции каждого ADR

```bash
# 1. Проверить что прогресс не изменился
./scripts/verify-adr-checklist.sh --topic {slug}

# 2. Проверить структурную целостность
./scripts/verify-all-adr.sh --quick

# 3. Проверить что файл валиден (нет обрезанных секций)
wc -l docs/explanation/adr/ADR-NNN-{slug}.md
# Сравнить с оригиналом — размер должен быть ±10 строк

# 4. Проверить что нет потерянного контента
diff <(grep '^## ' original.md) <(grep '^## ' docs/explanation/adr/ADR-NNN-{slug}.md)
# Новые секции (Статус решения, Прогресс) допустимы; исчезновение старых — НЕТ
```

---

## Шаг 3: Batch-миграция (рекомендуемый workflow)

### Группа 1: Маленькие ADR (full progress, <150 строк)
```
ADR-005 k3s-vs-microk8s              (full,  43 строки)
ADR-018 gitops-validation            (full,  55 строк)
ADR-010 k8s-provider-abstraction     (full,  85 строк)
ADR-007 automatic-lets-encrypt       (full,  93 строки)
ADR-001 sysbox-choice                (full, 126 строк)
ADR-012 bash-formatting-standard     (full, 131 строка)
ADR-011 documentation-generation     (full, 132 строки)
ADR-019 metrics-alerting-strategy    (full, 134 строки)
```

### Группа 2: Средние ADR (full progress, 150-400 строк)
```
ADR-013 storage-provider-selection   (full, 189 строк)
ADR-014 e2e-testing-new-features     (full, 210 строк)
ADR-004 path-based-routing           (full, 210 строк)
ADR-006 multi-user-approach          (full, 231 строка)
ADR-008 unified-auth-architecture    (full, 234 строки)
ADR-002 k8s-provider-unification     (full, 261 строка)
ADR-003 websocket-fix                (full, 288 строк)
ADR-020 readme-autogeneration        (full, 291 строка)
ADR-016 centralized-logging          (full, 368 строк)
ADR-009 comprehensive-infra-refactor (full, 383 строки)
```

### Группа 3: Большие/сложные ADR (partial или >400 строк)
```
ADR-015 helm-chart-structure         (partial 57%, Proposed, 106 строк)
ADR-021 shared-storage               (full, 902 строки — осторожно, большой файл)
ADR-017 telegram-bot-saas-platform   (partial 37%, 1178 строк, 29 пунктов чеклиста)
```

> **⚠️ Для Группы 3:** Чеклисты уже имеют нестандартные категории
> (✅/⚠️/❌/📝 в ADR-017). Нужно аккуратно перераспределить по 4 стандартным категориям,
> конвертировав `[⚠️]` → `[ ]` и сохранив описания.

---

## Шаг 4: Финальная верификация

После миграции ВСЕХ ADR:

```bash
# 1. Полная проверка чеклистов
./scripts/verify-adr-checklist.sh
# Ожидание: те же самые проценты, что до миграции

# 2. Полная структурная верификация
./scripts/verify-all-adr.sh
# Ожидание: 93/93 PASS (или более, если скрипт проверяет new-формат)

# 3. Проверить что ВСЕ ADR в new-формате
for f in docs/explanation/adr/ADR-[0-9]*.md; do
  if ! head -20 "$f" | grep -q '## Статус решения'; then
    echo "OLD FORMAT: $f"
  fi
done
# Ожидание: пустой вывод (все мигрированы)

# 4. Обновить index.md (запустить index-update-prompt)
cat docs/ai-agent-prompts/promt-index-update.md

# 5. Пересчитать очередь внедрения (Critical Path + Layers)
# Контекст для index-update: миграция шаблона завершена, обновить queue + graph + статусы

# 6. Дополнительно пересчитать приоритеты planned/partial/full
cat docs/ai-agent-prompts/promt-verification.md
```

### 4.1. Migration Normalization Gate (обязательный)

После миграции обязательно пройти gate:
1. Проверить расхождения `Прогресс реализации` vs чеклист (`verify-adr-checklist.sh`).
2. Сверить `Topic slug`/`Layer`/`Зависимости ADR` с актуальным Mermaid-графом.
3. Обновить `index.md` через `promt-index-update.md` с секцией очереди внедрения.
4. Убедиться, что planned/partial/full покрывает все активные ADR.
5. Убедиться, что `docs/official_document/` не изменялась.

---

## Anti-Patterns (ЗАПРЕЩЕНО)

| ❌ Не делай | ✅ Делай вместо |
|---|---|
| Удалять или сокращать контент секций | Копировать дословно, менять только структуру |
| Менять `[x]` на `[ ]` или наоборот | Сохранять состояние каждого пункта |
| Удалять Mermaid-диаграммы, таблицы, code blocks | Сохранять все блоки на месте |
| Удалять inline-примечания (`> ⚠️ ВАЖНО:`) | Сохранять все заметки |
| Конвертировать `[⚠️]` в `[x]` | Конвертировать `[⚠️]` → `[ ]` (не завершено) |
| Менять slug в имени файла | Имя файла остаётся прежним |
| Менять заголовок `# ADR-NNN:` | Заголовок остаётся прежним |
| Мигрировать все 21 ADR за один коммит | Коммитить группами (3-5 ADR за коммит) |
| Добавлять пункты чеклиста, которых не было | Только перераспределять существующие |
| Менять нумерацию ADR | Номера не трогать вообще |

---

## Checklist перед завершением

- [ ] Все 21 ADR содержат `## Статус решения`
- [ ] Все 21 ADR содержат `## Прогресс реализации`
- [ ] Все 21 ADR содержат `## Topic slug`
- [ ] Все 21 ADR содержат `## Слой реализации`
- [ ] Все 21 ADR содержат `## Зависимости ADR`
- [ ] Все чеклисты имеют 4 категории: Обязательные / Условные / Специфичные / Интеграция
- [ ] `./scripts/verify-adr-checklist.sh` показывает те же проценты, что до миграции
- [ ] `./scripts/verify-all-adr.sh` → pass rate ≥ 95%
- [ ] Ни один пункт чеклиста не потерян (суммарное количество `[x]` + `[ ]` не уменьшилось)
- [ ] Deprecated ADR в `deprecated/` — тоже мигрированы (опционально)
- [ ] Git коммиты по группам (Группа 1 → Группа 2 → Группа 3)
- [ ] `docs/ai-agent-prompts/promt-index-update.md` запущен для обновления index.md
- [ ] В `index.md` сформирована актуальная очередь внедрения (Critical Path + Layers)
- [ ] Все ADR классифицированы в planned/partial/full без пропусков
- [ ] `docs/official_document/` не изменялась (read-only)

---

## Примеры трансформации

### Пример 1: Простой ADR (ADR-010, full, heading format)

**BEFORE:**
```markdown
# ADR-010: K8s provider abstraction — unified ${KUBECTL_CMD} detection & usage

## Статус
✅ Принято

## Дата
2026-02-11

## Контекст
[контент...]

## Чеклист реализации

**Верификация (2026-02-16):** Полностью реализовано.

- [x] `scripts/helpers/k8s-exec.sh` — все функции реализованы
- [x] Авто-детект k3s/microk8s/kubectl с fallback
- [x] Тесты: `tests/ci/test-kubectl-detection.sh`
- [x] Обновлена запись в `docs/explanation/adr/index.md`
```

**AFTER:**
```markdown
# ADR-010: K8s provider abstraction — unified ${KUBECTL_CMD} detection & usage

## Статус решения
Accepted

## Прогресс реализации
🟢 Полностью

## Дата
2026-02-11

## Контекст
[контент — без изменений...]

## Чеклист реализации

<!-- Верификация (2026-02-16): Полностью реализовано. -->

### Обязательные
- [x] `scripts/helpers/k8s-exec.sh` — все функции реализованы и экспортированы
- [x] Тесты: `tests/ci/test-kubectl-detection.sh`

### Условные (если затронуты)
- [x] Авто-детект k3s/microk8s/kubectl с fallback

### Специфичные для данного ADR
*(нет специфичных пунктов)*

### Интеграция в проект
- [x] Обновлена запись в `docs/explanation/adr/index.md`
- [x] `## Прогресс реализации` обновлён в соответствии с чеклистом
```

### Пример 2: Сложный ADR (ADR-017, partial, inline format)

**BEFORE (заголовок):**
```markdown
# ADR-017: Telegram Bot SaaS Platform — Comprehensive Architecture

**Статус:** ✅ Принято
**Supersedes:** ADR-023 (merged 2026-02-18)
**Дата:** 2026-02-08 (обновлено: 2026-02-17)
```

**AFTER (заголовок):**
```markdown
# ADR-017: Telegram Bot SaaS Platform — Comprehensive Architecture

## Статус решения
Accepted

## Прогресс реализации
🟡 Частично (~37%) — базовая инфраструктура (pydantic-settings, DB schema, YooKassa integration, basic commands) реализована; не реализованы promo codes, 2FA, rate limiting, команды /restart, /clean, /autopay

**Supersedes:** ADR-023 (merged 2026-02-18)

## Дата
2026-02-08 (обновлено: 2026-02-17)
```

**BEFORE (чеклист):**
```markdown
## Чеклист реализации

**Верификация (2026-02-17):** Реализовано частично (~50%).

### ✅ Реализовано (Core Infrastructure)
- [x] **Bot library:** python-telegram-bot v22.5+
- [x] **Application pattern:** Application.builder()
...

### ⚠️ Частично / Отличается от ADR
- [⚠️] **Структура модулей:** Вместо commands/ используется bot/
...

### ❌ Не реализовано (Planned)
- [ ] **Promo codes system**
...

### 📝 Требуется обновление
- [ ] Обновить custom instructions
...
```

**AFTER (чеклист):**
```markdown
## Чеклист реализации

<!-- Верификация (2026-02-17): Реализовано частично (~37%). -->

### Обязательные
- [x] **Bot library:** python-telegram-bot v22.5+
- [x] **Application pattern:** Application.builder() + async handlers
- [x] **Database schema:** Core tables (users, plans, subscriptions, payments, ...)
- [ ] Обновить custom instructions (убрать упоминание aiogram)

### Условные (если затронуты)
- [ ] Исправить комментарий в `jobs/job_manager.py` (строка 2)
- [ ] Рефакторинг структуры под паттерн `commands/` + `services/` (опционально)

### Специфичные для данного ADR
- [x] **Webhook security:** HMAC signature validation, idempotency
- [x] **YooKassa integration:** `app/payments/`
- [x] **K8s provisioner:** `app/k8s/provisioner.py` (basic CRUD)
- [x] **Job manager:** `app/jobs/job_manager.py`
- [x] **Notification system:** `app/bot/notifications.py`
- [x] **Monitoring:** `app/monitoring/metrics.py`
- [x] **Basic commands:** /start, /status, /help, /history, /cancel_subscription, /credentials
- [x] **Plan management:** `app/bot/plan_management.py`
- [ ] **Структура модулей:** Вместо commands/ используется bot/ (отличается от ADR)
- [ ] **JobQueue:** Кастомный asyncio JobManager вместо python-telegram-bot JobQueue
- [ ] **Команда /upgrade:** Частично реализована, не как CommandHandler
- [ ] **Команда /pause:** Только через callbacks
- [ ] **K8s operations:** Только create/delete, нет restart/suspend
- [ ] **Promo codes system:** /promo, PromoService
- [ ] **Confirmation codes (2FA):** security/confirmation.py
- [ ] **Rate limiting:** security/rate_limit.py
- [ ] **Команда /restart**
- [ ] **Команда /clean**
- [ ] **Команда /autopay**
- [ ] **K8s restart_namespace()**
- [ ] **K8s suspend_namespace()**

### Интеграция в проект
- [x] Добавлена запись в `docs/explanation/adr/index.md`
- [x] `## Прогресс реализации` обновлён в соответствии с чеклистом
```

> **Обратите внимание:** `[⚠️]` пункты конвертированы в `[ ]`, т.к. они описывают
> неполную реализацию. Emoji-заголовки (✅/⚠️/❌/📝) заменены на стандартные 4 категории.

---

## Связанные промпты

| Промпт | Когда использовать |
|--------|-------------------|
| `promt-verification.md` | После миграции — полная верификация всех ADR |
| `promt-index-update.md` | После миграции — обновить индекс с dual-status |
| `promt-consolidation.md` | При обнаружении дублей в процессе миграции |
| `promt-adr-implementation-planner.md` | После завершения миграции — построить очередь |

## Ресурсы

| Ресурс | Путь | Назначение |
|---|---|---|
| **ADR-файлы** | `docs/explanation/adr/ADR-*.md` | Требуют миграции к dual-status |
| **ADR-шаблон v2** | `docs/explanation/adr/ADR-template.md` | Целевой формат с двойным статусом |
| **ADR-индекс** | `docs/explanation/adr/index.md` | Актуальная иерархия Layer 0-5 |
| **Скрипт прогресса** | `scripts/verify-adr-checklist.sh` | Вычисление прогресса из чеклистов |
| **Скрипт структурной верификации** | `scripts/verify-all-adr.sh` | Проверка соответствия шаблону |
| **Правила проекта** | `.github/copilot-instructions.md` | ADR Topic Registry |
| **Официальная документация** | `docs/official_document/` | **READ-ONLY** эталон |
| **Meta-prompt** | `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md` | Source of truth |

---

## Связанные промпты

| Промпт | Когда использовать |
|--------|-------------------|
| `promt-verification.md` | После миграции — полная верификация Dual-Status |
| `promt-index-update.md` | После миграции всех ADR — обновить индекс и граф |
| `promt-consolidation.md` | При обнаружении дубликатов во время миграции |
| `promt-adr-implementation-planner.md` | построить очередь внедрения по Layer и Critical Path |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|----------|
| 1.4 | 2026-03-06 | Добавлены секции Gate I: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`. |
| 1.3 | 2026-02-25 | Нормализация: `## Чеклист`, `## Связанные промпты`, footer. |
| 1.2 | 2026-02-24 | Batch migration workflow, Layer 0→5 ordering. |

---

**Prompt Version:** 1.4
**Date:** 2026-03-06
**For:** GitHub Copilot, Claude, GPT-4, Roo или любой AI-агент
**Trigger:** Однократная миграция всех ADR после внедрения dual-status шаблона
**Prerequisites:** `scripts/verify-adr-checklist.sh` работает, `ADR-template.md` обновлён до v2
**Change:** v1.3 добавлена секция `## Связанные промпты` по каноническому скелету meta-promt-prompt-generation.md
