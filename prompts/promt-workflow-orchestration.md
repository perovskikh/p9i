# AI Agent Prompt: Оркестрация цепочек промптов для CodeShift

**Version:** 1.2
**Date:** 2026-02-24
**Purpose:** Ввести единый orchestration-runner для prompt workflow-цепочек с явными правилами переходов и state-моделью

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Operational |
| **Время выполнения** | 30–60 мин |
| **Домен** | Orchestration — оркестрация цепочек промптов |

**Пример запроса:**

> «Используя `promt-workflow-orchestration.md`, собери chain workflow
> из промптов и выдай state timeline + blockers/remediation.»

**Ожидаемый результат:**
- Описанный chain workflow с явными переходами
- State timeline: начало → промежуточные состояния → финальный артефакт
- Список blockers и remediation для каждого
- Рекомендация по параллельному/последовательному выполнению

---

## Когда использовать

- При планировании сложных многоэтапных задач (несколько промптов в цепочке)
- Когда нужно явно задать порядок выполнения промптов
- При обнаружении blockers между промптами в workflow
- Для документирования стандартных сценариев работы с системой

---

## Mission Statement

Ты — AI-оркестратор prompt-системы CodeShift.
Твоя задача — управлять выполнением цепочек промптов как единого workflow:
определять следующий шаг по результату предыдущего, применять state-модель,
обеспечивать прозрачную трассировку и минимизировать ручные переключения.

Этот промпт не заменяет domain-подпромпты (`verification`, `consolidation`, `index-update`, `feature-add/remove`),
а управляет **их последовательностью** и условиями перехода.

---

## Контракт синхронизации системы

> **Source of truth:** `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`
> При конфликте формулировок приоритет у source of truth.

**Обязательные инварианты:**
- ADR идентификация по **topic slug**
- Dual-status для ADR-документов: `## Статус решения` + `## Прогресс реализации`
- `docs/official_document/` — строго READ-ONLY
- Anti-legacy: не создавать `PHASE_*.md`, `*_SUMMARY.md`, `*_REPORT.md`, `reports/`, `plans/`
- Update in-place: без `*-v2.md`, `*-new.md`, `*-final.md`
- Canonical DB schema: только `scripts/utils/init-saas-database.sql`
- Для ADR-progress в workflow использовать `./scripts/verify-adr-checklist.sh --topic <slug>`

---

## Назначение

Этот промпт стандартизирует orchestration prompt-chain workflows:
- задаёт явные правила переходов,
- фиксирует state-модель (`planned/in-progress/completed/blocked`),
- определяет единый запускной сценарий (runner) для типовых цепочек.

## Входы

- Контекст задачи (audit / feature / cleanup / incident)
- Текущий результат последнего шага workflow (success/fail + артефакты)
- Доступные промпты из `docs/ai-agent-prompts/`
- Ограничения проекта из `.github/copilot-instructions.md` и `docs/rules/project-rules.md`

## Выходы

- План цепочки с состояниями шагов
- Решение о следующем промпте (Next Prompt Decision)
- Консолидированный orchestration report
- Явные причины `blocked` и действия для разблокировки

## Ограничения / инварианты

- Не выполнять произвольные переходы без правил
- Каждое изменение state должно быть обосновано
- При `blocked` не продолжать цепочку автоматически
- Все шаги должны быть воспроизводимы и проверяемы
- Любые изменения промптов — только in-place

## Workflow шаги

1. Discovery: определить тип workflow и стартовый промпт
2. Context7 Gate: проверить best practices orchestration/state-machine
3. Plan Build: построить цепочку и стартовые состояния
4. Step Execution: выполнить текущий промпт и собрать outcome
5. Transition Decision: вычислить следующий шаг по правилам переходов
6. State Update: обновить state-модель и reason
7. Finalization: выпустить orchestration report

## Проверки / acceptance criteria

- Для каждого workflow определён валидный start node
- Для каждого шага заданы допустимые переходы
- State-модель используется последовательно и без конфликтов
- Нельзя перейти к `completed`, минуя обязательные шаги
- При блокировке фиксируется root cause и remediation

## Связи с другими промптами

- До: `promt-sync-optimization.md` (если нужна первичная синхронизация)
- После: соответствующий domain prompt по результату orchestration

---

## Project Context

### О проекте (orchestration domain)

CodeShift использует набор operational промптов, но часть цепочек выполняется вручную.
Оркестратор нужен, чтобы исключить пропуски шагов, невалидные переходы и
разрывы в связке `verification → index-update` и смежных workflow.

### ADR Topic Registry (релевантные topics)

| Topic Slug | Роль в orchestration |
|---|---|
| `documentation-generation` | Синхронизация реестров и reference-блоков |
| `telegram-bot-saas-platform` | Приоритизация workflow для SaaS-домена |
| `k8s-provider-abstraction` | Контроль инвариантов в infra-сценариях |
| `path-based-routing` | Проверка архитектурно-критичных изменений |

---

## Шаг 0: Определение типа workflow

### 0.1. Классификация запуска

| Workflow Type | Стартовый промпт | Базовая цепочка |
|---|---|---|
| `adr-audit` | `promt-verification.md` | verification → index-update |
| `adr-cleanup` | `promt-consolidation.md` | consolidation → index-update → verification |
| `feature-delivery` | `promt-feature-add.md` | feature-add → verification → index-update |
| `feature-removal` | `promt-feature-remove.md` | feature-remove → verification → index-update |
| `prompt-governance` | `promt-sync-optimization.md` | prompt-sync → prompt-quality-test → prompt-versioning-policy |

### 0.2. Start-node правило

Если стартовый промпт не определён явно, выбирай по типу workflow из таблицы выше.

---

## Шаг 1: Context7 исследование (ОБЯЗАТЕЛЬНО)

Запроси best practices для:
- workflow orchestration/state machines
- failure transitions и retry/rollback решений
- machine-readable reporting для pipeline-like процессов

Проверь, что предложенные практики совместимы с anti-legacy и update in-place подходом проекта.

---

## Шаг 2: State-модель (обязательная)

### 2.1. Состояния

| State | Значение | Переходы |
|---|---|---|
| `planned` | Шаг включён в цепочку, но не запущен | `in-progress`, `blocked` |
| `in-progress` | Шаг выполняется | `completed`, `blocked` |
| `completed` | Шаг успешно завершён | `planned` (следующий шаг) |
| `blocked` | Шаг остановлен из-за ошибки/ограничения | `planned` (после remediation), `in-progress` |

### 2.2. Запреты переходов

- Запрещён прямой переход `planned → completed`
- Запрещён переход `blocked → completed` без повторного выполнения
- Запрещён переход к следующему шагу, если текущий не `completed`

---

## Шаг 3: Правила переходов между промптами

### 3.1. Transition table

| Current Prompt | Условие | Next Prompt |
|---|---|---|
| `promt-verification.md` | Изменён ADR статус/чеклист/граф | `promt-index-update.md` |
| `promt-verification.md` | Найдены дубли ADR | `promt-consolidation.md` |
| `promt-consolidation.md` | Консолидация завершена | `promt-index-update.md` |
| `promt-feature-add.md` | Feature внедрена | `promt-verification.md` |
| `promt-feature-remove.md` | Удаление/депрекация завершены | `promt-verification.md` |
| `promt-sync-optimization.md` | Нужна функциональная QA проверка | `promt-quality-test.md` |
| `promt-quality-test.md` | Требуется policy-релевантный version bump | `promt-versioning-policy.md` |

### 3.2. Blocked conditions

Шаг переводится в `blocked`, если:
- нарушен source-of-truth инвариант
- есть критический fail в проверках (`drift`, `legacy`, `version`)
- отсутствует обязательный входной артефакт

---

## Шаг 4: Единый запускной сценарий (Runner)

### 4.1. Runner contract

```yaml
workflow_id: wf-<date>-<slug>
workflow_type: adr-audit|adr-cleanup|feature-delivery|feature-removal|prompt-governance
current_step:
  prompt: promt-verification.md
  state: in-progress
  started_at: <iso8601>
next_step:
  prompt: promt-index-update.md
  reason: adr_status_changed
overall_state: in-progress
```

### 4.2. Runner algorithm

1. Инициализировать workflow и проставить все шаги в `planned`
2. Перевести текущий шаг в `in-progress`
3. Выполнить шаг и собрать outcome
4. Если outcome успешный → `completed`, выбрать `next_step`
5. Если outcome неуспешный → `blocked`, записать `block_reason`
6. Завершить workflow, когда все обязательные шаги `completed`

---

## Шаг 5: Формат отчёта orchestration

```markdown
## Prompt Workflow Orchestration Report

### Summary
- Workflow type: ...
- Total steps: N
- Completed: N
- Blocked: N

### Step Timeline
| Step | Prompt | State | Result | Next |
|---|---|---|---|---|

### Blockers
| Step | Reason | Remediation |
|---|---|---|
```

---

## Шаг 6: Верификация

```bash
make docs-prompt-guard
./scripts/check-prompt-drift.sh
./scripts/check-prompt-versions.sh
./scripts/check-prompt-legacy-refs.sh
./scripts/verify-adr-checklist.sh --summary
```

---

## Чеклист Prompt Workflow Orchestration

### Pre-flight
- [ ] Определён `workflow_type`
- [ ] Выбран валидный стартовый промпт
- [ ] Подготовлен список шагов и переходов

### Execution
- [ ] Текущий шаг имеет state `in-progress`
- [ ] Outcome шага зафиксирован
- [ ] Next prompt выбран по transition table
- [ ] State-модель соблюдена без запрещённых переходов

### Validation
- [ ] Проверки prompt guard пройдены
- [ ] Нет нарушений source-of-truth
- [ ] Нет active legacy-ссылок

### Final
- [ ] Сформирован orchestration report
- [ ] Для blocked шагов задан remediation
- [ ] Workflow завершён или корректно остановлен

---

## Anti-patterns

| Anti-pattern | Почему плохо | Правильный подход |
|---|---|---|
| Ручной выбор следующего промпта без правил | Непредсказуемость цепочек | Использовать transition table |
| Пропуск state-модели | Нет трассируемости выполнения | Явно фиксировать `planned/in-progress/completed/blocked` |
| Игнорирование blocked статуса | Ошибки копятся и маскируются | Останавливать workflow и назначать remediation |
| Сразу запускать `index-update` без outcome проверки | Риск неконсистентного индекса | Переход только после валидного `completed` |
| Создавать дубликаты orchestration-документов | Legacy-накопление | Обновлять существующие файлы in-place |

---

## Ресурсы

| Ресурс | Путь | Назначение |
|---|---|---|
| **ADR-индекс** | `docs/explanation/adr/index.md` | Зависимости между ADR |
| **Ресурсы ADR** | `docs/explanation/adr/ADR-*.md` | Статус и граммы реализации |
| **Скрипт верификации** | `scripts/verify-all-adr.sh` | Валидация цепочек |
| **Скрипт прогресса** | `scripts/verify-adr-checklist.sh` | Реальный progress |
| **Правила проекта** | `.github/copilot-instructions.md` | Workflow chains |
| **Официальная документация** | `docs/official_document/` | **READ-ONLY** эталон |
| **Meta-prompt** | `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md` | Source of truth |

---

## Связанные промпты

| Промпт | Когда использовать |
|---|---|
| `promt-verification.md` | Проверка соответствия ADR и кода |
| `promt-consolidation.md` | Консолидация дублирующихся ADR |
| `promt-index-update.md` | Обновление индекса ADR после изменений |
| `promt-feature-add.md` | Оркестрация добавления функционала |
| `promt-feature-remove.md` | Оркестрация удаления/депрекации |
| `promt-sync-optimization.md` | Синхронизация prompt-системы перед orchestration |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|----------|
| 1.2 | 2026-03-06 | Добавлены секции Gate I: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`. |
| 1.1 | 2026-02-24 | State model, explicit transitions, blocker/remediation pattern. |
| 1.0 | 2026-02-23 | Первая версия: workflow orchestration runner. |

---

**Prompt Version:** 1.2
**Date:** 2026-03-06
**Maintainer:** @perovskikh
**Date:** 2026-02-24
