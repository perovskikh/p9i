---

dependencies:
- promt-verification
- promt-index-update
description: Зафиксировать единые правила version bump (MAJOR/MINOR/PATCH) для prompt-файлов
  и проверяемый workflow синхронизации header/footer/README registry
layer: Meta
name: promt-versioning-policy
status: active
tags:
- versioning
- policy
- semver
- registry
type: p9i
version: '1.3'
---

# AI Agent Prompt: Формальная semver-политика промптов для 

**Version:** 1.3
**Date:** 2026-02-24
**Purpose:** Зафиксировать единые правила version bump (MAJOR/MINOR/PATCH) для prompt-файлов и проверяемый workflow синхронизации header/footer/README registry

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Operational / Governance |
| **Время выполнения** | 10–20 мин |
| **Домен** | Governance — versioning policy |

**Пример запроса:**

> «Используя `promt-versioning-policy.md`, классифицируй изменения в
> `<список промптов>` и предложи корректный semver bump с чеклистом для PR.»

**Ожидаемый результат:**
- Классификация каждого изменения: MAJOR / MINOR / PATCH
- Рекомендованный version bump для каждого файла
- Чеклист для PR: header, footer, README registry согласованы
- Обнаружены несоответствия header ↔ footer ↔ README (если есть)

---

## Когда использовать

- При любом изменении промпта — до коммита (классификация bump)
- После batch-update промптов — проверить консистентность версий
- При обнаружении несоответствия header / footer / README
- Как часть PR-checklist для изменений в `docs/ai-agent-prompts/`

---

## Mission Statement

Ты — AI-агент, отвечающий за консистентное версионирование prompt-системы .
Твоя задача — определить корректный тип изменения версии для каждого обновления промпта,
обеспечить синхронное обновление версии в header/footer и в реестре `docs/ai-agent-prompts/README.md`,
а также применить проверяемый PR-checklist до merge.

Этот промпт не заменяет drift/version/legacy проверки, а задаёт формальную политику,
по которой эти проверки становятся предсказуемыми и единообразными.

---

## Контракт синхронизации системы

> **Source of truth:** `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`
> При конфликте формулировок приоритет у source of truth.

**Обязательные инварианты:**
- ADR идентифицируются по **topic slug**
- Для ADR-материалов сохраняется dual-status (`## Статус решения` + `## Прогресс реализации`)
- `docs/official_document/` — READ-ONLY
- Anti-legacy: не создавать `PHASE_*.md`, `*_SUMMARY.md`, `*_REPORT.md`, `reports/`, `plans/`
- Update in-place без `*-v2.md`, `*-new.md`, `*-final.md`
- Реестр версий в `docs/ai-agent-prompts/README.md` и `registry.yaml` должен совпадать с реальными файлами
- Для валидации прогресса ADR использовать `./scripts/verify-adr-checklist.sh --summary`

---

## Назначение

Этот промпт вводит формальную semver-политику для prompt-файлов, чтобы
однозначно решать, когда повышать MAJOR/MINOR/PATCH, и как синхронизировать
версии между header/footer/README registry и `registry.yaml`.

## Входы

- Изменённые prompt-файлы в `docs/ai-agent-prompts/`
- Описание изменений (что именно изменилось в структуре/логике/формате)
- Текущие версии header/footer prompt-файлов
- Текущий реестр версий в `docs/ai-agent-prompts/README.md`
- Текущий `registry.yaml`

## Выходы

- Решение по version bump для каждого затронутого промпта
- Обновлённые версии в header/footer/README registry и `registry.yaml`
- PR checklist со статусами pass/fail
- Краткий отчёт о совместимости и рисках рассинхронизации

## Ограничения / инварианты

- Не изменять read-only зоны (`docs/official_document/`, `.roo/`)
- Не добавлять дублирующие документы политики (`*policy-v2*`, `*final*`)
- Все изменения версий выполнять в рамках одного PR
- Применять политику одинаково к operational и meta prompt-файлам
- `registry.yaml` является Source of Truth для метаданных промптов

## Workflow шаги

1. Discovery: собрать список изменённых prompt-файлов и текущих версий
2. Context7 Gate: подтвердить best practices semver policy/CI gating
3. Classification: классифицировать изменения по типам
4. Version Decision: определить MAJOR/MINOR/PATCH для каждого файла
5. Sync Update: синхронно обновить header/footer/README registry и `registry.yaml`
6. Validation: прогнать prompt-guard проверки, включая Gates A-H
7. PR Gate: проверить checklist и сформировать итоговый verdict

## Проверки / acceptance criteria

- Для каждого изменённого промпта есть обоснованный version bump
- Header и footer версии совпадают
- README registry и `registry.yaml` синхронизированы с файлами
- `check-prompt-versions.sh` проходит без ошибок
- Нет нарушений anti-legacy/read-only ограничений
- Все Quality Gates (A-H) пройдены для затронутых промптов

## Связи с другими промптами

- До: `promt-sync-optimization.md` (при системном аудите)
- После: соответствующий operational prompt по домену изменений
- Registry Schema: `docs/reference/prompt-registry-schema.md`

---

## Project Context

### О проекте (versioning domain)

 поддерживает расширяемую prompt-систему для ADR и dev/infra workflow.
Без формальной semver-политики версия может расходиться между файлами,
реестром (`README.md` и `registry.yaml`) и CI проверками, что приводит к ложным fail и потере трассируемости.

### ADR Topic Registry (релевантные topics)

| Topic Slug | Связь с versioning policy |
|---|---|
| `documentation-generation` | Единые правила обновления docs и реестров |
| `${PLATFORM_SLUG}` | Бизнес-критичные изменения требуют явной трассировки |
| `k8s-provider-abstraction` | Инвариантные правила, влияющие на prompt constraints |

## Ресурсы

| Ресурс | Путь | Назначение |
|---|---|---|
| **Prompt-файлы** | `docs/ai-agent-prompts/*.md` | Затронутые файлы для версионирования |
| **Meta-prompt** | `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md` | Source of truth constraints |
| **Registry schema** | `docs/ai-agent-prompts/registry.yaml` | Метаданные prompt-файлов |
| **README registry** | `docs/ai-agent-prompts/README.md` | Реестр версий |
| **Скрипт проверки версий** | `scripts/check-prompt-versions.sh` | Валидация версий в header/footer |
| **Скрипт drift detection** | `scripts/check-prompt-drift.sh` | Обнаружение расхождений |
| **Скрипт legacy check** | `scripts/check-prompt-legacy-refs.sh` | Anti-legacy валидация |
| **Официальная документация** | `docs/official_document/` | **READ-ONLY** эталон |

---

## Шаг 0: Discovery

### 0.1. Собрать затронутые файлы

```bash
ls -1 docs/ai-agent-prompts/*.md
ls -1 docs/ai-agent-prompts/meta-promptness/*.md
```

### 0.2. Зафиксировать версии до изменения

```bash
for f in docs/ai-agent-prompts/*.md docs/ai-agent-prompts/meta-promptness/*.md; do
  [[ "$(basename "$f")" == "README.md" ]] && continue
  grep -m1 -E '^\*\*(Version|Версия|Prompt Version)' "$f" | sed "s|^|$(basename "$f"): |"
done
# Также зафиксировать состояние registry.yaml, если он существует
if [ -f docs/ai-agent-prompts/registry.yaml ]; then
  cat docs/ai-agent-prompts/registry.yaml
fi
```

---

## Шаг 1: Context7 исследование (ОБЯЗАТЕЛЬНО)

Подтверди практики:
- semantic versioning policy design
- документационные quality gates, включая Gates A-H
- PR checklist policy automation

Используй Context7 как источник практик и адаптируй под constraints .

---

## Шаг 2: Классификация изменений для version bump

### 2.1. PATCH bump (X.Y.Z → X.Y.Z+1)

Применять, если изменения:
- правки wording/формулировок без изменения смысла
- опечатки, grammar, стиль
- обновление примеров без изменения workflow
- синхронизация дат/ссылок/описаний без изменения требований

### 2.2. MINOR bump (X.Y.Z → X.(Y+1).0)

Применять, если изменения:
- добавлены новые шаги workflow
- добавлены новые обязательные секции
- расширены проверки/чеклисты/acceptance criteria
- добавлены новые сценарии использования при обратной совместимости

### 2.3. MAJOR bump (X.Y.Z → (X+1).0.0)

Применять, если изменения:
- меняют output contract (несовместимый формат результата)
- удаляют или радикально меняют обязательные блоки
- ломают ожидаемый workflow chain между промптами
- вводят несовместимые требования к входам/выходам

---

## Шаг 3: Decision Table (обязательная)

| Тип изменения | Пример | Bump |
|---|---|---|
| Wording only | Переформулировка абзаца без изменения требований | PATCH |
| Structure extension | Добавлен новый mandatory шаг проверки | MINOR |
| Workflow extension | Добавлен новый обязательный stage в pipeline | MINOR |
| Output format change | Изменён обязательный формат отчёта | MAJOR |
| Contract break | Удалён обязательный раздел из каркаса | MAJOR |

---

## Шаг 4: Правило синхронного обновления версий

Для каждого промпта после выбора bump обязательно обновить одновременно:
1. Header: `**Version:** X.Y` (или X.Y.Z в рамках policy)
2. Footer: `**Prompt Version:** X.Y`
3. README registry: строка в разделе `Реестр версий промптов`
4. `registry.yaml`: обновить соответствующие поля для промпта

Дополнительно:
- Обновить `Журнал изменений README` при добавлении/существенном обновлении промпта
- Проверить frozen snapshot в `promt-sync-optimization.md` (если затронут)

---

## Шаг 5: Проверяемый PR Checklist

### 5.1. Обязательный checklist

- [ ] Определён тип изменения (wording / structure / workflow / output contract)
- [ ] Принято и задокументировано решение по bump (PATCH/MINOR/MAJOR)
- [ ] Header версия обновлена
- [ ] Footer версия обновлена
- [ ] Реестр версий в `README.md` синхронизирован
- [ ] `registry.yaml` синхронизирован с файлом и `README.md`
- [ ] Пройден `scripts/check-prompt-versions.sh`
- [ ] Пройден `scripts/check-prompt-drift.sh`
- [ ] Пройден `scripts/check-prompt-legacy-refs.sh`
- [ ] Пройдены все Quality Gates (A-H) для затронутого промпта (проверяется `test-prompts.sh`)
- [ ] Нет новых legacy-файлов/дубликатов

### 5.2. Команды проверки

```bash
make docs-prompt-version-check
make docs-prompt-drift-check
make docs-prompt-legacy-check
make docs-prompt-guard
./scripts/verify-adr-checklist.sh --summary
./scripts/test-prompts.sh # Должен быть запущен для проверки Gates A-H
```

---

## Шаг 6: Формат решения по версии

```markdown
## Versioning Decision

| File | Current | Change Type | Bump | Next | Reason |
|------|---------|-------------|------|------|--------|
| prompt-x.md | 1.2 | workflow extension | MINOR | 1.3 | added mandatory validation step |
```

---

## Шаг 7: Anti-patterns

| Anti-pattern | Почему плохо | Правильный подход |
|---|---|---|
| Повышать версию «на глаз» | Непредсказуемость и конфликты в реестре | Использовать Decision Table |
| Обновить только header | Ломается проверка version registry | Обновлять header+footer+README+registry.yaml атомарно |
| Делать MINOR за wording | Инфляция версий | PATCH для wording-only |
| Пропускать drift/legacy checks | Риск скрытых расхождений | Прогонять полный prompt guard |
| Создавать `*-v2.md` | Нарушение anti-legacy | Только in-place updates |

---

## Чеклист Versioning Policy

### Pre-flight
- [ ] Определён scope изменений
- [ ] Собраны текущие версии prompt-файлов

### During update
- [ ] Классификация изменений выполнена
- [ ] Bump определён по Decision Table
- [ ] Версии синхронно обновлены (header/footer/README/registry.yaml)

### Validation
- [ ] `make docs-prompt-version-check` PASS
- [ ] `make docs-prompt-drift-check` PASS
- [ ] `make docs-prompt-legacy-check` PASS
- [ ] `scripts/test-prompts.sh` PASS (для затронутых промптов)

### Final
- [ ] PR checklist полностью закрыт
- [ ] Нет конфликтов с source of truth

---

## Связанные промпты

| Промпт | Когда использовать |
|---|---|
| `promt-sync-optimization.md` | Системный аудит синхронизации prompt-системы |
| `promt-quality-test.md` | Функциональная QA-проверка качества выходов промптов |
| `promt-verification.md` | Проверка ADR↔код после архитектурно значимых изменений |
| `promt-index-update.md` | Обновление индекса ADR после изменений структуры |
| `prompt-registry-schema.md` | Схема `registry.yaml` |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|----------|
| 1.3 | 2026-03-15 | ADR-022: добавлена интеграция с `registry.yaml` и Quality Gates A-H. Обновлены ссылки на `test-prompts.sh`, `sync-registry.sh`. |
| 1.2 | 2026-03-06 | Добавлены секции Gate I: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`. Исправлено несоответствие версии header/footer. |
| 1.1 | 2026-02-24 | MAJOR/MINOR/PATCH классификация, sync workflow, PR checklist. |
| 1.0 | 2026-02-23 | Первая версия: базовая semver-политика. |

---

**Prompt Version:** 1.3
**Date:** 2026-03-15
**Maintainer:** @perovskikh
