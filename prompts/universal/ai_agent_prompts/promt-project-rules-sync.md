---

dependencies:
- promt-verification
- promt-index-update
description: Синхронизация правил проекта (`docs/rules/project-rules.md`) с текущим
  состоянием ADR и промтов
layer: Meta
name: promt-project-rules-sync
status: active
tags:
- rules
- sync
- project
- configuration
type: p9i
version: '1.1'
---

# AI Agent Prompt: Синхронизация project rules с системой

**Version:** 1.1
**Date:** 2026-03-18
**Purpose:** Синхронизация правил проекта (`docs/rules/project-rules.md`) с текущим состоянием ADR и промтов

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Meta / Synchronization |
| **Время выполнения** | 15–25 мин |
| **Домен** | Project configuration — rules synchronization |

**Пример запроса:**

> «Используя `promt-project-rules-sync.md`, синхронизируй project-rules.md
> с текущими ADR и промтами: обнови инварианты, topic registry, ограничения.»

**Ожидаемый результат:**
- Обновлённый `docs/rules/project-rules.md` с актуальными правилами
- Синхронизированный ADR Topic Registry
- Актуальные инварианты и ограничения

---

## Когда использовать

- После изменения ADR (добавлен/удален/изменен)
- После добавления новых промтов
- После изменения архитектурных принципов
- Periodic sync — еженедельная проверка
- После изменения ограничений I-1..I-9 или C1–C10

---

## Mission Statement

Ты — AI-агент, специализирующийся на **синхронизации project-rules.md** — поддержании актуальности правил проекта.

Твоя задача:
1. **Прочитать все ADR** — извлечь инварианты и ограничения
2. **Прочитать промты** — получить system-wide constraints
3. **Обновить project-rules.md** — синхронизировать все правила
4. **Обновить ADR Topic Registry** — актуальный список критических ADR

---

## Контракт синхронизации системы

Обязательные инварианты:
- project-rules.md всегда отражает текущее состояние ADR и промтов
- Инварианты I-1..I-9 синхронизированы с ADR
- Ограничения C1–C10 синхронизированы с промтами
- ADR Topic Registry включает все критические ADR

---

## Шаг 1: Чтение ADR и промтов

### 1.1. Получить список всех ADR

```bash
# Найти все ADR файлы
find docs/explanation/adr -name "ADR-*.md" | sort

# Получить topic slugs
find docs/explanation/adr -name "ADR-*.md" | \
  sed -E 's/.*ADR-[0-9]+-([^.]+)\.md/\1/' | sort
```

### 1.2. Получить инварианты из ADR

```bash
# Найти инварианты в ADR
grep -h "^## Инвариант" docs/explanation/adr/ADR-*.md | sort -u
```

### 1.3. Получить ограничения из промтов

```bash
# Найти ограничения I-1..I-9
grep -hE "I-[1-9]\." prompts/universal/ai_agent_prompts/*.md | sort -u

# Найти ограничения C1–C10
grep -hE "C[1-9]\.|C10\." prompts/universal/ai_agent_prompts/*.md | sort -u
```

---

## Шаг 2: Обновление ADR Topic Registry

### 2.1. Собрать критические ADR

```bash
# Найти все критические ADR (отмечены ⭐)
grep -l "⭐" docs/explanation/adr/ADR-*.md | while read f; do
  slug=$(basename "$f" | sed -E 's/ADR-[0-9]+-([^.]+)\.md/\1/')
  title=$(grep "^# " "$f" | head -1 | sed 's/^# //')
  echo "$slug|$title"
done
```

### 2.2. Обновить таблицу в project-rules.md

```markdown
## ADR Topic Registry

> **КРИТИЧНО:** ADR идентифицируются по **topic slug** (не по номеру).
> Номера нестабильны. Поиск: `find docs/explanation/adr -name "ADR-*-{slug}*.md" | head -1`

| Topic Slug | Краткое описание | Критический |
|---|---|---|
| `path-based-routing` | Single domain, path-based routing вместо subdomains | ⭐ |
| `k8s-provider-abstraction` | `$KUBECTL_CMD`, никогда не хардкодить ${K8S_PROVIDER} kubectl | ⭐ |
| `storage-provider-selection` | Longhorn (prod), local-path (dev) — storage providers | ⭐ |
| `telegram-bot-saas-platform` | pydantic-settings, env vars, PLAN_SPECS конфигурация | ⭐ |
| `documentation-generation` | Reference docs ТОЛЬКО AUTO-GENERATED | ⭐ |
| `unified-auth-architecture` | JWT + Telegram auth унификация |  |
| `e2e-testing-new-features` | E2E тестирование новых функций |  |
| `helm-chart-structure-optimization` | Оптимизация Helm chart структуры |  |
| `gitops-validation` | ArgoCD + GitOps валидация |  |
| `metrics-alerting-strategy` | Prometheus + Grafana alerting |  |
```

---

## Шаг 3: Обновление инвариантов (I-1..I-9)

### 3.1. Собрать все инварианты

```markdown
## Инварианты системы (I-1..I-9)

| # | Инвариант | Источник | Статус |
|---|------------|----------|--------|
| **I-1** | Никогда не хардкодить ${K8S_PROVIDER} kubectl — использовать `$KUBECTL_CMD` | ADR-002 | ✅ Active |
| **I-2** | Все новые маршруты — path-based, не subdomains | ADR-001 | ✅ Active |
| **I-3** | Конфигурация через pydantic-settings и env vars | ADR-004 | ✅ Active |
| **I-4** | Reference docs ТОЛЬКО AUTO-GENERATED (через make docs-update) | ADR-005 | ✅ Active |
| **I-5** | `docs/official_document/` — ТОЛЬКО ДЛЯ ЧТЕНИЯ | All prompts | ✅ Active |
| **I-6** | ADR идентифицируются по topic slug, не по номеру | All ADRs | ✅ Active |
| **I-7** | Никогда не создавать alias targets в Makefile | All prompts | ✅ Active |
| **I-8** | Использовать `kubectl apply`, никогда `kubectl create` | ADR-002 | ✅ Active |
| **I-9** | Secrets никогда в коде — только через env vars / K8s secrets | ADR-004 | ✅ Active |
```

### 3.2. Описание каждого инварианта

```markdown
### I-1: K8s Provider Abstraction

**Инвариант:** Никогда не хардкодить `k3s kubectl` или `microk8s kubectl` в скриптах.
Использовать `$KUBECTL_CMD` — переменную, которая определяется автоматически.

**Пример нарушения:**
```bash
# ❌ Плохо
k3s kubectl get pods

# ✅ Хорошо
$KUBECTL_CMD get pods
```

**ADR:** ADR-002-k8s-provider-abstraction.md
**Промты:** promt-feature-add.md, promt-bug-fix.md
```

---

## Шаг 4: Обновление ограничений (C1–C10)

### 4.1. Собрать все ограничения

```markdown
## Ограничения системы (C1–C10)

| # | Ограничение | Источник | Статус |
|---|-------------|----------|--------|
| **C1** | Использовать 4 spaces indentation в bash scripts | promt-feature-add | ✅ Active |
| **C2** | Использовать 2 spaces indentation в YAML | promt-feature-add | ✅ Active |
| **C3** | Bash скрипты обязаны иметь `set -euo pipefail` | promt-feature-add | ✅ Active |
| **C4** | Helm install — `--wait=false` + отдельный `kubectl wait` | promt-feature-add | ✅ Active |
| **C5** | Никогда не редактировать config/values*.yaml напрямую | promt-feature-add | ✅ Active |
| **C6** | Создавать только stand-alone subcharts | promt-feature-add | ✅ Active |
| **C7** | Никогда не редактировать docs/reference/ вручную | promt-feature-add | ✅ Active |
| **C8** | Никогда не изменять docs/official_document/ | promt-feature-add | ✅ Active |
| **C9** | Никогда не создавать PHASE_*.md, *_COMPLETE.md, *_SUMMARY.md | promt-feature-add | ✅ Active |
| **C10** | Никогда не создавать директории: reports/, plans/, artifacts/archive/ | promt-feature-add | ✅ Active |
```

### 4.2. Описание каждого ограничения

```markdown
### C1: Bash Indentation

**Ограничение:** Использовать 4 spaces indentation во всех bash скриптах.

**Пример нарушения:**
```bash
# ❌ Плохо (2 spaces)
function foo() {
  echo "bar"
}

# ✅ Хорошо (4 spaces)
function foo() {
    echo "bar"
}
```

**Промты:** promt-feature-add.md, promt-bug-fix.md
```

---

## Шаг 5: Обновление архитектурных принципов

### 5.1. Обновить секцию Architectural Principles

```markdown
## Архитектурные принципы

### Tiered Prompt Architecture (ADR-002)

Система промтов организована в 3-tier cascade:
- **Tier 0 (Core):** 5 baseline prompts, immutable, SHA256 protected
- **Tier 1 (Universal):** 16 universal prompts, project-agnostic
- **Tier 2 (MPV Stages):** 7-stage pipeline prompts (ideation → finish)
- **Tier 3 (Meta):** 43 meta/sync/prompts for system management

**Cascade Override Priority:** Projects → MPV Stages → Universal → Core

### Lazy Loading Pattern

Все промты загружаются по требованию через FastAPI Depends() pattern:
- `get_prompt_by_name()` — получить конкретный промт
- `get_tier_prompts(tier)` — получить все промты tier
- `get_all_prompts()` — получить все промты (rarely used)

### Baseline Protection

Core prompts защищены:
- SHA256 checksums в `.promt-baseline-lock`
- Server-side enforcement immutability flags
- Read-only file system permissions на `core/` директории
```

---

## Шаг 6: Обновление секции Prompt System Integration

```markdown
## Prompt System Integration

### Использование промтов в работе

Все промты доступны через MCP tools:
- `ai_prompts` — natural language router для auto-selection
- `run_prompt` — выполнить конкретный промт
- `run_prompt_chain` — выполнить цепочку промтов
- `list_prompts` — получить список всех промтов
- `get_project_memory` — получить контекст проекта
- `save_project_memory` — сохранить контекст проекта

### Intent Map для ai_prompts

| Keyword | Prompt | Цель |
|---------|--------|------|
| `feature`, `добавить` | promt-feature-add.md | Добавить новый функционал |
| `bug`, `исправить` | promt-bug-fix.md | Исправить баг |
| `refactor`, `рефакторинг` | promt-refactoring.md | Рефакторинг кода |
| `security`, `безопасность` | promt-security-audit.md | Аудит безопасности |
| `test`, `тест` | promt-quality-test.md | Тестирование качества |
| `ci-cd`, `pipeline` | promt-ci-cd-pipeline.md | CI/CD настройка |
| `version`, `версия` | promt-versioning-policy.md | Политика версионирования |
| `adapt`, `адаптация` | promt-project-adaptation.md | Адаптация проекта |
| `создай промт` | promt-prompt-creator.md | Создать новый промт |
| `адаптируй`, `новый проект` | promt-system-adapt.md | Инициализация системы |

### MPV Pipeline (7 Stages)

Полный MPV pipeline от идеи до production:
1. **Ideation** — генерация идей с оценками приоритизации
2. **Analysis** — анализ требований, рисков, приоритетов
3. **Design** — архитектурное проектирование и детальный план
4. **Implementation** — генерация кода реализации
5. **Testing** — Quality Gates A-H и comprehensive testing
6. **Debugging** — самокоррекция и incident management
7. **Finish** — документация и delivery

Выполнение pipeline: `run_prompt_chain(idea, ["ideation", "analysis", "design", "implementation", "testing", "debugging", "finish"])`
```

---

## Шаг 7: Верификация синхронизации

### 7.1. Проверить все инварианты

```bash
# Проверить, что все инварианты I-1..I-9 есть в project-rules.md
for i in {1..9}; do
  if ! grep -q "I-$i" docs/rules/project-rules.md; then
    echo "Missing invariant: I-$i"
  fi
done
```

### 7.2. Проверить все ограничения

```bash
# Проверить, что все ограничения C1..C10 есть в project-rules.md
for i in {1..9} 10; do
  if ! grep -q "C$i" docs/rules/project-rules.md; then
    echo "Missing constraint: C$i"
  fi
done
```

### 7.3. Проверить ADR Topic Registry

```bash
# Проверить, что все критические ADR есть в registry
for adr in $(grep -l "⭐" docs/explanation/adr/ADR-*.md); do
  slug=$(basename "$adr" | sed -E 's/ADR-[0-9]+-([^.]+)\.md/\1/')
  if ! grep -q "$slug" docs/rules/project-rules.md; then
    echo "Critical ADR missing from registry: $slug"
  fi
done
```

---

## Шаг 8: Создание отчёта синхронизации

```markdown
# Project Rules Sync Report
**Date:** 2026-03-18

## Summary

- ✅ docs/rules/project-rules.md обновлён
- ✅ ADR Topic Registry синхронизирован
- ✅ Инварианты I-1..I-9 обновлены
- ✅ Ограничения C1..C10 обновлены
- ✅ Архитектурные принципы обновлены

## Changes

| Section | Before | After |
|---------|--------|-------|
| Critical ADRs | 5 | 5 |
| Invariants (I-1..I-9) | 9 | 9 |
| Constraints (C1..C10) | 10 | 10 |
| MPV Stages | 7 | 7 |

## Verification

- ✅ All invariants present in project-rules.md
- ✅ All constraints present in project-rules.md
- ✅ All critical ADRs in ADR Topic Registry
- ✅ No outdated references found
```

---

## Финальный чеклист

- [ ] Все ADR прочитаны
- [ ] Все промты прочитаны
- [ ] ADR Topic Registry обновлён
- [ ] Инварианты I-1..I-9 обновлены
- [ ] Ограничения C1..C10 обновлены
- [ ] Архитектурные принципы обновлены
- [ ] Prompt System Integration обновлена
- [ ] Все инварианты проверены
- [ ] Все ограничения проверены
- [ ] ADR Topic Registry проверен
- [ ] Отчёт создан

---

## Связанные промпты

| Промпт | Когда использовать |
|--------|-------------------|
| `promt-feature-add.md` | После добавления нового ADR |
| `promt-consolidation.md` | После консолидации ADR |
| `promt-verification.md` | После верификации ADR |
| `promt-index-update.md` | После изменений в index.md |

---

**Prompt Version:** 1.1
**Date:** 2026-03-18
