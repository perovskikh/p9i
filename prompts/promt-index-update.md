---
name: promt-index-update
version: "2.6"
type: CodeShift
layer: Operations
status: active
tags: [index, adr, regeneration]
---

# AI Agent Prompt: Автоматическое обновление ADR Index

**Version:** 2.6
**Date:** 2026-03-15
**Purpose:** Автоматическая регенерация `docs/explanation/adr/index.md` после любых ADR-операций.
Использует **двойной статус** (Decision Status + Implementation Progress), автоматический парсинг чеклистов,
актуальный Mermaid-граф зависимостей и построение очереди внедрения по Critical Path + Layer 0 → Layer 5.

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Operational |
| **Время выполнения** | 20–40 мин |
| **Домен** | ADR core — обновление индекса |

**Пример запроса:**

> «Используя `promt-index-update.md`, регенерируй `docs/explanation/adr/index.md`,
> статистику и Mermaid-граф после последних изменений ADR.»

**Ожидаемый результат:**
- Обновлённый `docs/explanation/adr/index.md` с актуальными статусами
- Mermaid dependency graph с текущим прогрессом
- Статистика ADR по статусам (Completed / In Progress / Planned)
- Очередь внедрения по Critical Path обновлена

---

## Когда использовать

- После добавления, изменения или депрекации любого ADR
- После `promt-consolidation.md` (слияние ADR изменило состав)
- После `promt-adr-template-migration.md` (изменились статусы)
- Раз в спринт — синхронизировать индекс с реальным состоянием

> **Обязателен после:** любой операции с ADR-файлами.
> Всегда запускать в паре с `promt-verification.md`.

---

## Mission Statement

Ты — AI-агент, специализирующийся на **автоматическом обновлении ADR index** проекта CodeShift.
Твоя задача — **регенерировать** файл `docs/explanation/adr/index.md` так, чтобы он точно отражал
текущее состояние всех ADR в проекте: их количество, статусы, связи и метаданные.

**Триггеры запуска этого промпта:**
- После верификации (`./scripts/verify-all-adr.sh`)
- После консолидации / слияния ADR
- После добавления нового ADR
- После изменения статуса ADR (Proposed → Принято → Deprecated)
- После ренумерации ADR
- После `feature-add` / `feature-remove` нормализации (gate), когда меняются зависимости или прогресс

---

## Контракт синхронизации системы

Этот промпт управляется из единой точки: `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`.

Обязательные инварианты синхронизации:
- Источник истины по статусам: dual-status + результаты `verify-adr-checklist.sh`
- Идентификация ADR по topic slug, а не по номеру
- Очередь внедрения синхронизируется с Mermaid dependency graph
- Context7 шаг обязателен перед пересборкой при изменениях архитектурных правил
- `docs/official_document/` — только чтение

---

## Назначение

Этот промпт обновляет ADR-индекс, граф зависимостей и очередь внедрения на основании фактического состояния ADR.

## Входы

- Текущие `docs/explanation/adr/ADR-*.md` и `docs/explanation/adr/index.md`
- Результаты `scripts/verify-all-adr.sh` и `scripts/verify-adr-checklist.sh`
- Изменения после feature/consolidation/migration workflow

## Выходы

- Обновлённый `docs/explanation/adr/index.md` (таблицы, статистика, очередь, Mermaid)
- Согласованные статусы и прогресс по topic slug
- Валидный индекс без конфликтов с архитектурными инвариантами

## Ограничения / инварианты

- Следовать ограничениям I-1..I-9 и Constraints C1–C13 из meta-prompt (v2.2)
- Использовать topic slug как единственный стабильный ключ (C11)
- Прогресс брать из `verify-adr-checklist.sh`, а не из декларативных полей
- Поддерживать dual-status и согласованность с ADR-файлами
- Соблюдать Diátaxis, Anti-Legacy и update in-place (C9)
- Context7 использовать для dependency DAG и roadmap (C12)
- docs/official_document/ = READ-ONLY (C13)

## Workflow шаги

1. Discovery: собрать актуальный список ADR и baseline прогресса
2. Rebuild: обновить таблицы, зависимости и queue logic
3. Validate: сверить данные с verification scripts
4. Publish: зафиксировать индекс в консистентном состоянии

## Проверки / acceptance criteria

- Все изменения в `index.md` соответствуют актуальным ADR-файлам
- Mermaid-граф и очередь внедрения отражают реальные зависимости/прогресс
- Нет ссылок на legacy как active source

## Связи с другими промптами

- До: `promt-verification.md`, `promt-consolidation.md`, `promt-feature-add.md`, `promt-feature-remove.md`
- После: `promt-adr-implementation-planner.md` (для next-step планирования)

---

## Project Context

### О проекте

**CodeShift** — multi-tenant SaaS платформа для VS Code в браузере через Telegram Bot с YooKassa.

### ADR Topic Registry

> **КРИТИЧНО:** ADR идентифицируются по **topic slug** (не по номеру). Номера нестабильны.
> Поиск: `find docs/explanation/adr -name "ADR-*-{slug}*.md" | head -1`

| Topic Slug | Краткое описание |
|---|---|
| `sysbox-choice` | Docker-in-Kubernetes через Sysbox |
| `k8s-provider-unification` | Унификация K8s провайдеров (концепт) |
| `websocket-fix` | WebSocket через Traefik |
| `path-based-routing` | Single domain, path-based routing |
| `k3s-vs-microk8s` | Выбор между K3s и MicroK8s |
| `multi-user-approach` | Multi-user code-server |
| `automatic-lets-encrypt` | SSL Let's Encrypt автоматизация |
| `unified-auth-architecture` | JWT + Telegram auth |
| `comprehensive-infrastructure-refactor` | Инфраструктурный рефакторинг |
| `k8s-provider-abstraction` | `$KUBECTL_CMD` абстракция |
| `documentation-generation` | Diátaxis + автогенерация docs |
| `bash-formatting-standard` | shfmt + editorconfig |
| `storage-provider-selection` | Longhorn/local-path/OpenEBS |
| `e2e-testing-new-features` | E2E тестирование |
| `helm-chart-structure-optimization` | Оптимизация Helm chart |
| `centralized-logging-grafana-loki` | Loki + Promtail + Grafana |
| `telegram-bot-saas-platform` | Telegram Bot SaaS (CRITICAL) |
| `gitops-validation` | ArgoCD + GitOps |
| `metrics-alerting-strategy` | Prometheus + Grafana alerting |
| `readme-autogeneration-solution` | generate-readme.sh |
| `shared-storage-code-server-nextcloud` | Shared PVC для code-server + Nextcloud |

### Критические ADR (5 ключевых тем)

Эти ADR определяют архитектурный фундамент и ДОЛЖНЫ быть помечены в index.md:
1. **path-based-routing** — Single domain, NO subdomains
2. **k8s-provider-abstraction** — `$KUBECTL_CMD`, never hardcode
3. **storage-provider-selection** — Longhorn (prod), local-path (dev)
4. **telegram-bot-saas-platform** — pydantic-settings, env vars
5. **documentation-generation** — Reference docs AUTO-GENERATED only

---

## Твой рабочий процесс

### Шаг 0: Context7 + official docs (ОБЯЗАТЕЛЬНО)

Перед регенерацией index.md выполни краткое исследование через Context7:

```text
Запрос к Context7:
- Тема: dependency graph / implementation roadmap / architecture decision tracking
- Что получить: best practices по синхронизации decision status, implementation progress, dependency DAG
- Выход: правила приоритизации очереди внедрения (critical path + layers)
```

Используй `docs/official_document/` как read-only эталон терминов/паттернов.
**Никогда не изменяй** файлы в `docs/official_document/`.

### Шаг 1: Сбор данных (ДИНАМИЧЕСКИ)

**1.1. Список активных ADR:**
```bash
# Получить ВСЕ активные ADR файлы (не deprecated, не template)
find docs/explanation/adr -maxdepth 1 -name "ADR-[0-9]*.md" | sort -V
```

**1.2. Для каждого ADR файла извлечь метаданные:**
```bash
# Для каждого файла:
FILE="docs/explanation/adr/ADR-NNN-slug.md"

# 1) Номер и slug из имени файла
BASENAME=$(basename "$FILE" .md)      # ADR-001-sysbox-choice
NUMBER=$(echo "$BASENAME" | grep -o 'ADR-[0-9]*')  # ADR-001
SLUG=$(echo "$BASENAME" | sed 's/^ADR-[0-9]*-//')   # sysbox-choice

# 2) Заголовок (первая строка # )
TITLE=$(head -20 "$FILE" | grep -m1 '^# ADR-' | sed 's/^# //')
# Fallback: если заголовок внутри ```markdown блока
[ -z "$TITLE" ] && TITLE=$(head -20 "$FILE" | grep -m1 '^# ' | sed 's/^# //')

# 3) Статус — ТОЛЬКО из первых 15 строк (формальное поле **Статус решения:** или **Статус:**)
# ❗ НЕ сканировать тело файла
STATUS=$(head -15 "$FILE" | grep -m1 '^\*\*Статус решения:\*\*\|^\*\*Статус:\*\*\|^## Статус$' | sed 's/.*Статус[  решения:\*]*//' | sed 's/\*//g' | xargs)
# Fallback: если ## Статус на отдельной строке (значение на следующей строке)
if [ -z "$STATUS" ]; then
  LINE_NUM=$(head -20 "$FILE" | grep -n -m1 '^## Статус$\|^## Статус решения$' | cut -d: -f1)
  [ -n "$LINE_NUM" ] && STATUS=$(sed -n "$((LINE_NUM + 1))p" "$FILE" | sed 's/\*//g' | xargs)
fi

# 4) Прогресс реализации (НОВОЕ в v2.0)
# Используется для определения отображаемого статуса в index.md
PROGRESS=$(./scripts/verify-adr-checklist.sh --topic "$SLUG" --format short 2>/dev/null | cut -d: -f3-4)
# PROGRESS формат: "progress_level:pct" (например "full:100" или "partial:37")

# 4) Дата
DATE=$(grep -m1 -i 'дата\|date' "$FILE" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)

# 5) Supersedes
SUPERSEDES=$(grep -i 'supersedes\|заменяет' "$FILE" | head -1)
```

**1.3. Список deprecated ADR:**
```bash
find docs/explanation/adr/deprecated -maxdepth 1 -name "ADR-*.md" 2>/dev/null | sort -V
```

**1.4. Результаты последней верификации:**
```bash
# Запустить верификацию и получить результат
./scripts/verify-all-adr.sh 2>&1 | tail -10

# Или прочитать последний отчёт
ls -t artifacts/ADR-VERIFICATION-REPORT-*.md 2>/dev/null | head -1
```

**Примечание:** если окружение доступно, **обязательно запускай** `./scripts/verify-all-adr.sh` (и при необходимости `./scripts/generate-adr-verification-report.sh`) перед обновлением index.md; если запуск невозможен, используй последний доступный отчёт из `artifacts/` как источник статуса.

**1.5. Superseded связи:**
```bash
# Найти все Supersedes ссылки
grep -rl 'Supersedes\|superseded\|Заменяет' docs/explanation/adr/ADR-*.md
```

### Шаг 2: Классификация статусов (v2.0 — ДВОЙНОЙ СТАТУС)

Нормализовать статусы к единому формату, используя **ОБА** поля (статус решения + прогресс реализации):

| Статус решения | Прогресс (из чеклиста) | Emoji | Отображение в index.md |
|---|---|---|---|
| `Proposed`, `Draft` | любой | ⏳ | Proposed |
| `Accepted`, `Принято` | full (100%) | ✅ | Реализовано |
| `Accepted`, `Принято` | partial (1-99%) | ⚠️ | Частично (~N%) |
| `Accepted`, `Принято` | none (0%) | 📋 | Принято (не начато) |
| `Accepted`, `Принято` | unknown (нет чеклиста) | ✅ | Принято |
| `Completed` | любой | ✅ | Completed |
| `Superseded by ...` | любой | 🔄 | Superseded |
| `Deprecated`, `Отклонено` | любой | ❌ | Deprecated |

**Правило:** Статус в index.md определяется КОМБИНАЦИЕЙ статуса решения и прогресса чеклиста.
"Принято" НЕ значит "Реализовано". Для определения прогресса используй `./scripts/verify-adr-checklist.sh`.

> **⚠️ КРИТИЧНО (v2.0):** НИКОГДА не отображай "✅ Реализовано" для ADR,
> у которого в чеклисте есть незакрытые пункты `[ ]` в секциях "Обязательные" или
> "Специфичные для данного ADR". Это именно та ошибка, которая привела к ADR-017
> (реализован на ~37%) отображающемуся как "✅ Реализовано" в index.md.

> **Как определить прогресс:**
> ```bash
> # Автоматический парсинг чеклистов ВСЕХ ADR
> ./scripts/verify-adr-checklist.sh
>
> # Для конкретного ADR по topic slug
> ./scripts/verify-adr-checklist.sh --topic {slug}
>
> # Машиночитаемый формат
> ./scripts/verify-adr-checklist.sh --format short
> ```
>
> Скрипт парсит `## Чеклист реализации`, подсчитывает `[x]` vs `[ ]` и определяет
> прогресс: full / partial / none / unknown.

### Шаг 3: Определить статистику

Подсчитать (используя вывод `./scripts/verify-adr-checklist.sh`):
- **Полное соответствие** — ADR с ✅ (Accepted + full/unknown checklist)
- **Частичная реализация** — ADR с ⚠️ (Accepted + partial checklist)
- **Не начато** — ADR с 📋 (Accepted + none checklist)
- **Superseded** — ADR, заменённые другими
- **Proposed** — ADR в статусе ⏳
- **Deprecated** — Файлы в `deprecated/` директории

### Шаг 3.5: Построить очередь внедрения (ОБЯЗАТЕЛЬНО)

Сформируй очередь внедрения ADR на основе **актуального графа зависимостей** и реального прогресса:

1. Построй DAG зависимостей из Mermaid-графа и связей ADR (topic slug, не номера).
2. Выдели Critical Path (самая длинная цепочка зависимостей).
3. Примени слоевой порядок: Layer 0 → Layer 1 → Layer 2 → Layer 3 → Layer 4 → Layer 5.
4. Внутри слоя приоритизируй: `partial` перед `none`, а `full` исключай из очереди.
5. Заблокируй Layer N+1, если в Layer N есть блокирующие зависимости с `none/partial`.

**Формат секции в index.md (обязательный):**

```markdown
## Очередь внедрения ADR (Critical Path + Layers)

### Critical Path
ADR-010 (k8s-provider-abstraction) → ADR-004 (path-based-routing) → ...

### Layered Queue
1. [L1] `topic-slug` — статус: ⚠️ Частично (~N%), причина приоритета: [dependency/blocker]
2. [L2] `topic-slug` — статус: 📋 Принято (не начато), причина приоритета: [critical path]
```

> Если Mermaid-граф и фактические зависимости расходятся, обнови Mermaid-граф и затем пересчитай очередь.

### Шаг 4: Построить секции index.md

Файл `docs/explanation/adr/index.md` ДОЛЖЕН содержать следующие секции **в этом порядке:**

```markdown
# Architecture Decision Records

[Вводный параграф с датой обновления и статистикой]

## Итоги последнего аудита (YYYY-MM-DD)

### 📊 Общая статистика
[Таблица: категория / количество / процент]

### ✅ Критически важные ADR (100% соответствие)
[Нумерованный список с evidence links]

### ⚠️ Частичная реализация (требуют внимания)
[Таблица: ADR / Что реализовано / Что отсутствует / Приоритет]

### 🎯 Ключевые находки
[Положительные + требующие внимания]

### 📌 Рекомендации
[Immediate / Medium term / Low priority / Next audit date]

## ADR по номерам
[Таблица: ADR link / Тема / Статус — ВСЕ активные ADR]

### Deprecated ADR
[Таблица: ADR link / Причина / Объединён с]

## Критические расхождения
[Таблица или "Нет критических расхождений"]

## Superseded ADR
[Таблица: Ранний / Заменён на / Тема]

## Процесс поддержания актуальности
[Периодичность / Триггеры / Действия — статическая секция]

## Иерархия реализации ADR
[Mermaid граф зависимостей — обновлять при добавлении/удалении ADR]
```

### Шаг 5: Генерация таблицы "ADR по номерам"

**Формат строки таблицы:**
```markdown
| [ADR-NNN](ADR-NNN-slug.md) | Тема из заголовка | [emoji] Статус |
```

**Правила:**
1. Ссылки — относительные пути внутри `docs/explanation/adr/`
2. Тема — из заголовка ADR файла (без `ADR-NNN:` префикса)
3. Статус — нормализованный emoji + текст
4. Сортировка — по номеру ADR (числовая)
5. **Не включать** deprecated ADR в основную таблицу (они в отдельной секции)
6. **Не включать** ADR-template.md

**Пример:**
```markdown
| [ADR-001](ADR-001-sysbox-choice.md) | Выбор Sysbox для Docker-in-Kubernetes | ✅ Реализовано |
| [ADR-002](ADR-002-k8s-provider-unification.md) | Унификация K8s провайдеров | 🔄 Superseded by 010 |
```

### Шаг 6: Генерация "Критически важные ADR"

**Для каждого ADR со 100% реализацией**, добавить evidence link — конкретный файл/строку кода, подтверждающую реализацию:

```markdown
1. **ADR-001** (Sysbox) — `runtimeClassName: sysbox` в [templates/deployment.yaml](../../templates/deployment.yaml#L27)
```

**Как найти evidence:**
```bash
# Для каждого ADR прочитать ## Чеклист реализации
grep -A 50 '## Чеклист реализации\|## Implementation Checklist' "$FILE" | head -50

# Или искать ключевые паттерны
grep -rl 'sysbox\|runtimeClassName' templates/ | head -1
```

### Шаг 7: Обновить Mermaid граф

**Когда обновлять граф:**
- Добавлен новый ADR → добавить узел в соответствующий Layer
- Удалён/deprecated ADR → убрать узел
- Изменились зависимости → обновить стрелки

**Структура слоёв:**
```
Layer 0: Foundation (Sysbox, Bash formatting, Docs, Testing)
Layer 1: K8s Abstraction (provider unification, abstraction)
Layer 2: Networking & SSL (WebSocket, path routing, SSL, storage)
Layer 3: Application (multi-user, auth, shared storage)
Layer 4: SaaS Platform (Telegram Bot, GitOps, Metrics)
Layer 5: Polish (Helm opt, Logging, README autogen)
```

**Цветовая схема:**
- ✅ Реализовано → `fill:#51cf66,stroke:#2f9e44,color:#fff` (зелёный)
- ⚠️ Частично → `fill:#ffd43b,stroke:#f59f00` (жёлтый)
- ⏳ Proposed → `fill:#74c0fc,stroke:#339af0` (синий)
- 🔄 Superseded → `fill:#dee2e6,stroke:#868e96` (серый)

### Шаг 8: Обновить mkdocs.yml навигацию

Если количество или состав ADR изменились, обновить `mkdocs.yml`:

```yaml
# Секция ADR в mkdocs.yml — display text = тема (topic), path = файл
- ADR:
  - Index: explanation/adr/index.md
  - Topic Name: explanation/adr/ADR-NNN-slug.md
  ...
  - Template: explanation/adr/ADR-template.md
```

**Правила для mkdocs.yml:**
- Display text = человекочитаемое имя темы (не номер)
- Путь = фактическое имя файла
- Порядок = по номеру ADR
- Template всегда последний

---

## Формат входных данных

При запуске этого промпта, агент должен получить одно из:

### Вариант A: После верификации
```
Контекст: Только что завершена верификация ADR.
Результат: [вставить вывод ./scripts/verify-all-adr.sh]
Действие: Обновить index.md по результатам верификации.
```

### Вариант B: После консолидации
```
Контекст: Проведена консолидация ADR.
Что изменилось:
- Объединены: [список пар topic_A ← topic_B]
- Deprecated: [список topic slugs]
- Ренумерация: [да/нет]
Действие: Полная регенерация index.md + mkdocs.yml.
```

### Вариант C: После добавления нового ADR
```
Контекст: Добавлен новый ADR.
Файл: docs/explanation/adr/ADR-NNN-new-slug.md
Topic slug: new-slug
Статус: [Proposed/Принято]
Layer: [0-5]
Зависимости: [от каких ADR зависит]
Действие: Добавить в index.md + mkdocs.yml + Mermaid граф.
```

### Вариант D: Полная регенерация (без контекста)
```
Контекст: Требуется полная регенерация index.md из текущего состояния файловой системы.
Действие: Просканировать все ADR, собрать метаданные, сгенерировать index.md с нуля.
```

---

## Критические правила

### 1. Динамическое обнаружение (НИКАКОГО хардкода)
```bash
# ✅ ПРАВИЛЬНО: динамически обнаруживать ADR
find docs/explanation/adr -maxdepth 1 -name "ADR-[0-9]*.md" | sort -V

# ❌ НЕПРАВИЛЬНО: хардкодить список файлов
FILES=("ADR-001-sysbox-choice.md" "ADR-002-k8s-provider-unification.md" ...)
```

### 2. Topic slug — первичный идентификатор
- В комментариях, описаниях и рекомендациях → используй topic slug
- В ссылках и путях → используй фактическое имя файла
- В display text → тема на русском (не `ADR-NNN`)

### 3. Evidence links (доказательства реализации)
- Каждый ADR со статусом ✅ ДОЛЖЕН иметь evidence link
- Evidence = конкретный файл + строка кода (если возможно)
- Формат: `[file.yaml](../../relative/path#L123)`

### 4. Mermaid граф — ОБЯЗАТЕЛЬНОЕ обновление
- При любом изменении состава ADR → обновить граф
- Цвета узлов = статус реализации
- Стрелки = архитектурные зависимости

### 5. Дата аудита
- Вводный параграф ВСЕГДА содержит дату последнего обновления
- Формат: `> **Последний аудит:** YYYY-MM-DD.`
- Рекомендовать дату следующего аудита: +90 дней

### 6. Не удалять статические секции
- "Процесс поддержания актуальности" — шаблонная секция, обновлять только при изменении процесса
- "Критический путь" — обновлять при изменении зависимостей
- "Правила применения" — не менять без явного запроса

### 7. Согласованность с mkdocs.yml
- Каждый ADR в index.md ДОЛЖЕН быть в навигации mkdocs.yml
- Каждый deprecated ADR НЕ ДОЛЖЕН быть в mkdocs.yml навигации
- Template всегда включён

### 8. Официальная документация (read-only)
- `docs/official_document/` используется только как источник истины для терминов и ссылок; **не изменять** содержимое. При расхождениях между ADR и официальной документацией фиксируй это в выводе и применяй решения, не затрагивая официальные файлы.

### 9. Критический путь и правила применения (context7 best practices)
- Блок "Критический путь" обновлять **только** при изменении зависимостей или последовательности внедрения, опираясь на актуальный Mermaid-граф и зависимости ADR.
- Блок "Правила применения" **не менять без явного запроса**; возможные улучшения отражать в разделе рекомендаций, не переписывая текст секции.

### 10. Очередь внедрения — обязательный артефакт
- После каждого обновления index.md в нём должна быть актуальная секция очереди внедрения.
- Очередь строится по topic slug и не может опираться только на номера ADR.
- Очередь должна быть согласована с `./scripts/verify-adr-checklist.sh` (реальный progress).

---

## Валидация результата

После генерации index.md, проверить:

```bash
# 1. Количество ADR в таблице = количество файлов
TABLE_COUNT=$(grep -c '^\| \[ADR-' docs/explanation/adr/index.md)
FILE_COUNT=$(find docs/explanation/adr -maxdepth 1 -name "ADR-[0-9]*.md" | wc -l)
[ "$TABLE_COUNT" = "$FILE_COUNT" ] && echo "✅ Count matches" || echo "❌ Mismatch: table=$TABLE_COUNT files=$FILE_COUNT"

# 2. Все ссылки в таблице валидны
grep -oP '\(ADR-[^)]+\.md\)' docs/explanation/adr/index.md | tr -d '()' | while read f; do
  [ -f "docs/explanation/adr/$f" ] || echo "❌ Broken link: $f"
done

# 3. Deprecated в отдельной таблице
grep -c 'deprecated/' docs/explanation/adr/index.md

# 4. Mermaid граф присутствует
grep -c 'mermaid' docs/explanation/adr/index.md

# 5. Дата аудита обновлена
grep 'Последний аудит' docs/explanation/adr/index.md

# 6. mkdocs.yml синхронизирован
MKDOCS_COUNT=$(grep -c 'explanation/adr/ADR-[0-9]' mkdocs.yml)
echo "mkdocs.yml ADR entries: $MKDOCS_COUNT (should be $FILE_COUNT)"

# 7. Верификация всё ещё проходит
./scripts/verify-all-adr.sh --quick 2>&1 | tail -5

# 8. Критические статические секции присутствуют (НЕ удалять при генерации!)
grep -q 'Критический путь' docs/explanation/adr/index.md \
  && echo "✅ Критический путь present" || echo "❌ MISSING: Критический путь"
grep -q 'Процесс поддержания актуальности' docs/explanation/adr/index.md \
  && echo "✅ Процесс поддержания актуальности present" || echo "❌ MISSING: Процесс поддержания актуальности"
grep -q 'Правила применения' docs/explanation/adr/index.md \
  && echo "✅ Правила применения present" || echo "❌ MISSING: Правила применения"
grep -q 'Иерархия реализации ADR\|graph TD' docs/explanation/adr/index.md \
  && echo "✅ Mermaid dependency graph present" || echo "❌ MISSING: Mermaid dependency graph"

# 9. Секция очереди внедрения присутствует и непустая
grep -q 'Очередь внедрения ADR' docs/explanation/adr/index.md \
  && echo "✅ Implementation queue present" || echo "❌ MISSING: Implementation queue"

# 10. Queue учитывает topic slug и critical path
grep -q 'Critical Path' docs/explanation/adr/index.md \
  && echo "✅ Critical Path present" || echo "❌ MISSING: Critical Path section"
```

---

## Пример: Добавление нового ADR-022

**Вход:**
```
Добавлен: docs/explanation/adr/ADR-022-ci-cd-pipeline-optimization.md
Topic: ci-cd-pipeline-optimization
Статус: ⏳ Proposed
Layer: 5 (Polish)
Зависимости: ADR-014 (E2E Testing), ADR-018 (GitOps)
```

**Действия агента:**

1. **index.md — Вводный параграф:**
   ```markdown
   > **Последний аудит:** 2026-02-19. После обновления: 22 активных ADR + 4 deprecated.
   ```

2. **index.md — Общая статистика:**
   Пересчитать все категории (было 21, стало 22).

3. **index.md — Таблица "ADR по номерам":**
   Добавить строку:
   ```markdown
   | [ADR-022](ADR-022-ci-cd-pipeline-optimization.md) | CI/CD Pipeline Optimization | ⏳ Proposed |
   ```

4. **index.md — Mermaid граф:**
   Добавить в Layer 5:
   ```mermaid
   graph TD
       A014 --> A022
       A018 --> A022
       A022["ADR-022: CI/CD Pipeline"]
       style A022 fill:#74c0fc,stroke:#339af0
   ```

5. **mkdocs.yml:**
   Добавить строку перед Template:
   ```yaml
   - CI/CD Pipeline: explanation/adr/ADR-022-ci-cd-pipeline-optimization.md
   ```

6. **Валидация:**
   ```bash
   # Все ссылки валидны
   # mkdocs build не ломается
   # verify-all-adr.sh --quick проходит
   ```

---

## Пример: После консолидации (слияние + deprecated)

**Вход:**
```
Объединены: e2e-testing-new-features ← phase-7-testing-edge-cases
Deprecated: docs/explanation/adr/deprecated/ADR-020-phase-7-testing-edge-cases.md → merged into ADR-014
```

**Действия агента:**

1. Удалить строку ADR-020 из основной таблицы
2. Добавить в таблицу "Deprecated ADR"
3. Обновить статистику (активных -1, deprecated +1)
4. Убрать узел A020 из Mermaid графа и перенаправить его стрелки на A014
5. Убрать строку из mkdocs.yml навигации
6. Обновить evidence links для ADR-014 (если изменились)

---

## Anti-Patterns (НИКОГДА не делай)

| ❌ Не делай | ✅ Делай вместо |
|---|---|
| Хардкодить список ADR в промпте | Динамически сканировать файловую систему |
| Использовать `ADR-NNN` как primary ID | Использовать topic slug для идентификации |
| Удалять секции из index.md | Обновлять/дополнять существующие секции |
| Оставлять broken links | Проверять existence каждой ссылки |
| Пропускать Mermaid граф | Обновлять граф при ЛЮБОМ изменении |
| Забывать mkdocs.yml | Синхронизировать навигацию с index.md |
| Копировать статус из файла без проверки | Запустить `./scripts/verify-adr-checklist.sh` и сверить |
| Оставлять deprecated в основной таблице | Переносить в секцию "Deprecated ADR" |
| Маппить "Принято" → "Реализовано" без проверки чеклиста | Использовать ДВОЙНОЙ статус: решение + прогресс чеклиста |
| Отображать ✅ для ADR с незакрытыми `[ ]` в обязательных пунктах | Показывать ⚠️ Частично (~N%) с реальным процентом из чеклиста |
| Игнорировать `## Чеклист реализации` как "заметки" | Чеклист — ЕДИНСТВЕННЫЙ источник прогресса реализации |
| Удалять или перезаписывать секции "Критический путь", "Процесс поддержания актуальности", "Правила применения" | Проверять присутствие этих секций; обновлять только при явном изменении зависимостей |

---

## Ресурсы

| Ресурс | Путь | Описание |
|---|---|---|
| ADR файлы | `docs/explanation/adr/ADR-*.md` | Исходные документы |
| Deprecated ADR | `docs/explanation/adr/deprecated/` | Устаревшие ADR |
| ADR Template | `docs/explanation/adr/ADR-template.md` | Шаблон для новых ADR |
| Верификация структуры | `scripts/verify-all-adr.sh` | 93+ проверок, topic-based |
| Верификация чеклистов | `scripts/verify-adr-checklist.sh` | Прогресс реализации из чеклистов |
| Отчёт | `scripts/generate-adr-verification-report.sh` | Генерация отчёта |
| MkDocs навигация | `mkdocs.yml` | Навигация сайта |
| Copilot Instructions | `.github/copilot-instructions.md` | ADR Topic Registry |
| Consolidation Prompt | `docs/ai-agent-prompts/promt-consolidation.md` | Промпт для слияния ADR |
| Официальная документация | `docs/official_document/` | Read-only поставщикский источник терминов |

---

## Checklist перед завершением

- [ ] `docs/explanation/adr/index.md` обновлён
- [ ] Дата аудита актуальна
- [ ] Количество ADR в таблице = количеству файлов
- [ ] Все ссылки в таблице валидны (файлы существуют)
- [ ] Deprecated ADR в отдельной секции
- [ ] Mermaid граф обновлён (узлы, стрелки, цвета)
- [ ] Статистика пересчитана
- [ ] Evidence links для ✅ ADR присутствуют
- [ ] `mkdocs.yml` навигация синхронизирована
- [ ] `./scripts/verify-all-adr.sh --quick` проходит
- [ ] `./scripts/verify-adr-checklist.sh` запущен и результат использован
- [ ] НИ ОДИН ADR с незакрытыми обязательными пунктами не показан как ✅
- [ ] Секция "Очередь внедрения ADR (Critical Path + Layers)" сформирована и актуальна
- [ ] Секция "Критический путь" присутствует в index.md
- [ ] Секция "Процесс поддержания актуальности" не удалена
- [ ] Секция "Правила применения" не изменена (если не было явного запроса)
- [ ] Статус ADR определён по ДВОЙНОЙ системе: статус решения + прогресс чеклиста

---

## Связанные промпты

| Промпт | Когда использовать |
|--------|-------------------|
| `promt-verification.md` | Перед обновлением — получить актуальные данные по всем ADR |
| `promt-consolidation.md` | После консолидации — обновить граф и статистику |
| `promt-adr-implementation-planner.md` | После обновления — построить план реализации |
| `promt-feature-add.md` | При добавлении нового ADR — обновить навигацию |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 2.6 | 2026-03-15 | Обновлён index.md: дата аудита 2026-03-15, ADR-017 39%, версия 2.7. |
| 2.5 | 2026-03-13 | Исправлена дата. |
| 2.4 | 2026-03-06 | Добавлены секции Gate I: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`. |
| 2.3 | 2026-02-25 | Нормализация: `## Чеклист`, `## Связанные промпты`, footer; Critical Path Layers. |
| 2.1 | 2026-02-24 | Обязательный артефакт очереди внедрения + Context7 шаг. |

---

**Prompt Version:** 2.6
**For:** GitHub Copilot, Claude, GPT-4, Roo или любой AI-агент
**Trigger:** После любой ADR-операции (верификация, консолидация, добавление, изменение)
