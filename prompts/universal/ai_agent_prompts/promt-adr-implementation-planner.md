---

dependencies:
- promt-verification
- promt-index-update
description: Планирование очереди внедрения ADR, трекинг прогресса, Critical Path
  анализ
layer: Meta
name: promt-adr-implementation-planner
status: active
tags:
- adr
- planning
- implementation
- tracking
type: p9i
version: '2.3'
---

# AI Agent Prompt: Планирование и трекинг ADR implementation

**Version:** 2.3
**Date:** 2026-03-18
**Purpose:** Планирование очереди внедрения ADR, трекинг прогресса, Critical Path анализ

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Meta / Planning |
| **Время выполнения** | 20–30 мин |
| **Домен** | Project management — ADR implementation |

**Пример запроса:**

> «Используя `promt-adr-implementation-planner.md`, спланируй очередь внедрения ADR:
> рассчитай Critical Path, приоритизируй по слоям, обнови прогресс чеклистов.»

**Ожидаемый результат:**
- Обновлённая очередь внедрения ADR по Critical Path
- Приоритизация ADR по слоям и зависимостям
- Прогресс реализации из чеклистов
- Рекомендации по sequencing

---

## Когда использовать

- После добавления новых ADR — добавить в очередь внедрения
- После изменения прогресса ADR — пересчитать очередь
- После консолидации ADR — обновить зависимости
- Periodic planning — еженедельный review очереди
- Pre-implementation — определить sequence для новых фич

---

## Mission Statement

Ты — AI-агент, специализирующийся на **планировании внедрения ADR** — управлении очереди, зависимостях и sequencing.

Твоя задача:
1. **Рассчитать Critical Path** — минимальный путь к полной реализации
2. **Приоритизировать по слоям** — Layer 0 → Layer 5
3. **Построить зависимости** — DAG (Directed Acyclic Graph) ADR
4. **Трекировать прогресс** — реальные проценты из чеклистов
5. **Генерировать рекомендации** — оптимальный sequence для команд

---

## Контракт синхронизации системы

Обязательные инварианты:
- Очередь внедрения всегда отражает текущее состояние ADR
- Прогресс рассчитывается из чеклистов (verify-adr-checklist.sh)
- Зависимости ADR всегда корректны (no cycles)
- Critical Path пересчитывается при каждом изменении
- Layer priority: 0 → 1 → 2 → 3 → 4 → 5

---

## Шаг 1: Чтение ADR и зависимостей

### 1.1. Получить список всех ADR

```bash
# Найти все ADR файлы
find docs/explanation/adr -name "ADR-*.md" | sort

# Получить topic slugs и статусы
for adr in docs/explanation/adr/ADR-*.md; do
  slug=$(basename "$adr" | sed -E 's/ADR-[0-9]+-([^.]+)\.md/\1/')
  status=$(grep "^## Статус решения" -A2 "$adr" | head -1 | sed 's/.*: //')
  critical=$(grep "⭐" "$adr" > /dev/null && echo "⭐" || echo "")
  progress=$(./scripts/verify-adr-checklist.sh --topic "$slug" --format short | \
    grep -oE '[0-9]+%' || echo "0%")
  echo "$slug|$status|$critical|$progress"
done | sort -t'|' -k4 -rn
```

### 1.2. Построить граф зависимостей

```bash
# Собрать зависимости из `## Связанные ADR`
for adr in docs/explanation/adr/ADR-*.md; do
  slug=$(basename "$adr" | sed -E 's/ADR-[0-9]+-([^.]+)\.md/\1/')
  deps=$(grep -A10 "## Связанные ADR" "$adr" | grep -oE '[a-z0-9-]+' | tr '\n' ',')
  echo "$slug|$deps"
done
```

**Пример графа зависимостей:**
```
path-based-routing → (no dependencies)
k8s-provider-abstraction → (no dependencies)
storage-provider-selection → (no dependencies)
telegram-bot-saas-platform → (no dependencies)
documentation-generation → (no dependencies)
unified-auth-architecture → telegram-bot-saas-platform
e2e-testing-new-features → telegram-bot-saas-platform, unified-auth-architecture
helm-chart-structure-optimization → k8s-provider-abstraction
gitops-validation → k8s-provider-abstraction
metrics-alerting-strategy → telegram-bot-saas-platform
```

---

## Шаг 2: Классификация ADR по слоям

### 2.1. Определить слой для каждого ADR

```markdown
## Layer Mapping

| Layer | Описание | ADRs |
|-------|----------|-------|
| **Layer 0** | Infrastructure (K8s, Helm, Storage, Networking) | path-based-routing, k8s-provider-abstraction, storage-provider-selection |
| **Layer 1** | Platform (DB, Auth, Caching) | telegram-bot-saas-platform, unified-auth-architecture |
| **Layer 2** | Bot/API (Telegram, FastAPI) | e2e-testing-new-features |
| **Layer 3** | Business Logic (Payments, SaaS) | (future) |
| **Layer 4** | Monitoring/Operations | metrics-alerting-strategy, gitops-validation |
| **Layer 5** | Documentation | documentation-generation, helm-chart-structure-optimization |
```

### 2.2. Приоритизация по слоям

**Правило sequencing:** Layer 0 → Layer 1 → Layer 2 → Layer 3 → Layer 4 → Layer 5

**Обоснование:**
1. Layer 0 обеспечивает базовую инфраструктуру для всех слоёв
2. Layer 1 строится поверх Layer 0 (платформенные сервисы)
3. Layer 2 использует Layer 0 и Layer 1 (application logic)
4. Layer 3 реализует бизнес-логику поверх application
5. Layer 4 мониторит все предыдущие слои
6. Layer 5 документирует все предыдущие слои

---

## Шаг 3: Расчёт Critical Path

### 3.1. Определить зависимости по слоям

```python
# Pseudocode for Critical Path calculation
def calculate_critical_path(adr_graph, layer_mapping):
    """
    Calculate Critical Path through ADR DAG.

    Args:
        adr_graph: {topic_slug: [dependencies]}
        layer_mapping: {topic_slug: layer}

    Returns:
        List of topic_slugs in optimal order
    """
    # 1. Group ADRs by layer
    layers = {}
    for slug, deps in adr_graph.items():
        layer = layer_mapping[slug]
        layers.setdefault(layer, []).append(slug)

    # 2. Sort each layer by dependencies and priority
    sorted_layers = {}
    for layer in range(6):
        adrs_in_layer = layers.get(layer, [])
        # Sort by number of dependencies (fewer first)
        sorted_adrs = sorted(
            adrs_in_layer,
            key=lambda x: len(adr_graph[x])
        )
        sorted_layers[layer] = sorted_adrs

    # 3. Build Critical Path (layers 0–5)
    critical_path = []
    for layer in range(6):
        critical_path.extend(sorted_layers[layer])

    return critical_path
```

### 3.2. Critical Path Output

```markdown
## Critical Path (Optimal Implementation Order)

| Order | Layer | ADR | Dependencies | Progress | Estimated Days |
|-------|-------|-----|-------------|-----------|-----------------|
| 1 | 0 | path-based-routing | None | 100% | ✅ Complete |
| 2 | 0 | k8s-provider-abstraction | None | 100% | ✅ Complete |
| 3 | 0 | storage-provider-selection | None | 100% | ✅ Complete |
| 4 | 1 | telegram-bot-saas-platform | None | 90% | 🟡 In Progress (2 days) |
| 5 | 5 | documentation-generation | None | 100% | ✅ Complete |
| 6 | 4 | gitops-validation | k8s-provider-abstraction | 20% | 🔴 Planned (5 days) |
| 7 | 1 | unified-auth-architecture | telegram-bot-saas-platform | 0% | 🔴 Planned (7 days) |
| 8 | 4 | metrics-alerting-strategy | telegram-bot-saas-platform | 0% | 🔴 Planned (5 days) |
| 9 | 2 | e2e-testing-new-features | telegram-bot-saas-platform, unified-auth-architecture | 60% | 🟡 In Progress (3 days) |
| 10 | 5 | helm-chart-structure-optimization | k8s-provider-abstraction | 0% | 🔴 Planned (3 days) |

**Total Estimated Time:** 20 days (5 days for remaining ADRs)

**Parallelization Potential:**
- Layer 4 ADRs (gitops-validation, metrics-alerting-strategy) can be parallel
- Layer 2 ADRs can start after Layer 1 is 80% complete
```

---

## Шаг 4: Приоритизация по критичности

### 4.1. Critical ADRs (⭐)

```markdown
## Critical ADR Priority Queue

| Priority | ADR | Layer | Progress | Blocking | Notes |
|----------|-----|-------|-----------|----------|-------|
| **P0** | path-based-routing | 0 | 100% | None | ✅ Complete |
| **P0** | k8s-provider-abstraction | 0 | 100% | None | ✅ Complete |
| **P0** | storage-provider-selection | 0 | 100% | None | ✅ Complete |
| **P0** | telegram-bot-saas-platform | 1 | 90% | Layer 1+,2+,3+ | 🟡 2 days to complete |
| **P0** | documentation-generation | 5 | 100% | None | ✅ Complete |

**Definition:** Critical ADRs (⭐) are blocking other layers. Must be 100% before dependent ADRs start.
```

### 4.2. Non-Critical ADRs

```markdown
## Non-Critical ADR Priority Queue

| Priority | ADR | Layer | Progress | Dependencies | Notes |
|----------|-----|-------|-----------|--------------|-------|
| **P1** | unified-auth-architecture | 1 | 0% | telegram-bot-saas-platform (90%) | ⏳ Start in 2 days |
| **P2** | metrics-alerting-strategy | 4 | 0% | telegram-bot-saas-platform (90%) | ⏳ Start in 2 days |
| **P2** | gitops-validation | 4 | 20% | k8s-provider-abstraction (100%) | 🔴 In Progress (5 days) |
| **P3** | e2e-testing-new-features | 2 | 60% | telegram-bot-saas-platform (90%) | 🟡 In Progress (3 days) |
| **P4** | helm-chart-structure-optimization | 5 | 0% | k8s-provider-abstraction (100%) | 🔴 Planned (3 days) |

**Definition:** Non-critical ADRs can be sequenced flexibly within their layer.
```

---

## Шаг 5: Трекинг прогресса реализации

### 5.1. Получить прогресс из чеклистов

```bash
# Использовать verify-adr-checklist.sh
./scripts/verify-adr-checklist.sh --format short

# Вывод:
# path-based-routing: 100% (5/5 completed)
# k8s-provider-abstraction: 100% (8/8 completed)
# telegram-bot-saas-platform: 90% (27/30 completed)
# ...
```

### 5.2. Классификация по реализации

| Статус реализации | Процент | Значок | Описание |
|------------------|---------|--------|----------|
| **planned** | 0% | 🔴 Не начато | ADR принят, но ничего не реализовано |
| **partial** | 1–99% | 🟡 Частично | Реализована часть чеклиста |
| **full** | 100% | 🟢 Полностью | Все пункты чеклиста выполнены |

### 5.3. Статистика реализации

```markdown
## Implementation Statistics

| Layer | Total ADRs | Planned | Partial | Full | Average Progress |
|-------|-------------|---------|----------|-------|------------------|
| Layer 0: Infrastructure | 3 | 0 | 0 | 3 | 100% |
| Layer 1: Platform | 2 | 1 | 1 | 0 | 45% |
| Layer 2: Bot/API | 1 | 0 | 1 | 0 | 60% |
| Layer 3: Business Logic | 0 | 0 | 0 | 0 | N/A |
| Layer 4: Monitoring | 2 | 1 | 1 | 0 | 10% |
| Layer 5: Documentation | 2 | 1 | 0 | 1 | 50% |
| **Total** | **10** | **3** | **3** | **4** | **67.3%** |

**Critical ADRs:** 5/5 (100%) fully implemented
**Non-Critical ADRs:** 3/6 (50%) fully implemented
```

---

## Шаг 6: Рекомендации по sequencing

### 6.1. Оптимальный sequencing для команд

```markdown
## Sequencing Recommendations

### Team Alpha (Infrastructure)

**Focus:** Complete Layer 0 ADRs (already 100% ✅)
**Next:** Support Layer 4 ADRs (gitops-validation)

**Tasks:**
- [ ] Complete gitops-validation (5 days)
- [ ] Support metrics-alerting-strategy setup

### Team Beta (Platform)

**Focus:** Complete Layer 1 ADRs
**Sequence:**
1. Finish telegram-bot-saas-platform (2 days)
2. Start unified-auth-architecture (7 days)

**Dependencies:**
- Wait for telegram-bot-saas-platform 100% before unified-auth-architecture

### Team Gamma (Application)

**Focus:** Layer 2 and Layer 3 ADRs
**Sequence:**
1. Finish e2e-testing-new-features (3 days)
2. Plan Layer 3 ADRs (business logic)

**Dependencies:**
- Wait for unified-auth-architecture before Layer 3 ADRs

### Team Delta (Documentation)

**Focus:** Layer 5 ADRs
**Sequence:**
1. Start helm-chart-structure-optimization (3 days)
2. Update all reference docs (ongoing)

**Dependencies:**
- Can start immediately (k8s-provider-abstraction is 100%)
```

### 6.2. Оптимизация для параллелизации

```markdown
## Parallelization Opportunities

| Team | ADR | Dependencies | Can Start When |
|-------|-----|--------------|----------------|
| Alpha | gitops-validation | k8s-provider-abstraction (100%) | ✅ Now |
| Alpha | metrics-alerting-strategy | telegram-bot-saas-platform (90%) | ⏳ In 2 days |
| Beta | unified-auth-architecture | telegram-bot-saas-platform (100%) | ⏳ In 2 days |
| Gamma | e2e-testing-new-features | telegram-bot-saas-platform (90%) | 🟡 Now (can proceed with 90%) |
| Delta | helm-chart-structure-optimization | k8s-provider-abstraction (100%) | ✅ Now |

**Parallel Teams:**
- Team Alpha + Team Delta can work in parallel now
- Team Beta + Team Gamma can start in 2 days
- Total time with parallelization: ~7 days (vs 20 days sequential)
```

---

## Шаг 7: Создание отчёта планирования

### 7.1. Структура отчёта

Сохранить в: `artifacts/planning/adr-implementation-plan-{timestamp}.md`

```markdown
# ADR Implementation Plan
**Date:** 2026-03-18
**Scope:** All ADRs (10 total)

## Summary

| Metric | Value |
|--------|-------|
| **Total ADRs** | 10 |
| **Critical ADRs** | 5 (100% complete) |
| **Non-Critical ADRs** | 5 (50% complete) |
| **Average Progress** | 67.3% |
| **Estimated Time Remaining** | 7 days (parallel) / 20 days (sequential) |

## Critical Path

See [Critical Path section](#critical-path-optimal-implementation-order)

## Team Assignments

| Team | ADRs | Estimated Days |
|-------|-------|-----------------|
| Alpha (Infrastructure) | gitops-validation | 5 |
| Beta (Platform) | telegram-bot-saas-platform, unified-auth-architecture | 9 |
| Gamma (Application) | e2e-testing-new-features | 3 |
| Delta (Documentation) | helm-chart-structure-optimization | 3 |

## Recommendations

1. **Parallelize:** Start Alpha + Delta now, Beta + Gamma in 2 days
2. **Dependencies:** Ensure telegram-bot-saas-platform 100% before unified-auth-architecture
3. **Review:** Consider adding Layer 3 ADRs (business logic) after Layer 2 is complete

## Next Steps

- [ ] Assign gitops-validation to Team Alpha
- [ ] Assign helm-chart-structure-optimization to Team Delta
- [ ] Wait for telegram-bot-saas-platform 100% before Beta/Gamma start
- [ ] Schedule weekly review of implementation progress
```

---

## Финальный чеклист планирования

- [ ] Все ADR прочитаны
- [ ] Граф зависимостей построен
- [ ] Слои определены (Layer 0–5)
- [ ] Critical Path рассчитан
- [ ] Очередь приоритетов построена (Critical → Non-Critical)
- [ ] Прогресс из чеклистов получен
- [ ] Статистика реализации рассчитана
- [ ] Команды назначены
- [ ] Parallelization opportunities определены
- [ ] Отчёт планирования создан

---

## Связанные промпты

| Промпт | Когда использовать |
|--------|-------------------|
| `promt-feature-add.md` | После добавления нового ADR |
| `promt-consolidation.md` | После изменения зависимостей |
| `promt-verification.md` | Для получения прогресса ADR |
| `promt-index-update.md` | После изменения очереди внедрения |

---

## Метрики успеха планирования

| Метрика | Требование |
|---------|------------|
| Critical Path рассчитан | Да |
| Зависимости корректны | Нет циклов |
| Прогресс из чеклистов | Да (verify-adr-checklist.sh) |
| Команды назначены | Все ADR покрыты |
| Parallelization | Определены возможности |

---

## Anti-patterns при планировании

| Anti-pattern | Правильный подход |
|--------------|------------------|
| Игнорировать зависимости | Всегда проверять граф зависимостей |
| Планировать без слоёв | Использовать Layer 0→1→2→3→4→5 |
| Не проверять прогресс | Использовать verify-adr-checklist.sh |
| Секвенировать всё | Ищем parallelization opportunities |
| Не назначать команды | Каждому ADR — команда/owner |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 2.3 | 2026-03-18 | Добавлена структура отчёта планирования |
| 2.2 | 2026-03-06 | Добавлена parallelization optimization |
| 2.1 | 2026-02-25 | Добавлена team assignment logic |
| 2.0 | 2026-02-20 | Полный рефакторинг, Critical Path calculation |
| 1.5 | 2026-02-15 | Добавлена интеграция с verify-adr-checklist.sh |
| 1.0 | 2026-02-10 | Первая версия: basic queue management |

---

**Prompt Version:** 2.3
**Date:** 2026-03-18
