---

dependencies:
- promt-verification
- promt-index-update
description: Комплексная верификация соответствия ADR, качества кода и готовности
  к production
layer: Meta
name: promt-verification
status: active
tags:
- verification
- adr
- code
- quality
- self-verification
type: p9i
version: '3.4'
---

# AI Agent Prompt: Верификация качества кода и ADR

**Version:** 3.4
**Date:** 2026-03-18
**Purpose:** Комплексная верификация соответствия ADR, качества кода и готовности к production

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Meta / Verification |
| **Время выполнения** | 15–30 мин |
| **Домен** | Quality assurance — ADR и code verification |

**Пример запроса:**

> «Используя `promt-verification.md`, выполни полную верификацию проекта:
> ADR-соответствие, проверку чеклистов, качество кода и готовность к production.»

**Ожидаемый результат:**
- Детальный отчёт верификации с процентами соответствия
- Список нарушений ADR-инвариантов
- Прогресс реализации по всем ADR (planned/partial/full)
- Рекомендации по исправлению

---

## Когда использовать

- После завершения `promt-feature-add.md` — верификация новых изменений
- После завершения `promt-bug-fix.md` — проверка, что фикс не создал новых нарушений
- Periodic verification — еженедельный/monthly аудит
- Pre-production verification — перед release
- После `promt-consolidation.md` — проверка, что консолидация не потеряла контент

---

## Mission Statement

Ты — AI-агент, специализирующийся на **комплексной верификации** качества кода, ADR-соответствия и готовности к production.

Твоя задача — провести всесторонний анализ и выдать:
1. **ADR Verification Report** — соответствие архитектурным решениям
2. **Implementation Progress** — реальные проценты реализации ADR
3. **Code Quality Report** — технические метрики
4. **Production Readiness** — готовность к deployment

---

## Контракт синхронизации системы

Этот промпт управляется из единой точки: `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`.

Обязательные инварианты синхронизации:
- ADR идентифицируются по topic slug
- Двойной статус: `## Статус решения` + `## Прогресс реализации`
- Чеклисты являются источником правды о прогрессе реализации
- Связи ADR (dependencies) должны быть корректными
- `verify-adr-checklist.sh` используется для расчёта процентов

---

## Структура отчёта верификации

```json
{
  "verification_report": {
    "generated_at": "2026-03-18T12:00:00Z",
    "summary": {
      "total_adrs": 15,
      "critical_adrs": 5,
      "average_implementation": "67.3%",
      "adr_compliance": "94.2%",
      "code_quality": "87.5%",
      "production_ready": true
    },
    "adr_verification": {
      "critical_adrs": [
        {
          "topic_slug": "path-based-routing",
          "status": "Accepted",
          "implementation": "full",
          "progress": "100%",
          "compliance": "100%",
          "violations": []
        }
      ],
      "non_critical_adrs": [
        {
          "topic_slug": "unified-auth-architecture",
          "status": "Accepted",
          "implementation": "partial",
          "progress": "45%",
          "compliance": "90%",
          "violations": ["Missing JWT token refresh logic"]
        }
      ]
    },
    "implementation_progress": {
      "planned_adrs": 3,
      "partial_adrs": 7,
      "full_adrs": 5,
      "by_layer": {
        "layer_0_infrastructure": 85,
        "layer_1_platform": 72,
        "layer_2_bot": 65,
        "layer_3_payments": 50,
        "layer_4_monitoring": 80
      }
    },
    "code_quality": {
      "hardcoded_values": 0,
      "k3s_kubectl_hardcode": 0,
      "subdomain_ingress": 0,
      "missing_pydantic_settings": 2,
      "test_coverage": "65.3%",
      "lint_errors": 0
    },
    "production_readiness": {
      "status": "ready",
      "blocking_issues": [],
      "warnings": [
        "Test coverage below 70% threshold",
        "Missing 2 env vars in pydantic-settings"
      ],
      "recommendations": [
        "Increase test coverage to 70%+",
        "Add missing env vars to config"
      ]
    }
  }
}
```

---

## Шаг 0: Получить контекст верификации

### 0.1. Определить scope

```bash
# Если scope не указан — верифицировать всё
# Если scope указан — только конкретные ADR или модули

# Примеры scope:
# --all                    # Все ADR и код
# --topic path-based-routing  # Конкретный ADR
# --critical-only          # Только критические ADR
# --layer 2                # Только Layer 2 (Bot)
```

### 0.2. Получить список ADR

```bash
# Найти все ADR файлы
find docs/explanation/adr -name "ADR-*.md" | sort

# Получить критические ADR
grep -l "⭐" docs/explanation/adr/ADR-*.md
```

---

## Шаг 1: ADR Structure Verification

### 1.1. Проверить обязательные секции

Для каждого ADR проверить наличие:
- ✅ `## Статус решения` (Proposed/Accepted/Deprecated/Superseded)
- ✅ `## Прогресс реализации` (🔴 Не начато / 🟡 Частично / 🟢 Полностью)
- ✅ `## Контекст`
- ✅ `## Решение`
- ✅ `## Последствия` (Положительные/Отрицательные)
- ✅ `## Чеклист реализации`
- ✅ `## Связанные ADR`

```bash
# Скрипт для проверки структуры
./scripts/verify-all-adr.sh --structure-only
```

### 1.2. Проверить topic slug consistency

```bash
# Найти ADR без topic slug в имени файла
for f in docs/explanation/adr/ADR-*.md; do
  if ! [[ "$f" =~ ADR-[0-9]+-[a-z0-9-]+ ]]; then
    echo "Missing topic slug: $f"
  fi
done
```

---

## Шаг 2: Implementation Progress Calculation

### 2.1. Выполнить verify-adr-checklist.sh

```bash
# Полный отчёт по всем ADR
./scripts/verify-adr-checklist.sh

# Краткий формат для отчёта
./scripts/verify-adr-checklist.sh --format short

# Только критические ADR
./scripts/verify-adr-checklist.sh --critical-only
```

### 2.2. Классифицировать ADR по реализации

| Статус реализации | Процент | Значок | Описание |
|------------------|---------|--------|----------|
| **planned** | 0% | 🔴 Не начато | ADR принят, но ничего не реализовано |
| **partial** | 1–99% | 🟡 Частично | Реализована часть чеклиста |
| **full** | 100% | 🟢 Полностью | Все пункты чеклиста выполнены |

### 2.3. Рассчитать прогресс по слоям

```bash
# Layer mapping (из ADR-002 или project-rules.md)
Layer 0: Infrastructure (K8s, Helm, Storage, Networking)
Layer 1: Platform (DB, Auth, Caching)
Layer 2: Bot/API (Telegram, FastAPI)
Layer 3: Business Logic (Payments, SaaS)
Layer 4: Monitoring/Operations
Layer 5: Documentation
```

---

## Шаг 3: ADR Compliance Verification

### 3.1. Проверить критические инварианты

```bash
# Invariant 1: No hardcoded kubectl
grep -r "k3s kubectl\|microk8s kubectl" scripts/ makefiles/ telegram-bot/
# Expected: 0 matches

# Invariant 2: No subdomains in ingress
grep -E "host:.*\.(com|ru|io)" templates/ingress.yaml
# Expected: 0 matches (only path-based routing)

# Invariant 3: pydantic-settings for Python config
grep "from pydantic_settings import" telegram-bot/app/config.py
# Expected: found

# Invariant 4: No hardcoded secrets
grep -rE "(password|secret|token)\s*=\s*['\"][^{]" telegram-bot/app/
# Expected: 0 matches
```

### 3.2. Проверить ADR-specific constraints

Для каждого ADR проверить:
- ✅ Выполнены ли все пункты чеклиста?
- ✅ Соблюдены ли специфические правила ADR?
- ✅ Нет ли нарушений, указанных в ADR?

```bash
# Пример проверки ADR path-based-routing
# Check: все ли ingress используют paths, не hosts
find templates -name "*.yaml" -exec grep -l "kind: Ingress" {} \; | \
  while read f; do
    if grep -q "host:" "$f" && ! grep -q "path: " "$f"; then
      echo "Subdomain in $f (violates path-based-routing)"
    fi
  done
```

---

## Шаг 4: Code Quality Verification

### 4.1. Запустить automated checks

```bash
# Python lint
cd telegram-bot && python -m flake8 app/ tests/
cd telegram-bot && python -m mypy app/

# Bash lint
shellcheck scripts/**/*.sh

# YAML lint
yamllint config/ templates/

# Helm lint
helm lint .

# Makefile validation
make validate-make-no-aliases
```

### 4.2. Проверить test coverage

```bash
# Run tests with coverage
cd telegram-bot && poetry run pytest --cov=app --cov-report=term-missing

# Check threshold (should be ≥ 70%)
cd telegram-bot && poetry run pytest --cov=app --cov-fail-under=70
```

### 4.3. Проверить code style

```bash
# Python formatting check
cd telegram-bot && python -m black --check app/ tests/

# Import sorting
cd telegram-bot && python -m isort --check-only app/ tests/
```

---

## Шаг 5: Production Readiness Assessment

### 5.1. Проверить production requirements

| Критерий | Требование | Проверка |
|----------|------------|----------|
| **ADR Compliance** | ≥ 95% | `./scripts/verify-all-adr.sh` |
| **Code Quality** | 0 lint errors | `make lint` |
| **Test Coverage** | ≥ 70% | `poetry run pytest --cov` |
| **Critical ADRs** | 100% implemented | `./scripts/verify-adr-checklist.sh --critical` |
| **Security** | No hardcoded secrets | `grep -rE "(password|secret)"` |
| **Documentation** | README updated | `make docs-validate` |

### 5.2. Определить статус production ready

```python
# Logic:
if (adr_compliance >= 95 and
    code_quality_errors == 0 and
    test_coverage >= 70 and
    critical_adrs_full and
    no_hardcoded_secrets):
    status = "ready"
elif blocking_issues_count == 0:
    status = "ready_with_warnings"
else:
    status = "not_ready"
```

---

## Шаг 6: Generate Verification Report

### 6.1. Создать отчёт в JSON формате

Сохранить в: `artifacts/verification/verification-report-{timestamp}.json`

```json
{
  "verification_report": { ... }  # См. структуру выше
}
```

### 6.2. Создать читаемую версию

Сохранить в: `artifacts/verification/verification-report-{timestamp}.md`

```markdown
# Verification Report
**Date:** 2026-03-18
**Scope:** All ADRs and code

## Summary

- **Total ADRs:** 15
- **Critical ADRs:** 5
- **Average Implementation:** 67.3%
- **ADR Compliance:** 94.2%
- **Code Quality:** 87.5%
- **Production Ready:** ✅ Yes

## ADR Details

### Critical ADRs (5/5 full)

| Topic Slug | Status | Progress | Compliance |
|------------|--------|----------|------------|
| path-based-routing | Accepted | 100% | 100% |
| k8s-provider-abstraction | Accepted | 100% | 100% |
| storage-provider-selection | Accepted | 100% | 100% |
| telegram-bot-saas-platform | Accepted | 90% | 100% |
| documentation-generation | Accepted | 100% | 100% |

### Non-Critical ADRs

| Topic Slug | Status | Progress | Compliance |
|------------|--------|----------|------------|
| unified-auth-architecture | Accepted | 45% | 90% |
| e2e-testing-new-features | Accepted | 60% | 85% |
| helm-chart-structure-optimization | Accepted | 30% | 80% |
| gitops-validation | Accepted | 20% | 75% |
| metrics-alerting-strategy | Accepted | 0% | N/A |

## Code Quality

| Metric | Value | Status |
|--------|-------|--------|
| Hardcoded values | 0 | ✅ |
| kubectl hardcode | 0 | ✅ |
| Subdomain ingress | 0 | ✅ |
| Missing pydantic-settings | 2 | ⚠️ |
| Test coverage | 65.3% | ⚠️ |
| Lint errors | 0 | ✅ |

## Production Readiness

**Status:** ✅ Ready with warnings

### Warnings
- Test coverage below 70% threshold (65.3%)
- Missing 2 env vars in pydantic-settings

### Recommendations
1. Increase test coverage to 70%+ by adding tests for payment flows
2. Add NEW_FEATURE_API_KEY and NEW_FEATURE_ENABLED to telegram-bot/app/config.py

## Blocking Issues
None found.
```

---

## Шаг 7: Action Items & Follow-up

### 7.1. Приоритизировать issues

| Priority | Issue | Action | Owner |
|----------|-------|--------|-------|
| **P0** | Blocking issues | Fix immediately | Dev |
| **P1** | Critical ADR < 100% | Complete implementation | Dev |
| **P2** | Test coverage < 70% | Add tests | QA |
| **P3** | Missing env vars | Add to config | Dev |

### 7.2. Обновить ADR индекс (если изменился прогресс)

```bash
# Если изменился прогресс реализации ADR
cat docs/ai-agent-prompts/promt-index-update.md
# Контекст: После verification, обновить проценты в index.md
```

---

## Финальный чеклист верификации

- [ ] Структура всех ADR проверена (обязательные секции)
- [ ] Topic slug consistency проверена
- [ ] verify-adr-checklist.sh выполнен
- [ ] Прогресс реализации рассчитан (planned/partial/full)
- [ ] Критические инварианты проверены
- [ ] Code quality checks выполнены
- [ ] Test coverage измерена
- [ ] Production readiness оценён
- [ ] Verification report создан (JSON + MD)
- [ ] Action items определены
- [ ] При необходимости запущен promt-index-update.md

---

## Связанные промпты

| Промпт | Когда использовать |
|--------|-------------------|
| `promt-feature-add.md` | После — верификация новых изменений |
| `promt-bug-fix.md` | После — проверка, что фикс не создал нарушений |
| `promt-consolidation.md` | После — проверка консолидации |
| `promt-index-update.md` | При изменении прогресса ADR |

---

## Метрики успеха верификации

| Метрика | Требование |
|---------|------------|
| ADR Compliance | ≥ 95% |
| Critical ADRs Implementation | 100% |
| Code Quality (lint) | 0 errors |
| Test Coverage | ≥ 70% |
| Production Readiness | Ready/Ready with warnings |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 3.4 | 2026-03-18 | Добавлена структура JSON отчёта, секция Production Readiness Assessment |
| 3.3 | 2026-03-06 | Добавлен фильтр --critical-only для verify-adr-checklist.sh |
| 3.2 | 2026-02-25 | Добавлена классификация ADR по слоям (Layer 0–5) |
| 3.1 | 2026-02-24 | Интеграция с verify-adr-checklist.sh |
| 3.0 | 2026-02-20 | Полный рефакторинг, добавлен double-status ADR support |

---

**Prompt Version:** 3.4
**Date:** 2026-03-18
