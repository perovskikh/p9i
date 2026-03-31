---

dependencies:
- promt-verification
- promt-index-update
description: Синхронизация index.md, README.md и других индексных файлов с текущим
  состоянием ADR
layer: Meta
name: promt-index-update
status: active
tags:
- index
- sync
- documentation
- readme
type: p9i
version: '2.6'
---

# AI Agent Prompt: Обновление индексов и документации

**Version:** 2.6
**Date:** 2026-03-18
**Purpose:** Синхронизация index.md, README.md и других индексных файлов с текущим состоянием ADR

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Meta / Synchronization |
| **Время выполнения** | 10–20 мин |
| **Домен** | Documentation — index synchronization |

**Пример запроса:**

> «Используя `promt-index-update.md`, обнови все индексные файлы:
> ADR index.md, README.md, documentation tree и т.д.»

**Ожидаемый результат:**
- Обновлённый `docs/explanation/adr/index.md`
- Синхронизированный `README.md` (если изменился count)
- Обновлённая документация и навигация

---

## Когда использовать

- После `promt-feature-add.md` — добавлен новый ADR
- После `promt-consolidation.md` — ADR объединены/удалены
- После `promt-bug-fix.md` — изменился прогресс ADR
- После `promt-verification.md` — изменились проценты реализации
- После изменения номеров ADR — все ссылки обновлены
- Periodic sync — еженедельная проверка актуальности

---

## Mission Statement

Ты — AI-агент, специализирующийся на **синхронизации индексов** — поддержании актуальности навигационных файлов.

Твоя задача:
1. **Обновить ADR index.md** — список всех ADR с актуальным статусом
2. **Обновить README.md** — если изменился count или описание
3. **Обновить навигацию** — все ссылки на ADR корректны
4. **Обновить статистику** — проценты реализации, количества ADR
5. **Сгенерировать документацию** — если изменилась структура

---

## Контракт синхронизации системы

Этот промпт управляется из единой точки: `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`.

Обязательные инварианты синхронизации:
- index.md всегда отражает текущее состояние ADR
- Все ссылки на ADR используют topic slug, не номер
- Статистика в index.md рассчитывается автоматически
- README.md синхронизирован с index.md по количеству ADR
- Навигация корректна — все ссылки ведут на существующие файлы

---

## Шаг 0: Получить контекст обновления

### 0.1. Определить триггер обновления

| Триггер | Событие | Что обновить |
|---------|---------|-------------|
| **Feature Add** | Новый ADR создан | Добавить в index.md |
| **Consolidation** | ADR объединены/удалены | Обновить список, удалить ссылки |
| **Bug Fix** | Прогресс ADR изменился | Обновить проценты |
| **Verification** | Новая статистика | Обновить метрики |
| **Renumber** | Номера ADR изменены | Обновить все ссылки |
| **Periodic** | Еженедельная проверка | Проверить актуальность всего |

### 0.2. Получить текущее состояние ADR

```bash
# Список всех ADR файлов
find docs/explanation/adr -name "ADR-*.md" | sort

# Список всех topic slugs
find docs/explanation/adr -name "ADR-*.md" | \
  sed -E 's/.*ADR-[0-9]+-([^.]+)\.md/\1/' | sort

# Статистика ADR
./scripts/verify-adr-checklist.sh --format short
```

---

## Шаг 1: Обновление docs/explanation/adr/index.md

### 1.1. Получить актуальный список ADR

```bash
# Собрать информацию обо всех ADR
for adr in docs/explanation/adr/ADR-*.md; do
  number=$(basename "$adr" | sed -E 's/ADR-([0-9]+)-.*/\1/')
  slug=$(basename "$adr" | sed -E 's/ADR-[0-9]+-([^.]+)\.md/\1/')
  title=$(grep "^# " "$adr" | head -1 | sed 's/^# //')
  status=$(grep "^## Статус решения" -A2 "$adr" | head -1 | sed 's/.*: //')
  critical=$(grep "⭐" "$adr" > /dev/null && echo "⭐" || echo "")
  progress=$(grep "^## Прогресс реализации" -A1 "$adr" | head -1 | \
    sed -E 's/.*🟢|🟡|🔴.*(\([0-9]+%\)).*/\1/' | grep -oE '[0-9]+%')

  echo "$number|$slug|$title|$status|$critical|$progress"
done | sort -t'|' -k1 -n
```

### 1.2. Обновить таблицу ADR в index.md

```markdown
<!-- Аналогичная таблица уже есть в index.md -->
| # | Topic Slug | ADR Title | Status | Critical | Progress |
|---|-------------|-----------|--------|----------|----------|
| 001 | path-based-routing | Path-based routing instead of subdomains | Accepted | ⭐ | 100% |
| 002 | k8s-provider-abstraction | K8s provider abstraction with $KUBECTL_CMD | Accepted | ⭐ | 100% |
| ...
```

**Правила обновления:**
- ✅ Сортировка по номеру ADR
- ✅ topic slug используется как первичный идентификатор
- ✅ Статус: Proposed/Accepted/Deprecated/Superseded
- ✅ Критичность: ⭐ для critical ADR
- ✅ Прогресс: % из чеклиста (verify-adr-checklist.sh)

### 1.3. Обновить статистику ADR

```markdown
## ADR Statistics

| Metric | Count |
|--------|-------|
| **Total ADRs** | 15 |
| **Critical ADRs** | 5 |
| **Proposed** | 3 |
| **Accepted** | 12 |
| **Deprecated** | 0 |
| **Superseded** | 0 |
| **Fully Implemented** | 7 |
| **Partially Implemented** | 5 |
| **Not Implemented** | 3 |
| **Average Progress** | 67.3% |

## Implementation Progress by Layer

| Layer | Progress | ADRs |
|-------|----------|------|
| Layer 0: Infrastructure | 85% | 3 |
| Layer 1: Platform | 72% | 2 |
| Layer 2: Bot/API | 65% | 4 |
| Layer 3: Business Logic | 50% | 3 |
| Layer 4: Monitoring | 80% | 2 |
| Layer 5: Documentation | 100% | 1 |

## Critical ADR Status

| Topic Slug | Status | Progress | Last Updated |
|------------|--------|----------|--------------|
| path-based-routing | Accepted | 100% | 2026-03-18 |
| k8s-provider-abstraction | Accepted | 100% | 2026-03-18 |
| storage-provider-selection | Accepted | 100% | 2026-03-15 |
| ${PLATFORM_SLUG} | Accepted | 90% | 2026-03-10 |
| documentation-generation | Accepted | 100% | 2026-03-05 |
```

---

## Шаг 2: Обновление README.md

### 2.1. Проверить, нужно ли обновить README.md

Обновить README.md только если:
- ✅ Изменилось количество ADR (добавлен/удален)
- ✅ Изменилось описание проекта
- ✅ Добавлен новый раздел документации

```bash
# Сравнить количество ADR
current_count=$(find docs/explanation/adr -name "ADR-*.md" | wc -l)
readme_count=$(grep "Total ADRs" README.md | grep -oE '[0-9]+')

if [ "$current_count" -ne "$readme_count" ]; then
  echo "README.md needs update: $readme_count → $current_count"
fi
```

### 2.2. Обновить секцию ADR в README.md

```markdown
## Architecture Decisions (ADRs)

We use ADRs to document significant architectural decisions. See [docs/explanation/adr/index.md](docs/explanation/adr/index.md) for the complete list.

**Current Status:**
- **Total ADRs:** 15
- **Critical ADRs:** 5
- **Implementation Progress:** 67.3% (average)

### Critical ADRs

- ✅ [ADR-001: Path-based routing](docs/explanation/adr/ADR-001-path-based-routing.md) - 100%
- ✅ [ADR-002: K8s provider abstraction](docs/explanation/adr/ADR-002-k8s-provider-abstraction.md) - 100%
- ✅ [ADR-003: Storage provider selection](docs/explanation/adr/ADR-003-storage-provider-selection.md) - 100%
- 🟡 [ADR-004: ${PLATFORM_SLUG}](docs/explanation/adr/ADR-004-${PLATFORM_SLUG}.md) - 90%
- ✅ [ADR-005: Documentation generation](docs/explanation/adr/ADR-005-documentation-generation.md) - 100%

See [docs/explanation/adr/index.md](docs/explanation/adr/index.md) for all ADRs.
```

---

## Шаг 3: Обновление навигации

### 3.1. Проверить все ссылки на ADR

```bash
# Найти все ссылки на ADR в документации
grep -r "docs/explanation/adr/ADR-" docs/ --include="*.md" | \
  grep -v "index.md"

# Проверить, что все ссылки ведут на существующие файлы
for link in $(grep -roh "ADR-[0-9]+-[a-z0-9-]+\.md" docs/ | sort -u); do
  if [ ! -f "docs/explanation/adr/$link" ]; then
    echo "Broken link: $link"
  fi
done
```

### 3.2. Обновить ссылки после изменения номеров

```bash
# Если ADR перенумерованы — обновить все ссылки
# Пример: ADR-007 → ADR-005 (после удаления 005, 006)
find docs/ -name "*.md" -exec sed -i 's/ADR-007/ADR-005/g' {} \;
```

### 3.3. Обновить ссылки после изменения topic slugs

```bash
# Если topic slug изменён — обновить все ссылки
OLD_SLUG="k8s-abstraction"
NEW_SLUG="k8s-provider-abstraction"
find docs/ -name "*.md" -exec sed -i "s/$OLD_SLUG/$NEW_SLUG/g" {} \;
```

---

## Шаг 4: Синхронизация документации

### 4.1. Проверить структуру документации

```bash
# Проверить, что все директории документации существуют
for dir in docs/explanation docs/how-to docs/reference docs/tutorials; do
  if [ ! -d "$dir" ]; then
    echo "Missing directory: $dir"
  fi
done
```

### 4.2. Обновить documentation tree

```markdown
<!-- Добавить/обновить в README.md или docs/README.md -->
## Documentation Structure

```
docs/
├── explanation/          # Почему и зачем (architectural decisions, concepts)
│   ├── adr/            # Architecture Decision Records
│   │   ├── index.md    # ADR index with statistics
│   │   ├── ADR-001-*.md
│   │   └── ADR-002-*.md
│   └── *.md           # Explanations of complex topics
├── how-to/             # Как сделать конкретную задачу
│   ├── setup.md
│   └── deployment.md
├── reference/          # Справка по API, CLI, config (AUTO-GENERATED)
├── tutorials/          # Обучение новым концепциям
└── official_document/  # Official documentation (READ-ONLY)
    ├── ${CODE_SERVER}/
    ├── k3s/
    └── ...
```

### 4.3. Сгенерировать reference docs (если изменилась структура)

```bash
# Reference docs только AUTO-GENERATED
make docs-update
```

---

## Шаг 5: Верификация синхронизации

### 5.1. Проверить index.md

```bash
# Проверить, что все ADR есть в index.md
for adr_file in docs/explanation/adr/ADR-*.md; do
  slug=$(basename "$adr_file" | sed -E 's/ADR-[0-9]+-([^.]+)\.md/\1/')
  if ! grep -q "$slug" docs/explanation/adr/index.md; then
    echo "ADR missing from index.md: $slug"
  fi
done

# Проверить, что все ADR в index.md существуют
for slug in $(grep -oE 'ADR-[0-9]+-[a-z0-9-]+\.md' docs/explanation/adr/index.md); do
  if [ ! -f "docs/explanation/adr/$slug" ]; then
    echo "ADR in index.md but not found: $slug"
  fi
done
```

### 5.2. Проверить README.md

```bash
# Проверить количество ADR
current_count=$(find docs/explanation/adr -name "ADR-*.md" | wc -l)
readme_count=$(grep "Total ADRs" README.md | grep -oE '[0-9]+')

if [ "$current_count" -ne "$readme_count" ]; then
  echo "README.md count mismatch: $readme_count vs $current_count"
fi

# Проверить ссылки на index.md
if ! grep -q "docs/explanation/adr/index.md" README.md; then
  echo "README.md missing link to ADR index"
fi
```

### 5.3. Проверить все ссылки

```bash
# Проверить, что все ссылки на ADR корректны
./scripts/verify-adr-links.sh

# Ожидаемый результат: 0 broken links
```

### 5.4. Проверить verify-all-adr.sh

```bash
# Полная верификация ADR структуры
./scripts/verify-all-adr.sh

# Ожидаемый результат: 100% PASS
```

---

## Шаг 6: Создание отчёта обновления

### 6.1. Структура отчёта

Сохранить в: `artifacts/sync/index-update-report-{timestamp}.md`

```markdown
# Index Update Report
**Date:** 2026-03-18
**Trigger:** Feature Add (ADR-006-unified-auth-architecture.md)

## Summary

| File | Changes |
|------|---------|
| docs/explanation/adr/index.md | ✅ Updated (1 ADR added) |
| README.md | ✅ Updated (count 14 → 15) |
| Navigation links | ✅ Verified (0 broken links) |

## ADR Statistics Update

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total ADRs | 14 | 15 | +1 |
| Critical ADRs | 5 | 5 | 0 |
| Proposed | 3 | 3 | 0 |
| Accepted | 11 | 12 | +1 |
| Average Progress | 65.2% | 67.3% | +2.1% |

## New ADR Added

| # | Topic Slug | Title | Status | Critical |
|---|-------------|-------|--------|----------|
| 006 | unified-auth-architecture | Unified authentication architecture | Accepted | |

## Verification Results

- ✅ All ADRs in index.md
- ✅ All ADRs in index.md exist
- ✅ README.md count matches (15)
- ✅ No broken links (verify-adr-links.sh)
- ✅ verify-all-adr.sh: 100% PASS

## Next Steps

- [ ] Review new ADR for completeness
- [ ] Update related documentation
- [ ] Communicate changes to team
```

---

## Финальный чеклист обновления индекса

- [ ] ADR список получен (из файловой системы)
- [ ] Таблица ADR в index.md обновлена
- [ ] Статистика ADR пересчитана
- [ ] Прогресс реализации обновлён (из verify-adr-checklist.sh)
- [ ] README.md обновлён (если изменился count)
- [ ] Навигация проверена (все ссылки корректны)
- [ ] Документация проверена (структура актуальна)
- [ ] Index.md верифицирован (все ADR есть и существуют)
- [ ] README.md верифицирован (count совпадает)
- [ ] Все ссылки проверены (0 broken links)
- [ ] verify-all-adr.sh: 100% PASS
- [ ] Отчёт обновления создан

---

## Связанные промпты

| Промпт | Когда использовать |
|--------|-------------------|
| `promt-feature-add.md` | После — новый ADR добавлен |
| `promt-consolidation.md` | После — ADR объединены/удалены |
| `promt-bug-fix.md` | После — прогресс ADR изменился |
| `promt-verification.md` | После — новая статистика |
| `promt-adr-implementation-planner.md` | После — пересчёт queue |

---

## Метрики успеха обновления

| Метрика | Требование |
|---------|------------|
| index.md актуален | 100% ADR есть |
| README.md актуален | Count совпадает |
| Broken links | 0 |
| verify-all-adr.sh | 100% PASS |

---

## Anti-patterns при обновлении индекса

| Anti-pattern | Правильный подход |
|--------------|------------------|
| Обновлять index.md вручную | Использовать автоматический сбор из файлов |
| Использовать номера ADR для ссылок | Использовать topic slug |
| Забывать обновить README.md | Проверить count после каждого изменения |
| Не проверять broken links | Всегда запускать verify-adr-links.sh |
| Добавлять reference docs вручную | Использовать make docs-update (AUTO-GENERATED) |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 2.6 | 2026-03-18 | Добавлена структура отчёта обновления |
| 2.5 | 2026-03-06 | Добавлена верификация index.md и README.md |
| 2.4 | 2026-02-25 | Добавлена проверка навигации и ссылок |
| 2.3 | 2026-02-24 | Добавлена синхронизация документации |
| 2.2 | 2026-02-20 | Добавлена статистика по слоям (Layer 0–5) |
| 2.1 | 2026-02-15 | Добавлена автоматическая генерация таблицы ADR |
| 2.0 | 2026-02-10 | Полный рефакторинг, интеграция с verify-adr-checklist.sh |

---

**Prompt Version:** 2.6
**Date:** 2026-03-18
