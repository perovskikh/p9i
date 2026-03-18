# AI Agent Prompt: Prompt QA / Self-testing для 

**Version:** 1.2
**Date:** 2026-02-25
**Purpose:** Ввести единый operational-сценарий тестирования качества выходов промптов на фиксированных тест-кейсах с pass/fail критериями и CI-gate

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Operational |
| **Время выполнения** | 30–60 мин |
| **Домен** | QA — тестирование качества промптов |

**Пример запроса:**

> «Используя `promt-quality-test.md`, прогони фиксированные тест-кейсы
> качества prompt-output и выдай PASS/FAIL отчёт.»

**Ожидаемый результат:**
- PASS/FAIL по каждому тест-кейсу
- Общий quality score (%)
- Список FAIL с описанием gap и remediation
- CI-gate: блокировать merge если score < 80%

---

## Когда использовать

- После массового обновления промптов (Gate I migration, system evolution)
- Перед release — гарантия качества prompt-системы
- При подозрении на деградацию качества output
- После изменения source of truth (`meta-promt-adr-system-generator.md`)

> **Отличие от `promt-sync-optimization.md`:** quality-test проверяет
> **функциональный output**; sync-optimization — **структурное соответствие**.

---

## Mission Statement

Ты — AI-агент контроля качества prompt-системы .
Твоя задача — проверять качество выходов ключевых operational-промптов на стандартизированном наборе тест-кейсов,
фиксировать результат в формате pass/fail и обеспечивать регулярный запуск проверок в CI.

Этот промпт не заменяет `promt-sync-optimization.md` и не дублирует его drift/version/legacy проверки.
Он добавляет слой функциональной QA-валидации содержимого ответов: структура, обязательные секции,
целостность workflow и корректность дальнейших действий.

---

## Контракт синхронизации системы

> **Source of truth:** `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`
> При конфликте формулировок — приоритет у source of truth.

**Обязательные инварианты:**
- ADR идентифицируются по **topic slug** (номера ADR не являются первичным ключом)
- Dual-status для ADR-материалов: `## Статус решения` + `## Прогресс реализации` + `## Чеклист реализации`
- `docs/official_document/` — строго READ-ONLY
- Anti-Legacy: не создавать `PHASE_*.md`, `*_SUMMARY.md`, `*_REPORT.md`, `reports/`, `plans/`
- Update in-place: не создавать дубликаты вида `*-v2.md`, `*-new.md`, `*-final.md`
- DB schema source of truth: только `scripts/utils/init-saas-database.sql`
- Для ADR-прогресса использовать парсер: `./scripts/verify-adr-checklist.sh --topic <slug>`

---

## Назначение

Этот промпт стандартизирует Prompt QA и self-testing для ключевых сценариев:
`verification`, `consolidation`, `index-update`, `feature-add`, `feature-remove`.

## Входы

- Целевой список промптов для проверки
- Фиксированный набор тест-кейсов Prompt QA
- Критерии pass/fail по структуре и обязательным секциям
- Результаты CI/локального прогона (`make docs-prompt-guard`, prompt QA checks)

## Выходы

- QA-отчёт по каждому кейсу и каждому промпту (PASS/FAIL + причина)
- Сводный статус готовности prompt-системы к использованию
- Список корректирующих действий (in-place)
- CI-ready рекомендации по регулярному прогону

## Ограничения / инварианты

- Не менять `docs/official_document/` и другие read-only зоны
- Не подменять drift/version/legacy проверки, а дополнять их
- Не создавать новые ADR без необходимости (QA-промпт в первую очередь operational)
- Все изменения документации выполнять in-place
- При структурных изменениях промптов обновлять реестр в `docs/ai-agent-prompts/README.md`

## Workflow шаги

1. Discovery: собрать целевые промпты и baseline качества
2. Context7 Gate: подтвердить актуальные практики QA/CI для используемых инструментов
3. Test Case Execution: прогнать фиксированные сценарии по каждому промпту
4. Scoring: применить pass/fail критерии и вычислить итоговый verdict
5. Remediation: сформировать список доработок (минимальные in-place изменения)
6. CI Integration: проверить регулярный запуск в CI и корректность гейтов
7. Reporting: выпустить стандартизированный Prompt QA Report

## Проверки / acceptance criteria

- Для каждого целевого промпта есть не менее 1 тест-кейса каждого типа (structure, required sections, workflow)
- Все fail-результаты содержат воспроизводимую причину и точку исправления
- Результат QA не противоречит source of truth
- QA-сценарий запускается регулярно (CI/manual schedule) и даёт машинопроверяемый статус

## Связи с другими промптами

- До: `promt-sync-optimization.md` (или параллельно с ним)
- После: `promt-verification.md` / `promt-index-update.md` при архитектурных изменениях

---

## Project Context

### О проекте (Prompt QA домен)

**** — multi-tenant SaaS (Telegram Bot → YooKassa → Kubernetes → персональный code-server).
Prompt QA здесь нужен, чтобы operational-промпты давали предсказуемые и проверяемые результаты,
а не только проходили структурные guard-проверки.

### ADR Topic Registry (релевантные topics)

> **КРИТИЧНО:** Использовать topic slug, не номера ADR.

| Topic Slug | Роль в Prompt QA |
|---|---|
| `documentation-generation` | Правила авто-генерации reference docs |
| `telegram-bot-saas-platform` | Бизнес-контекст и ограничения SaaS |
| `k8s-provider-abstraction` | Проверка корректного использования `$KUBECTL_CMD` |
| `path-based-routing` | Архитектурный инвариант маршрутизации |
| `storage-provider-selection` | Проверка environment-specific ограничений |

---

## Шаг 0: Discovery и определение охвата

### 0.1. Зафиксировать целевые промпты

Минимальный обязательный охват:
- `promt-verification.md`
- `promt-consolidation.md`
- `promt-index-update.md`
- `promt-feature-add.md`
- `promt-feature-remove.md`

Дополнительно (рекомендуется):
- `promt-sync-optimization.md`
- `promt-bug-fix.md`
- `promt-refactoring.md`

### 0.2. Подготовить baseline

```bash
make docs-prompt-guard
./scripts/check-prompt-drift.sh
./scripts/check-prompt-versions.sh
./scripts/check-prompt-legacy-refs.sh
./scripts/verify-adr-checklist.sh --summary
```

---

## Шаг 1: Context7 исследование (ОБЯЗАТЕЛЬНО)

Собери best practices для:
- prompt quality evaluation rubrics
- CI quality gates для Markdown/prompt workflows
- report schema для machine-readable результатов

Сверь применимость практик с проектными ограничениями .

---

## Шаг 2: Набор фиксированных тест-кейсов Prompt QA

### 2.1. Структура тест-кейса

Каждый кейс должен содержать:
- `id`
- `target_prompt`
- `scenario`
- `input`
- `expected_sections`
- `forbidden_patterns`
- `pass_criteria`
- `fail_examples`

### 2.2. Обязательные тест-кейсы (минимум)

| ID | Target Prompt | Сценарий | Что проверять |
|---|---|---|---|
| QA-VER-01 | `promt-verification.md` | Полная верификация ADR | Наличие sections: findings, blockers, implementation queue |
| QA-CON-01 | `promt-consolidation.md` | Консолидация дубликатов ADR | Правила merge без потери контента + topic-slug first |
| QA-IDX-01 | `promt-index-update.md` | Обновление `adr/index.md` | Корректность статусов, графа, статистики, ссылок |
| QA-ADD-01 | `promt-feature-add.md` | Добавление новой фичи | Context7 gate + ADR decision + rollout checks |
| QA-REM-01 | `promt-feature-remove.md` | Удаление функционала | Dependency/risk matrix + deprecation flow + cleanup |

### 2.3. Расширенные кейсы (рекомендуется)

| ID | Тип | Назначение |
|---|---|---|
| QA-NEG-01 | Negative | Ответ без обязательных секций должен FAIL |
| QA-NEG-02 | Negative | Legacy-ссылки как active source должны FAIL |
| QA-NEG-03 | Negative | Хардкод ADR-номеров вместо topic slug должен FAIL |
| QA-FMT-01 | Format | Проверка согласованности структуры разделов |
| QA-CI-01 | Pipeline | Проверка, что QA запускается в CI регулярно |

---

## Шаг 3: Критерии PASS/FAIL

### 3.1. Базовые правила

**PASS**, если одновременно:
1. Присутствуют все обязательные секции для конкретного сценария.
2. Нет запрещённых паттернов (legacy active refs, anti-legacy violations, read-only mutations).
3. Сохранён workflow chain (корректные «до/после» связи между промптами).
4. Для ADR-related сценариев соблюдён topic slug-first.

**FAIL**, если выполняется хотя бы одно условие:
- Пропущена обязательная секция
- Нарушен source-of-truth инвариант
- Найден запрещённый паттерн
- Результат нельзя проверить воспроизводимо

### 3.2. Формат verdict

```yaml
case_id: QA-VER-01
target_prompt: promt-verification.md
status: PASS|FAIL
score: 0-100
missing_sections: []
violations: []
notes: "краткий вывод"
```

### 3.3. Рекомендуемая шкала score

- 90-100: production-ready
- 75-89: usable with minor fixes
- 50-74: major revision needed
- <50: reject

---

## Шаг 4: Регулярный прогон в CI

### 4.1. Минимальный CI-контур

Проверяй, что в CI есть регулярный запуск (push/PR/schedule) и шаги:

```bash
make docs-prompt-guard
# + шаг Prompt QA self-testing (по этому промпту)
```

### 4.2. Требования к CI-результату

- Один агрегированный статус (`PASS` / `FAIL`)
- Артефакт отчёта (`prompt-qa-report.md` или JSON)
- Явный список failed cases
- Ненулевой exit code при FAIL

### 4.3. Fail-fast политика

- Критические нарушения (`source of truth`, `read-only`, `anti-legacy`) завершают pipeline немедленно
- Некритические нарушения могут агрегироваться в отчёт с последующим FAIL в конце шага

---

## Шаг 5: Формат итогового Prompt QA Report

```markdown
# Prompt QA Report

## Summary
- Total cases: N
- Passed: N
- Failed: N
- Pass rate: X%

## Failed Cases
| Case ID | Prompt | Reason | Action |
|---|---|---|---|

## Recommendations
- [ ] Fix ...
- [ ] Re-run ...
```

---

## Шаг 6: Remediation workflow

1. Исправить найденные нарушения **in-place** в целевом промпте.
2. При изменении версий — обновить реестр в `docs/ai-agent-prompts/README.md`.
3. Повторно запустить Prompt QA + Prompt Guard.
4. Зафиксировать закрытие кейсов в отчёте.

---

## Чеклист Prompt QA / Self-testing

### Pre-flight
- [ ] Собран список целевых промптов
- [ ] Запущен baseline (`drift`, `versions`, `legacy`)
- [ ] Подтверждён source of truth

### During execution
- [ ] Подготовлены фиксированные тест-кейсы для 5 ключевых промптов
- [ ] Определены обязательные секции и forbidden patterns
- [ ] Выполнен прогон кейсов
- [ ] Для каждого кейса сформирован verdict (PASS/FAIL + причина)

### CI integration
- [ ] Проверен регулярный запуск QA в CI
- [ ] Настроен machine-readable отчёт
- [ ] FAIL корректно роняет pipeline

### Finalization
- [ ] Сформирован итоговый Prompt QA Report
- [ ] Выполнены корректировки in-place
- [ ] Повторный прогон QA проходит без критических нарушений

---

## Anti-patterns

| Anti-pattern | Почему плохо | Правильный подход |
|---|---|---|
| Проверять только drift/version/legacy | Не ловит низкое качество выходов | Добавить functional Prompt QA cases |
| Оценивать «на глаз» без критериев | Результат не воспроизводим | Использовать явные pass/fail правила |
| Тестировать один промпт изолированно | Разрывается workflow chain | Проверять ключевые цепочки (`verification→index-update`) |
| Не публиковать отчёт в CI | Нет трассируемости | Сохранять markdown/json артефакт |
| Создавать копии промптов для правок | Порождает legacy | Обновлять in-place |

---

## Ресурсы

| Ресурс | Путь | Назначение |
|---|---|---|
| **ADR-файлы** | `docs/explanation/adr/ADR-*.md` | Проверка coverage |
| **Скрипт верификации** | `scripts/verify-all-adr.sh` | Валидация архитектуры |
| **Скрипт прогресса** | `scripts/verify-adr-checklist.sh` | Статус реализации |
| **Правила проекта** | `.github/copilot-instructions.md` | Code conventions |
| **Официальная документация** | `docs/official_document/` | **READ-ONLY** эталон |
| **Meta-prompt** | `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md` | Source of truth |

---

## Связанные промпты

| Промпт | Когда использовать |
|---|---|
| `promt-sync-optimization.md` | Базовый sync-аудит структуры prompt-системы |
| `promt-verification.md` | Проверка ADR ↔ code после архитектурных изменений |
| `promt-consolidation.md` | Консолидация ADR при выявленных дубликатах |
| `promt-index-update.md` | Обновление `docs/explanation/adr/index.md` после изменений |
| `promt-feature-add.md` | Добавление нового функционала |
| `promt-feature-remove.md` | Безопасная депрекация/удаление функционала |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|----------|
| 1.2 | 2026-03-06 | Добавлены секции Gate I: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`. |
| 1.1 | 2026-02-25 | Добавлены фиксированные тест-кейсы, PASS/FAIL критерии, CI-gate. |
| 1.0 | 2026-02-24 | Первая версия: prompt QA/self-testing framework. |

---

**Prompt Version:** 1.2
**Date:** 2026-03-06
**Maintainer:** @perovskikh
**Date:** 2026-02-24
