---

dependencies:
- promt-verification
- promt-index-update
description: Миграция существующих ADR на новые форматы шаблонов с dual-status и чеклистами
layer: Meta
name: promt-adr-template-migration
status: active
tags:
- adr
- template
- migration
- standards
type: p9i
version: '1.4'
---

# AI Agent Prompt: Миграция на новые форматы ADR template

**Version:** 1.4
**Date:** 2026-03-18
**Purpose:** Миграция существующих ADR на новые форматы шаблонов с dual-status и чеклистами

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Meta / Migration |
| **Время выполнения** | 20–40 мин |
| **Домен** | Documentation — ADR template migration |

**Пример запроса:**

> «Используя `promt-adr-template-migration.md`, выполни миграцию ADR
> на новый формат v2: добавь dual-status, чеклисты, topic slug.»

**Ожидаемый результат:**
- Все ADR мигрированы на новый формат шаблона
- Dual-status добавлен (## Статус решения + ## Прогресс реализации)
- Чеклисты реализации добавлены
- Topic slugs добавлены в имена файлов

---

## Когда использовать

- После обновления ADR template (ADR-template.md)
- Periodic migration — когда изменился стандарт ADR
- После ADR-002 implementation — tiered prompt architecture migration
- Перед consolidating ADRs — единый формат для merge

---

## Mission Statement

Ты — AI-агент, специализирующийся на **миграции ADR** — обновлении существующих ADR на новые стандарты шаблонов.

Твоя задача:
1. **Прочитать новый ADR template** — понять требуемый формат
2. **Прочитать существующие ADR** — определить несоответствия
3. **Мигрировать ADR** — добавить недостающие секции
4. **Переименовать файлы** — добавить topic slug (если отсутствует)
5. **Верифицировать миграцию** — проверка соответствия шаблону

---

## Контракт синхронизации системы

Обязательные инварианты:
- Все ADR соответствуют текущему шаблону (ADR-template.md)
- Dual-status присутствует во всех ADR (## Статус решения + ## Прогресс реализации)
- Чеклисты присутствуют во всех Accepted ADR
- Topic slug присутствует в имени файла (ADR-NNN-{slug}.md)
- Ссылки на ADR используют topic slug, не номер

---

## Шаг 0: Получить контекст миграции

### 0.1. Прочитать новый ADR template

```bash
# Прочитать новый шаблон
cat docs/explanation/adr/ADR-template.md
```

**Новый формат v2 включает:**
```markdown
# ADR-NNN: {Title}

## Статус решения
Proposed / Accepted / Deprecated / Superseded

## Прогресс реализации
🔴 Не начато / 🟡 Частично (~N%) / 🟢 Полностью

**Дата:** YYYY-MM-DD
**Автор:** Author Name
**Теги:** #{technology} #{area}

## Контекст
[Why is this needed? What problem does it solve?]

## Решение
[Specific decision with code/commands]

## Последствия
- Положительные: [list]
- Отрицательные: [risks]

## Рассмотренные варианты
[Alternatives considered]

## Реализация
[Key files, commands, configurations]

## Тестирование
[How to verify]

## Чеклист реализации
[4 categories: Обязательные / Условные / Специфичные / Интеграция]

## Связанные ADR
[Links to related topic slugs]

## Ссылки
- Context7: [what was researched]
- Official docs: `docs/official_document/{technology}/`
- Issue/PR: [link]
```

### 0.2. Определить scope миграции

```bash
# Найти все ADR файлы
find docs/explanation/adr -name "ADR-*.md" | sort

# Найти ADR без topic slug в имени файла
for f in docs/explanation/adr/ADR-*.md; do
  if ! [[ "$f" =~ ADR-[0-9]+-[a-z0-9-]+ ]]; then
    echo "Missing topic slug: $f"
  fi
done
```

---

## Шаг 1: Анализ существующих ADR

### 1.1. Проверить соответствие шаблону

```bash
# Проверить наличие обязательных секций
for adr in docs/explanation/adr/ADR-*.md; do
  echo "Checking: $adr"
  grep -q "## Статус решения" "$adr" || echo "  ❌ Missing: ## Статус решения"
  grep -q "## Прогресс реализации" "$adr" || echo "  ❌ Missing: ## Прогресс реализации"
  grep -q "## Чеклист реализации" "$adr" || echo "  ❌ Missing: ## Чеклист реализации"
  grep -q "## Связанные ADR" "$adr" || echo "  ❌ Missing: ## Связанные ADR"
done
```

### 1.2. Создать отчёт анализа

```markdown
# ADR Migration Analysis Report
**Date:** 2026-03-18

## Summary

| Metric | Count |
|--------|-------|
| **Total ADRs** | 10 |
| **Missing Dual-Status** | 3 |
| **Missing Checklists** | 4 |
| **Missing Topic Slug** | 2 |
| **Requires Migration** | 5 |

## Issues Found

### Missing Dual-Status

| ADR File | Missing |
|-----------|---------|
| ADR-006-unified-auth.md | ## Прогресс реализации |
| ADR-007-e2e-testing.md | ## Прогресс реализации |
| ADR-008-metrics.md | ## Прогресс реализации |

### Missing Checklists

| ADR File | Missing |
|-----------|---------|
| ADR-006-unified-auth.md | ## Чеклист реализации |
| ADR-007-e2e-testing.md | ## Чеклист реализации |
| ADR-008-metrics.md | ## Чеклист реализации |
| ADR-009-gitops.md | ## Чеклист реализации |

### Missing Topic Slug

| ADR File | Current Name | Suggested Name |
|-----------|--------------|-----------------|
| ADR-006.md | ADR-006.md | ADR-006-unified-auth-architecture.md |
| ADR-010.md | ADR-010.md | ADR-010-helm-chart-structure-optimization.md |
```

---

## Шаг 2: Миграция ADR на новый формат

### 2.1. Добавить Dual-Status

Для каждого ADR добавить:

```markdown
## Статус решения
Accepted

## Прогресс реализации
🟡 Частично (~N%)
```

**Примечание:** Если ADR в статусе Proposed, прогресс = 🔴 Не начато (0%).
Если ADR полностью реализован, прогресс = 🟢 Полностью (100%).

### 2.2. Добавить Чеклист реализации

Для Accepted ADR добавить чеклист с 4 категориями:

```markdown
## Чеклист реализации

### Обязательные
- [ ] Пункт 1 из ADR
- [ ] Пункт 2 из ADR
- [ ] Пункт 3 из ADR

### Условные
- [ ] (если применимо) Пункт 1
- [ ] (если применимо) Пункт 2

### Специфичные для [domain]
- [ ] Специфичный пункт 1
- [ ] Специфичный пункт 2

### Интеграция
- [ ] Интеграционный тест 1
- [ ] Интеграционный тест 2
- [ ] Обновление документации
```

**Правила заполнения:**
- ✅ Пункты берутся из секции `## Решение` ADR
- ✅ Минимум 3 обязательных пункта
- ✅ Специфичные пункты зависят от domain (infrastructure/platform/app/etc.)
- ✅ Интеграционные пункты — тесты с другими сервисами

### 2.3. Добавить Связанные ADR

```markdown
## Связанные ADR
- `path-based-routing` — если ADR затрагивает routing
- `k8s-provider-abstraction` — если ADR затрагивает K8s
- `telegram-bot-saas-platform` — если ADR затрагивает bot/platform
```

**Правила:**
- ✅ Использовать topic slug, не номер ADR
- ✅ Только прямые зависимости
- ✅ Минимум 1 связанный ADR (если применимо)

---

## Шаг 3: Переименование файлов с topic slug

### 3.1. Определить topic slug для каждого ADR

Правило: topic slug = kebab-case из заголовка ADR

```bash
# Примеры:
# ADR-NNN: Path-based routing instead of subdomains
# → ADR-001-path-based-routing.md

# ADR-NNN: K8s provider abstraction with $KUBECTL_CMD
# → ADR-002-k8s-provider-abstraction.md

# ADR-NNN: Telegram bot SaaS platform architecture
# → ADR-004-telegram-bot-saas-platform.md
```

### 3.2. Переименовать файлы

```bash
# Переименовать ADR без topic slug
mv docs/explanation/adr/ADR-006.md docs/explanation/adr/ADR-006-unified-auth-architecture.md

# Переименовать ADR с неверным topic slug
mv docs/explanation/adr/ADR-006-unified-auth.md \
   docs/explanation/adr/ADR-006-unified-auth-architecture.md
```

### 3.3. Обновить ссылки после переименования

```bash
# Найти все ссылки на старые номера
grep -r "ADR-006\]" docs/explanation/adr/

# Заменить ссылки на topic slug
find docs/ -name "*.md" -exec sed -i 's/ADR-006\]/ADR-006-unified-auth-architecture.md]/g' {} \;
```

---

## Шаг 4: Верификация миграции

### 4.1. Проверить соответствие шаблону

```bash
# Запустить верификацию структуры ADR
./scripts/verify-all-adr.sh

# Ожидаемый результат: 100% PASS
```

### 4.2. Проверить topic slug consistency

```bash
# Проверить, что все ADR имеют topic slug
for f in docs/explanation/adr/ADR-*.md; do
  if ! [[ "$f" =~ ADR-[0-9]+-[a-z0-9-]+ ]]; then
    echo "❌ Missing topic slug: $f"
  else
    echo "✅ Valid: $f"
  fi
done
```

### 4.3. Проверить dual-status

```bash
# Проверить, что все ADR имеют dual-status
for adr in docs/explanation/adr/ADR-*.md; do
  if ! grep -q "## Статус решения" "$adr"; then
    echo "❌ Missing status: $adr"
  fi
  if ! grep -q "## Прогресс реализации" "$adr"; then
    echo "❌ Missing progress: $adr"
  fi
done
```

### 4.4. Проверить чеклисты

```bash
# Проверить, что все Accepted ADR имеют чеклисты
for adr in docs/explanation/adr/ADR-*.md; do
  status=$(grep "^## Статус решения" -A2 "$adr" | head -1 | sed 's/.*: //')
  if [ "$status" = "Accepted" ]; then
    if ! grep -q "## Чеклист реализации" "$adr"; then
      echo "❌ Missing checklist (Accepted ADR): $adr"
    fi
  fi
done
```

---

## Шаг 5: Обновление ссылок

### 5.1. Заменить ссылки на номера → topic slug

```bash
# Найти все ссылки на ADR по номеру
grep -rE "ADR-[0-9]+\]" docs/

# Заменить на topic slug
# Пример: [ADR-006] → [ADR-006-unified-auth-architecture.md]
find docs/ -name "*.md" -exec sed -i \
  's/\[ADR-006\]/[ADR-006-unified-auth-architecture.md]/g' {} \;
```

### 5.2. Проверить все ссылки

```bash
# Проверить, что все ссылки ведут на существующие файлы
./scripts/verify-adr-links.sh

# Ожидаемый результат: 0 broken links
```

---

## Шаг 6: Создание отчёта миграции

### 6.1. Структура отчёта

Сохранить в: `artifacts/migration/adr-migration-report-{timestamp}.md`

```markdown
# ADR Template Migration Report
**Date:** 2026-03-18
**Scope:** All ADRs (10 total)

## Summary

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **ADR Files** | 10 | 10 | 0 |
| **Dual-Status ADRs** | 7 | 10 | +3 |
| **Checklists Present** | 6 | 10 | +4 |
| **Topic Slug Files** | 8 | 10 | +2 |
| **Verification** | N/A | 100% PASS | ✅ |

## Migrations Performed

### Dual-Status Added (3)

| ADR | Added Sections |
|-----|---------------|
| ADR-006-unified-auth-architecture.md | ## Прогресс реализации |
| ADR-007-e2e-testing-new-features.md | ## Прогресс реализации |
| ADR-008-metrics-alerting-strategy.md | ## Прогресс реализации |

### Checklists Added (4)

| ADR | Checklist Items |
|-----|-----------------|
| ADR-006-unified-auth-architecture.md | 12 items (4 categories) |
| ADR-007-e2e-testing-new-features.md | 15 items (4 categories) |
| ADR-008-metrics-alerting-strategy.md | 10 items (4 categories) |
| ADR-009-gitops-validation.md | 8 items (4 categories) |

### Topic Slugs Added (2)

| Old Name | New Name |
|-----------|-----------|
| ADR-006.md | ADR-006-unified-auth-architecture.md |
| ADR-010.md | ADR-010-helm-chart-structure-optimization.md |

### Links Updated (15)

| Old Reference | New Reference |
|--------------|---------------|
| [ADR-006] | [ADR-006-unified-auth-architecture.md] |
| [ADR-010] | [ADR-010-helm-chart-structure-optimization.md] |

## Verification Results

- ✅ verify-all-adr.sh: 100% PASS
- ✅ All topic slugs valid
- ✅ All dual-status present
- ✅ All checklists present (for Accepted ADRs)
- ✅ No broken links

## Next Steps

- [ ] Review migrated checklists for completeness
- [ ] Update progress percentages based on checklists
- [ ] Run promt-index-update.md to sync index.md
- [ ] Communicate changes to team
```

---

## Финальный чеклист миграции

- [ ] Новый ADR template прочитан
- [ ] Все существующие ADR проанализированы
- [ ] Отчёт анализа создан
- [ ] Dual-Status добавлен всем ADR
- [ ] Чеклисты добавлены всем Accepted ADR
- [ ] Связанные ADR добавлены
- [ ] Файлы переименованы с topic slug
- [ ] Ссылки обновлены (номера → topic slug)
- [ ] verify-all-adr.sh: 100% PASS
- [ ] Topic slug consistency проверена
- [ ] Dual-status проверена
- [ ] Чеклисты проверены
- [ ] verify-adr-links.sh: 0 broken links
- [ ] Отчёт миграции создан

---

## Связанные промпты

| Промпт | Когда использовать |
|--------|-------------------|
| `promt-feature-add.md` | После — новый ADR соответствует шаблону |
| `promt-consolidation.md` | После — все ADR в едином формате для merge |
| `promt-verification.md` | После — верификация структуры ADR |
| `promt-index-update.md` | После — обновить index.md с переименованными ADR |

---

## Метрики успеха миграции

| Метрика | Требование |
|---------|------------|
| verify-all-adr.sh | 100% PASS |
| Dual-Status | 100% ADR |
| Чеклисты | 100% Accepted ADR |
| Topic Slug | 100% файлов |
| Broken Links | 0 |

---

## Anti-patterns при миграции

| Anti-pattern | Правильный подход |
|--------------|------------------|
| Мигрировать вручную без проверки | Использовать verify-all-adr.sh после каждого ADR |
| Забывать обновить ссылки | Всегда обновлять ссылки после переименования |
| Добавлять пустые чеклисты | Заполнять чеклисты на основе `## Решение` |
| Игнорировать topic slug | Всегда использовать kebab-case из заголовка |
| Мигрировать без бэкапа | Сохранять backup перед изменениями |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.4 | 2026-03-18 | Добавлена структура отчёта миграции |
| 1.3 | 2026-03-06 | Добавлена интеграция с verify-adr-links.sh |
| 1.2 | 2026-02-25 | Добавлена проверка чеклистов для Accepted ADR |
| 1.1 | 2026-02-20 | Добавлена автоматическая генерация topic slug |
| 1.0 | 2026-02-10 | Первая версия: basic template migration |

---

**Prompt Version:** 1.4
**Date:** 2026-03-18
