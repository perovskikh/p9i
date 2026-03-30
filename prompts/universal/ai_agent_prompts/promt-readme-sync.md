---

dependencies:
- promt-verification
- promt-index-update
description: Автоматическая синхронизация README.md с текущим состоянием prompt registry
layer: Meta
name: promt-readme-sync
status: active
tags:
- sync
- readme
- documentation
type: p9i
version: '1.0'
---

# AI Agent Prompt: Синхронизация README.md с registry.json

**Version:** 1.0
**Date:** 2026-03-18
**Purpose:** Автоматическая синхронизация README.md с текущим состоянием prompt registry

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Meta / Synchronization |
| **Время выполнения** | 5–10 мин |
| **Домен** | Documentation — README synchronization |

**Пример запроса:**

> «Используя `promt-readme-sync.md`, синхронизируй README.md
> с prompts/registry.json: обнови количество промтов, добавь новые категории.»

**Ожидаемый результат:**
- Обновлённый README.md с актуальными данными из registry.json
- Корректное количество промтов по категориям
- Актуальные ссылки и навигация

---

## Когда использовать

- После добавления новых промтов в registry.json
- После изменения структуры промтов (новые tier, category)
- Periodic sync — еженедельная проверка
- После рефакторинга структуры prompts/

---

## Mission Statement

Ты — AI-агент, специализирующийся на **синхронизации README.md** — поддержании актуальности главной документации.

Твоя задача:
1. **Прочитать registry.json** — получить текущее состояние системы
2. **Обновить README.md** — синхронизировать количество, категории, ссылки
3. **Проверить навигацию** — все ссылки корректны
4. **Обновить статистику** — общее количество промтов по tier

---

## Контракт синхронизации системы

Обязательные инварианты:
- README.md всегда отражает текущее состояние registry.json
- Количество промтов рассчитывается автоматически из registry
- Все ссылки на промты корректны
- Категории в README.md соответствуют tiers в registry

---

## Шаг 1: Чтение registry.json

```bash
# Получить общее количество промтов
jq '.prompts | length' prompts/registry.json

# Получить количество по tier
jq '.prompts | group_by(.tier) | map({tier: .[0].tier, count: length})' prompts/registry.json

# Получить список всех промтов
jq -r '.prompts[].name' prompts/registry.json
```

---

## Шаг 2: Обновление README.md

### 2.1. Обновить секцию Overview

```markdown
## Overview

AI Prompt System is an MCP (Model Context Protocol) server for managing AI prompts
through their full lifecycle: from idea to production implementation.

**Current Version:** 2.0.0
**Total Prompts:** 66
**Prompt Tiers:** Core (5) + Universal (16) + MPV Stages (7) + Meta (43)

### Prompt Distribution

| Tier | Count | Description |
|------|-------|-------------|
| **Core** | 5 | Baseline prompts, immutable, SHA256 protected |
| **Universal** | 16 | Universal AI Agent prompts, project-agnostic |
| **MPV Stages** | 7 | 7-Stage MPV pipeline prompts (ideation → finish) |
| **Meta** | 43 | Verification, consolidation, sync, and system prompts |
```

### 2.2. Обновить секцию Core Prompts

```markdown
## Core Prompts (Baseline)

Core prompts are immutable and protected by SHA256 checksums in `.promt-baseline-lock`.

| Prompt | Version | Description | Status |
|--------|----------|-------------|--------|
| `promt-feature-add.md` | 1.5 | Adding new functionality | ✅ Protected |
| `promt-bug-fix.md` | 1.2 | Fixing bugs and debugging | ✅ Protected |
| `promt-refactoring.md` | 1.2 | Improving code structure | ✅ Protected |
| `promt-security-audit.md` | 1.2 | Security audit and assessment | ✅ Protected |
| `promt-quality-test.md` | 1.2 | Quality assurance testing | ✅ Protected |

**Location:** `prompts/core/`
**Protection:** SHA256 checksums, server-side enforcement, read-only FS
```

### 2.3. Обновить секцию Universal Prompts

```markdown
## Universal AI Agent Prompts

Universal prompts are project-agnostic and can be used across any project.

| Category | Prompt | Version | Description | Tags |
|----------|---------|----------|-------------|------|
| **Discovery** | promt-project-stack-dump.md | 1.1 | Quick project analysis and status | universal, stack, dump |
| **Planning** | promt-project-adaptation.md | 1.1 | Adapt system to specific project | universal, adaptation, onboard |
| **Planning** | promt-system-adapt.md | 1.0 | Automatic initialization | universal, adapt, init |
| **Operations** | promt-feature-add.md | 1.5 | Adding new functionality | universal, feature, adr |
| **Operations** | promt-bug-fix.md | 1.2 | Fixing bugs and debugging | universal, bug, fix |
| **Operations** | promt-refactoring.md | 1.2 | Code refactoring | universal, refactor |
| **Operations** | promt-security-audit.md | 1.2 | Security audit | universal, security, audit |
| **Operations** | promt-quality-test.md | 1.2 | Quality testing | universal, qa, testing |
| **Operations** | promt-ci-cd-pipeline.md | 1.2 | CI/CD setup | universal, ci-cd, pipeline |
| **Documentation** | promt-onboarding.md | 1.2 | New developer onboarding | universal, onboard, docs |
| **Documentation** | promt-context7-generation.md | 1.0 | Context7-based code generation | universal, context7, code |
| **Meta** | promt-prompt-creator.md | 1.0 | Create new prompts | universal, meta, template |
| **Meta** | promt-versioning-policy.md | 1.2 | Versioning policy (SemVer) | universal, version, policy |

**Location:** `prompts/universal/ai_agent_prompts/`
```

### 2.4. Обновить секцию MPV Stage Prompts

```markdown
## MPV Stage Prompts (7-Stage Pipeline)

The MPV (Model-Product-Validation) pipeline provides a structured 7-stage approach
from idea to production.

| Stage | Prompt | Version | Description | Dependencies |
|-------|--------|----------|-------------|---------------|
| 1. Ideation | promt-ideation.md | 1.0 | Generate prioritized ideas | None |
| 2. Analysis | promt-analysis.md | 1.0 | Analyze requirements and risks | ideation |
| 3. Design | promt-design.md | 1.0 | Architecture planning | analysis |
| 4. Implementation | promt-implementation.md | 1.0 | Code generation | design |
| 5. Testing | promt-testing.md | 1.0 | Quality validation | implementation |
| 6. Debugging | promt-debugging.md | 1.0 | Self-correction | testing |
| 7. Finish | promt-finish.md | 1.0 | Documentation & delivery | debugging, testing, implementation |

**Location:** `prompts/universal/mpv_stages/`
**Registry:** `prompts/universal/mpv_stages/registry.json`
```

### 2.5. Обновить секцию Meta/Sync Prompts

```markdown
## Meta & Synchronization Prompts

Meta prompts manage the prompt system lifecycle, verification, and synchronization.

| Category | Prompt | Version | Description |
|----------|--------|----------|-------------|
| **Verification** | promt-verification.md | 3.4 | ADR and code quality verification |
| **Consolidation** | promt-consolidation.md | 2.5 | Merge duplicate ADRs, dedup |
| **Sync** | promt-index-update.md | 2.6 | Update index.md and navigation |
| **Sync** | promt-readme-sync.md | 1.0 | Sync README.md with registry |
| **Sync** | promt-project-rules-sync.md | 1.1 | Sync project rules |
| **Planning** | promt-adr-implementation-planner.md | 2.3 | ADR implementation tracking |
| **Migration** | promt-adr-template-migration.md | 1.4 | Migrate to new ADR formats |
| **Orchestration** | promt-workflow-orchestration.md | 1.2 | Workflow orchestration |
| **Export** | promt-sync-report-export.md | 1.2 | Export sync reports |
| **Docs** | promt-documentation-quality-compression.md | 1.1 | Documentation quality |
| **Evolution** | promt-system-evolution.md | 1.2 | System evolution & roadmap |

**Location:** `prompts/universal/ai_agent_prompts/`
```

---

## Шаг 3: Верификация синхронизации

### 3.1. Проверить количество промтов

```bash
# Сравнить с registry.json
registry_count=$(jq '.prompts | length' prompts/registry.json)
readme_count=$(grep "Total Prompts:" README.md | grep -oE '[0-9]+')

if [ "$registry_count" -ne "$readme_count" ]; then
  echo "Count mismatch: registry=$registry_count, readme=$readme_count"
fi
```

### 3.2. Проверить все ссылки

```bash
# Найти все ссылки на промты в README.md
grep -oE 'promt-[a-z0-9-]+\.md' README.md | sort -u

# Проверить, что все файлы существуют
for prompt in $(grep -oE 'promt-[a-z0-9-]+\.md' README.md); do
  if ! find prompts/ -name "$prompt" > /dev/null; then
    echo "Broken link: $prompt"
  fi
done
```

---

## Шаг 4: Создание отчёта синхронизации

```markdown
# README Sync Report
**Date:** 2026-03-18

## Summary

- ✅ README.md updated with registry.json data
- ✅ Total prompts: 66
- ✅ All categories synchronized
- ✅ All links verified

## Changes

| Section | Before | After |
|---------|--------|-------|
| Total Prompts | 31 | 66 |
| Core Prompts | 5 | 5 |
| Universal Prompts | 16 | 16 |
| MPV Stage Prompts | 7 | 7 |
| Meta Prompts | 3 | 43 |

## Verification

- ✅ Count matches registry.json
- ✅ All prompt links valid
- ✅ All categories present
```

---

## Финальный чеклист

- [ ] registry.json прочитан
- [ ] README.md секция Overview обновлена
- [ ] Core Prompts секция обновлена
- [ ] Universal Prompts секция обновлена
- [ ] MPV Stage Prompts секция обновлена
- [ ] Meta Prompts секция обновлена
- [ ] Количество промтов синхронизировано
- [ ] Все ссылки проверены
- [ ] Отчёт создан

---

## Связанные промпты

| Промпт | Когда использовать |
|--------|-------------------|
| `promt-index-update.md` | После изменений ADR |
| `promt-consolidation.md` | После консолидации промтов |
| `promt-prompt-creator.md` | После создания нового промта |

---

**Prompt Version:** 1.0
**Date:** 2026-03-18
