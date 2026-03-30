---

dependencies:
- promt-verification
- promt-index-update
description: Объединение дублирующих ADR, устранение пересечений и синхронизация ссылок
layer: Meta
name: promt-consolidation
status: active
tags:
- consolidation
- dedup
- sync
- adr
type: p9i
version: '2.5'
---

# AI Agent Prompt: Консолидация изменений и синхронизация ADR

**Version:** 2.5
**Date:** 2026-03-18
**Purpose:** Объединение дублирующих ADR, устранение пересечений и синхронизация ссылок

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Meta / Consolidation |
| **Время выполнения** | 30–60 мин |
| **Домен** | ADR management — deduplication and sync |

**Пример запроса:**

> «Используя `promt-consolidation.md`, выполни консолидацию ADR:
> найди дубликаты, пересечения, устаревшие ссылки и синхронизируй систему.»

**Ожидаемый результат:**
- Консолидированный набор ADR без дубликатов
- Обновлённые связи и зависимости между ADR
- Перенумерованные ADR (при необходимости)
- Отчёт о консолидации

---

## Когда использовать

- После `promt-feature-add.md` — если новый ADR пересекается с существующими
- Periodic consolidation — ежемесячный аудит дубликатов
- После удаления/замены ADR — обновить ссылки
- После переименования topic slugs — обновить все ссылки
- Pre-ADR-002 implementation — подготовка к tiered architecture

---

## Mission Statement

Ты — AI-агент, специализирующийся на **консолидации ADR** — устранении дубликатов, пересечений и синхронизации связей.

Твоя задача:
1. **Найти дубликаты** — ADR с одинаковым или очень похожим topic slug
2. **Обнаружить пересечения** — ADR, покрывающие одну и ту же область
3. **Устранить устаревшие ссылки** — ссылки на несуществующие/удалённые ADR
4. **Синхронизировать зависимости** — обновить `## Связанные ADR` во всех ADR
5. **Перенумеровать при необходимости** — поддерживать непрерывную нумерацию

---

## Контракт синхронизации системы

Этот промпт управляется из единой точки: `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`.

Обязательные инварианты синхронизации:

5. **Автоматизация Slug-нормализации**
   - Pre-commit hook проверяет duplicate topic slugs
   - При создании нового ADR выбирать уникальный slug
   - Slug форматируется в lowercase и kebab-case
   - Предотвращает конфликты с существующими ADR
- ADR идентифицируются по topic slug (первичный ключ)
- Номера ADR нестабильны — topic slug используется для всех ссылок
- При удалении ADR обновить все ссылки
- При консолидации сохранить весь контент (verify-adr-merge.sh)
- После консолидации обновить index.md

---

## Типы консолидации

### 1. Merge (Слияние)

**Сценарий:** Два или более ADR покрывают одну и ту же область с небольшими различиями.

**Действие:** Объединить в один ADR, сохранив весь контент.

**Пример:**
```
ADR-003-payment-gateway.md + ADR-015-payment-provider.md
→ ADR-003-payment-gateway.md (обновлённый)
```

### 2. Deprecate (Устаревание)

**Сценарий:** ADR полностью заменён новым ADR или больше не актуален.

**Действие:** Пометить как Deprecated, добавить ссылку на замещающий ADR.

**Пример:**
```markdown
## Статус решения
Deprecated

## Заменён на
ADR-007-unified-payment-gateway.md

## Причина деактуализации
Унифицированный payment gateway заменяет отдельные ADR для каждого провайдера.
```

### 3. Renumber (Перенумерация)

**Сценарий:** Номера ADR стали неканоническими после удаления большого количества ADR.

**Действие:** Перенумеровать ADR, обновить все ссылки в index.md и других ADR.

**Пример:**
```
ADR-003, ADR-005, ADR-010 (после удаления 001, 002, 004, 006-009)
→ ADR-001, ADR-002, ADR-003 (перенумерованы)
```

### 4. Update References (Обновление ссылок)

**Сценарий:** topic slug изменён или ADR переименован.

**Действие:** Обновить все ссылки на этот ADR во всей системе.

**Пример:**
```
topic slug: `k8s-abstraction` → `k8s-provider-abstraction`

Найти все ссылки: grep -r "k8s-abstraction" docs/
Обновить: sed -i 's/k8s-abstraction/k8s-provider-abstraction/g' docs/**/*.md
```

---

## Шаг 0: Получить контекст консолидации

### 0.1. Определить scope

```bash
# Если scope не указан — консолидировать всё
# Если scope указан — только конкретные ADR

# Примеры scope:
# --all                    # Все ADR
# --topic payment-gateway   # Конкретный topic
# --duplicate               # Только дубликаты
# --orphan                 # Только ADR без ссылок
```

### 0.2. Получить список всех ADR

```bash
# Найти все ADR файлы
find docs/explanation/adr -name "ADR-*.md" | sort

# Получить все topic slugs
find docs/explanation/adr -name "ADR-*.md" | \
  sed -E 's/.*ADR-[0-9]+-([^.]+)\.md/\1/' | sort -u
```

---

## Шаг 1: Поиск дубликатов

### 1.1. Поиск по topic slug

```bash
# Найти ADR с одинаковыми topic slugs
for slug in $(find docs/explanation/adr -name "ADR-*.md" | \
  sed -E 's/.*ADR-[0-9]+-([^.]+)\.md/\1/' | sort | uniq -d); do
  echo "Duplicate topic slug: $slug"
  find docs/explanation/adr -name "ADR-*-${slug}*.md"
done
```

### 1.2. Поиск по содержанию

Использовать скрипт для анализа содержимого:

```bash
# Запустить поиск дубликатов по содержанию
./scripts/find-duplicate-adr.sh
```

Скрипт проверяет:
- Одинаковые ключевые слова в `## Контекст`
- Одинаковые `## Решение`
- Пересечение > 80% в содержании

### 1.3. Анализ найденных дубликатов

Для каждой пары дубликатов определить:
- **Процент пересечения** (по содержанию)
- **Какой ADR более полный/актуальный**
- **Какой ADR был создан позже**
- **Есть ли уникальный контент в каждом ADR**

---

## Шаг 2: Обнаружение пересечений

### 2.1. Найти ADR с пересекающимися областями

```bash
# Проверить `## Связанные ADR` в каждом ADR
for adr in docs/explanation/adr/ADR-*.md; do
  topic=$(basename "$adr" | sed -E 's/ADR-[0-9]+-([^.]+)\.md/\1/')
  echo "Checking: $topic"
  grep -A10 "## Связанные ADR" "$adr"
done
```

### 2.2. Карта пересечений

Создать матрицу пересечений ADR:

| Topic Slug | Пересекается с | Тип пересечения |
|------------|----------------|----------------|
| payment-gateway | payment-provider | Duplicate (95%) |
| k8s-abstraction | k8s-provider-abstraction | Rename (100%) |
| auth-jwt | unified-auth | Partial overlap (60%) |

### 2.3. Классифицировать пересечения

| Тип | Процент пересечения | Действие |
|-----|---------------------|----------|
| **Full duplicate** | 90–100% | Merge |
| **Partial overlap** | 50–89% | Merge или Update References |
| **Minimal overlap** | 10–49% | Update References |
| **No overlap** | 0–9% | Ничего не делать |

---

## Шаг 3: Устранение устаревших ссылок

### 3.1. Найти ссылки на несуществующие ADR

```bash
# Получить все существующие ADR
existing_slugs=$(find docs/explanation/adr -name "ADR-*.md" | \
  sed -E 's/.*ADR-[0-9]+-([^.]+)\.md/\1/' | sort)

# Проверить ссылки в каждом ADR
for adr in docs/explanation/adr/ADR-*.md; do
  for link in $(grep -oE '\[ADR-[0-9]+-[a-z0-9-]+\]' "$adr" | \
    sed -E 's/\[ADR-[0-9]+-([a-z0-9-]+)\]/\1/'); do
    if ! echo "$existing_slugs" | grep -q "^$link$"; then
      echo "Broken link in $adr: $link"
    fi
  done
done
```

### 3.2. Найти orphan ADR (без ссылок)

```bash
# ADR, на которые не ссылается ни один другой ADR
for adr in docs/explanation/adr/ADR-*.md; do
  slug=$(basename "$adr" | sed -E 's/ADR-[0-9]+-([^.]+)\.md/\1/')
  if ! grep -r "ADR-\[0-9\]+-${slug}" docs/explanation/adr/ | \
    grep -v "$adr" > /dev/null; then
    echo "Orphan ADR: $slug"
  fi
done
```

---

## Шаг 4: Выполнение консолидации

### 4.1. Merge дубликатов

```bash
# Проверить, что контент не потерян
./scripts/verify-adr-merge.sh --source ADR-003 --target ADR-015

# Если verify успешен — выполнить merge
./scripts/merge-adr.sh --source ADR-003 --target ADR-015
```

**Шаги merge:**
1. Сохранить полный контент source ADR
2. Объединить `## Контекст` (unique content)
3. Объединить `## Решение` (merge strategies)
4. Объединить `## Чеклист` (unique items)
5. Обновить `## Связанные ADR` (merge references)
6. Удалить source ADR
7. Обновить все ссылки на source → target

### 4.2. Deprecate устаревших ADR

```markdown
# Обновить статус ADR

## Статус решения
Deprecated

## Заменён на
ADR-NNN-{new-topic-slug}.md

## Причина деактуализации
[Причина, по которой ADR устарел]

## Дата деактуализации
2026-03-18

## Примечание
См. [ADR-NNN-{new-topic-slug}.md](ADR-NNN-{new-topic-slug}.md) для актуальной информации.
```

### 4.3. Renumber ADR

```bash
# Перенумеровать ADR (автоматический скрипт)
./scripts/renumber-adrs.sh

# Ручной процесс:
# 1. Получить список ADR для перенумерации
# 2. Переименовать файлы (ADR-005 → ADR-002, и т.д.)
# 3. Обновить все ссылки в index.md
# 4. Обновить все ссылки в других ADR
```

### 4.4. Update References

```bash
# Обновить все ссылки на topic slug
OLD_SLUG="k8s-abstraction"
NEW_SLUG="k8s-provider-abstraction"

# Найти все файлы с ссылками
grep -r "$OLD_SLUG" docs/

# Обновить ссылки
find docs/ -name "*.md" -exec sed -i "s/$OLD_SLUG/$NEW_SLUG/g" {} \;
```

---

## Шаг 5: Верификация консолидации

### 5.1. Проверить отсутствие дубликатов

```bash
# Запустить проверку дубликатов
./scripts/find-duplicate-adr.sh

# Ожидаемый результат: 0 дубликатов
```

### 5.2. Проверить целостность ссылок

```bash
# Проверить, что все ссылки существуют
./scripts/verify-adr-links.sh

# Ожидаемый результат: 0 broken links
```

### 5.3. Проверить сохранение контента

```bash
# Если был merge — проверить, что контент не потерян
./scripts/verify-adr-merge.sh --source ADR-003 --target ADR-015

# Ожидаемый результат: все уникальные секции сохранены
```

### 5.4. Запустить полную верификацию

```bash
# Полная верификация ADR
./scripts/verify-all-adr.sh

# Ожидаемый результат: 100% PASS
```

---

## Шаг 6: Обновление индекса

### 6.1. Запустить promt-index-update.md

```bash
# Обновить index.md после консолидации
cat docs/ai-agent-prompts/promt-index-update.md
# Контекст: После консолидации ADR (merge/deprecate/renumber/update-refs)
# Действие: Обновить index.md с актуальным списком ADR
```

### 6.2. Проверить синхронизацию

```bash
# Проверить, что index.md синхронизирован с файлами ADR
./scripts/verify-index-sync.sh

# Ожидаемый результат: 0 расхождений
```

---

## Шаг 7: Создание отчёта консолидации

### 7.1. Структура отчёта

Сохранить в: `artifacts/consolidation/consolidation-report-{timestamp}.md`

```markdown
# ADR Consolidation Report
**Date:** 2026-03-18
**Scope:** All ADRs

## Summary

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total ADRs | 20 | 15 | -5 |
| Critical ADRs | 5 | 5 | 0 |
| Duplicates | 3 | 0 | -3 |
| Broken links | 7 | 0 | -7 |
| Orphan ADRs | 2 | 0 | -2 |

## Merged ADRs (3)

| Source | Target | Reason |
|--------|--------|--------|
| ADR-015-payment-provider | ADR-003-payment-gateway | 95% overlap |
| ADR-018-payment-api | ADR-003-payment-gateway | 92% overlap |
| ADR-012-payment-hooks | ADR-003-payment-gateway | 88% overlap |

## Deprecated ADRs (2)

| ADR | Replacement | Reason |
|-----|-------------|--------|
| ADR-007-auth-jwt | ADR-008-unified-auth | Partial overlap, unified approach |
| ADR-016-auth-oauth | ADR-008-unified-auth | Partial overlap, unified approach |

## Renumbered ADRs (0)

No ADRs required renumbering.

## Updated References (7)

| Topic Slug | Old Reference | New Reference |
|------------|----------------|----------------|
| payment-gateway | ADR-003 | ADR-003 |
| unified-auth | ADR-008 | ADR-007 |

## Verification Results

- ✅ No duplicates found
- ✅ No broken links
- ✅ All content preserved (verify-adr-merge.sh)
- ✅ verify-all-adr.sh: 100% PASS
- ✅ index.md synchronized

## Next Steps

- [ ] Review merged ADRs for consistency
- [ ] Update documentation if needed
- [ ] Communicate changes to team
- [ ] Schedule next consolidation (1 month)
```

---

## Финальный чеклист консолидации

- [ ] Дубликаты найдены (по topic slug и содержанию)
- [ ] Пересечения классифицированы (full/partial/minimal/no overlap)
- [ ] Устаревшие ссылки найдены
- [ ] Orphan ADRs найдены
- [ ] Merge выполнен (verify-adr-merge.sh successful)
- [ ] Deprecate выполнен (status updated, replacement link added)
- [ ] Renumber выполнен (если необходимо)
- [ ] References обновлены (все ссылки актуальны)
- [ ] Верификация прошла (find-duplicate-adr.sh: 0)
- [ ] Верификация ссылок прошла (verify-adr-links.sh: 0)
- [ ] Контент сохранён (verify-adr-merge.sh: successful)
- [ ] verify-all-adr.sh: 100% PASS
- [ ] index.md обновлён (promt-index-update.md)
- [ ] Отчёт консолидации создан

---

## Связанные промпты

| Промпт | Когда использовать |
|--------|-------------------|
| `promt-feature-add.md` | После — если новый ADR пересекается |
| `promt-verification.md` | После — верификация консолидации |
| `promt-index-update.md` | После консолидации — обновить index.md |
| `promt-adr-implementation-planner.md` | Для пересчёта queue после консолидации |

---

## Метрики успеха консолидации

| Метрика | Требование |
|---------|------------|
| Дубликаты | 0 |
| Broken links | 0 |
| Orphan ADRs | 0 |
| verify-all-adr.sh | 100% PASS |
| Контент сохранён | 100% (verify-adr-merge.sh) |
| index.md синхронизирован | Да |

---

## Anti-patterns при консолидации

| Anti-pattern | Правильный подход |
|--------------|------------------|
| Удалить ADR без проверки ссылок | Найти и обновить все ссылки |
| Merge без verify-adr-merge.sh | Всегда проверять сохранение контента |
| Renumber без обновления ссылок | Обновить все ссылки на новые номера |
| Обновить index.md вручную | Использовать promt-index-update.md |
| Deprecate без ссылки на replacement | Добавить замену и причину |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 2.5 | 2026-03-18 | Добавлена структура отчёта консолидации |
| 2.4 | 2026-03-06 | Добавлена классификация пересечений |
| 2.3 | 2026-02-25 | Добавлена поддержка renumber и update-references |
| 2.2 | 2026-02-24 | Интеграция с verify-adr-merge.sh |
| 2.1 | 2026-02-20 | Добавлен поиск orphan ADRs |
| 2.0 | 2026-02-15 | Полный рефакторинг, добавлена поддержка всех типов консолидации |

---

**Prompt Version:** 2.5
**Date:** 2026-03-18
