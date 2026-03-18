# AI Agent Prompts для управления ADR и эволюции проекта

**Версия документа:** 1.59
**Совместимость:** >= v0.8.0
**Последнее обновление:** 2026-03-13

Эта директория содержит промпты для AI-агентов, которые автоматизируют верификацию,
синхронизацию и эволюцию Architecture Decision Records (ADR) с кодом проекта,
а также управление жизненным циклом функционала.

> Вся документация по каждому промпту находится **внутри файла промпта** (секции
> `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`).
> README — только индекс-навигатор.

---

## Единая точка управления

Система промптов управляется из одного файла:
- `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`

Операционный аудит синхронизации (CI-ready):
- `docs/ai-agent-prompts/promt-sync-optimization.md`

> **Разграничение:** meta-prompt — **конституция** (определяет архитектуру и constraints);
> prompt-sync — **аудитор** (проверяет соответствие и генерирует Sync Report).

**Порядок запуска (стандартный поток):**
1. `meta-promt-adr-system-generator.md` — сначала (задаёт правила)
2. `promt-sync-optimization.md` — после (проверяет соответствие правилам)

**Исключение — эволюция системы** (обнаружена системная рассинхронизация):
1. `promt-sync-optimization.md` → получить Sync Report с gap
2. Обновить `meta-promt-adr-system-generator.md` (зафиксировать новые правила)
3. Снова `promt-sync-optimization.md` → применить правила ко всем промптам

Базовые инварианты всей системы:
- ADR идентифицируются по **topic slug** (номера ADR вторичны и могут меняться)
- Используется dual-status: `## Статус решения` + `## Прогресс реализации`
- Перед архитектурными действиями выполняется Context7 gate
- Для схемы БД используется только `scripts/utils/init-saas-database.sql`
- `docs/official_document/` всегда READ-ONLY

Генераторы промптов (фабрики):
- **CodeShift-специфичные:** `meta-promptness/meta-promt-prompt-generation.md`
- **Universal (project-agnostic):** `meta-promptness/meta-promt-universal-prompt-generator.md`

---

## Шаблоны запросов и навигация по всей системе

Ниже — готовые формулировки в формате «скопировал-вставил».

**Универсальный шаблон запроса:**

> «Используя `<имя-подходящего-промпта>.md`, выполни задачу: `<кратко цель>`.
> Ограничения: `<инварианты>`. Ожидаемый результат: `<артефакты и проверки>`.»

### 1) Meta-промпты (управление системой правил)

| Сценарий | Что запускать | Готовая формулировка запроса |
|---|---|---|
| Изменить глобальные правила prompt-системы | `meta-promt-adr-system-generator.md` | «Используя `meta-promt-adr-system-generator.md`, обнови системные инварианты prompt-системы по требованиям: … Сохрани совместимость с topic slug-first, dual-status, Context7 gate, READ-ONLY `docs/official_document/`. Выдай список изменённых файлов и проверок.» |
| Создать / обновить операционный промпт (CodeShift) | `meta-promt-prompt-generation.md` | «Используя `meta-promt-prompt-generation.md`, сгенерируй/обнови промпт `<name>.md` по требованиям: … Пройди workflow `Discovery → Тип → Context7 → Сборка по скелету → Валидация → Регистрация` и обнови реестр в README.» |
| Создать / обновить универсальный промпт | `meta-promt-universal-prompt-generator.md` | «Используя `meta-promt-universal-prompt-generator.md`, создай project-agnostic промпт `<name>.md` для работы с любым проектом по требованиям: …» |
| Сгенерировать Sync/Init промпты по структуре v3.0 | `meta-promt-sync-init-generator.md` | «Используя `meta-promt-sync-init-generator.md`, сгенерируй или обнови промпты `promt-agent-init.md`, `promt-project-rules-sync.md`, `promt-readme-sync.md` по самодокументирующейся структуре фабрики v3.0.» |
| Изменить только логику planner-промпта | `meta-promt-adr-implementation-planner.md` | «Используя `meta-promt-adr-implementation-planner.md`, обнови `promt-adr-implementation-planner.md` под новые требования планирования: … Сохрани Critical Path, Layer 0→5 и Context7 gate.» |
| Инициализация AI-агента | `promt-agent-init.md` | «Используя `promt-agent-init.md`, выполни обязательную инициализацию агента: загрузи контекст, зафиксируй состояние ADR, выбери промпт для задачи и задекларируй инварианты.» |

### 2) Операционные промпты (рабочие задачи)

| Цель | Промпт | Готовая формулировка запроса |
|---|---|---|
| Полная верификация ADR↔код | `promt-verification.md` | «Используя `promt-verification.md`, выполни полную верификацию ADR↔код, построй очередь внедрения и дай итоговый отчёт с блокерами и приоритетами.» |
| Консолидация ADR | `promt-consolidation.md` | «Используя `promt-consolidation.md`, найди и объедини дублирующиеся ADR без потери контента, затем обнови связи и очередь внедрения.» |
| Обновление ADR index | `promt-index-update.md` | «Используя `promt-index-update.md`, регенерируй `docs/explanation/adr/index.md`, статистику и Mermaid-граф после последних изменений ADR.» |
| Добавление функционала | `promt-feature-add.md` | «Используя `promt-feature-add.md`, исследуй best practices (Context7), прими ADR-решение и добавь функционал: … с верификацией после изменений.» |
| Расширение ADR идеями из how-to / документа | `promt-feature-add.md` | «Используя `promt-feature-add.md`, проверь каждую идею из `<источник>` по 4 критериям (корректность ADR, реализуемость в стеке, согласованность с другими ADR, полнота обоснования) и расширь ADR `<topic-slug>` одобренными идеями; обнови `Прогресс реализации` и `index.md`.» |
| Удаление / депрекация функционала | `promt-feature-remove.md` | «Используя `promt-feature-remove.md`, безопасно удали/задепрекируй функционал: … с анализом зависимостей, рисков и ADR-обновлениями.» |
| Миграция ADR к dual-status | `promt-adr-template-migration.md` | «Используя `promt-adr-template-migration.md`, выполни batch-миграцию ADR к dual-status шаблону и синхронизируй индекс/очередь.» |
| План реализации ADR | `promt-adr-implementation-planner.md` | «Используя `promt-adr-implementation-planner.md`, построй приоритизированный план реализации ADR по Critical Path и слоям Layer 0→5.» |
| Исправление дефекта | `promt-bug-fix.md` | «Используя `promt-bug-fix.md`, диагностируй и исправь баг: … проверь связь с ADR и обнови релевантные чеклисты.» |
| Рефакторинг | `promt-refactoring.md` | «Используя `promt-refactoring.md`, выполни рефакторинг без изменения функциональности, с baseline-проверками до/после.» |
| Security аудит | `promt-security-audit.md` | «Используя `promt-security-audit.md`, проведи аудит безопасности по компонентам: … и выдай приоритизированный remediation plan.» |
| Управление baseline SQL | `promt-db-baseline-governance.md` | «Используя `promt-db-baseline-governance.md`, внеси изменения в `scripts/utils/init-saas-database.sql`, синхронизируй модели и проверь безопасность SQL.» |
| CI/CD pipeline | `promt-ci-cd-pipeline.md` | «Используя `promt-ci-cd-pipeline.md`, проанализируй и оптимизируй CI/CD workflow: … с измеримым эффектом и списком рисков.» |
| Онбординг | `promt-onboarding.md` | «Используя `promt-onboarding.md`, составь onboarding-план для роли `<Bot/DevOps/Full-stack>` с файлами, командами и FAQ.» |
| Prompt Sync аудит | `promt-sync-optimization.md` | «Используя `promt-sync-optimization.md`, выполни аудит синхронизации prompt-системы и выдай Sync Report с gap, severity и remediation.» |
| Prompt QA/self-test | `promt-quality-test.md` | «Используя `promt-quality-test.md`, прогони фиксированные тест-кейсы качества prompt-output и выдай PASS/FAIL отчёт.» |
| Prompt versioning policy | `promt-versioning-policy.md` | «Используя `promt-versioning-policy.md`, классифицируй изменения и предложи корректный semver bump с чеклистом для PR.» |
| Prompt workflow orchestration | `promt-workflow-orchestration.md` | «Используя `promt-workflow-orchestration.md`, собери chain workflow из промптов и выдай state timeline + blockers/remediation.» |
| Prompt Sync экспорт | `promt-sync-report-export.md` | «Используя `promt-sync-report-export.md`, сформируй machine-readable Sync Report (`.md` + `.json`) в `artifacts/prompt-sync/`.» |
| Синхронизация copilot-instructions и project-rules | `promt-copilot-instructions-update.md` | «Используя `promt-copilot-instructions-update.md`, синхронизируй `.github/copilot-instructions.md` и `docs/rules/project-rules.md` с текущими ADR topic slug и инвариантами проекта.» |
| Эволюция prompt-системы | `promt-system-evolution.md` | «Используя `promt-system-evolution.md`, внеси системные изменения в prompt-систему: `<scope>`, с каскадной миграцией и финальным quality gate A–J.» |
| Рефакторинг документации 2026 | `promt-documentation-refactoring-standards-2026.md` | «Используя `promt-documentation-refactoring-standards-2026.md`, выполни системный аудит и план рефакторинга документации по стандартам 2026 с Diátaxis scorecard и проверками через make-команды.» |
| Качественное сжатие документации | `promt-documentation-quality-compression.md` | «Используя `promt-documentation-quality-compression.md`, выполни качественное сжатие `<целевой документ>` — удали дублирование и избыточность, сохрани все инварианты, сформируй Protected Content Registry.» |
| Project Stack & Status Dump (Universal) | `promt-project-stack-dump.md` | «Используя `promt-project-stack-dump.md`, быстро и полностью опиши текущее состояние любого проекта: стек, архитектуру, задачи, прогресс и roadmap для onboarding и стратегического планирования.» |
| MVP / Baseline генератор (Universal) | `promt-mvp-baseline-generator-universal.md` | «Используя `promt-mvp-baseline-generator-universal.md`, проанализируй любой проект и сгенерируй чёткий, реалистичный MVP или Baseline документ с Must/Should/Could/Won't, Critical Path, Technical Baseline, AC и Roadmap.» |
| Адаптация к проекту по MVP/Baseline (Universal) | `promt-project-adaptation.md` | «Используя `promt-project-adaptation.md`, адаптируй меня под текущий проект по файлу MVP.md / BASELINE.md: 7-step workflow, маппинг к коду, выявление gaps, onboarding-чеклист и Adaptation Report с Next 5 Steps.» |
| Синхронизация реестра промптов (README) | `promt-readme-sync.md` | «Используя `promt-readme-sync.md`, проверь актуальность навигационной таблицы README: все промпты зарегистрированы, версии совпадают с файлами, нет строк для несуществующих файлов.» |
| Аудит и исправление project-rules.md | `promt-project-rules-sync.md` | «Используя `promt-project-rules-sync.md`, выполни аудит `docs/rules/project-rules.md`: замени ADR-XXX на topic slugs, добавь раздел AI Instructions Sync Rules, восстанови раздел «Рабочие процессы».» |

### 3) Как выбрать промпт за 30 секунд (decision tree)

Ответь на вопросы сверху вниз:

1. Нужны изменения в **правилах всей prompt-системы**?
   - Да → `meta-promt-adr-system-generator.md`
2. Нужен **новый промпт** или обновление одного существующего?
   - CodeShift-специфичный → `meta-promt-prompt-generation.md`
   - Universal (project-agnostic) → `meta-promt-universal-prompt-generator.md`
3. Нужна **верификация ADR↔код**?
   - Да → `promt-verification.md`
4. Нужны **консолидация/дедупликация ADR**?
   - Да → `promt-consolidation.md`
5. Нужен **план реализации ADR**?
   - Да → `promt-adr-implementation-planner.md`
6. Задача про **добавление/удаление фичи**?
   - Добавить → `promt-feature-add.md`
   - Удалить/депрекировать → `promt-feature-remove.md`
7. Нужен **аудит/синхронизация prompt-системы**?
   - Аудит → `promt-sync-optimization.md`
   - QA кейсы → `promt-quality-test.md`
   - Оркестрация цепочки → `promt-workflow-orchestration.md`
8. Нужны **системные изменения в prompt-системе** (скелет, домены, депрекация, каскад)?
   - Да → `promt-system-evolution.md`
9. Нужно **быстро описать проект и его состояние** (стек, задачи, progress, roadmap)?
   - Да → `promt-project-stack-dump.md`
10. Нужен **MVP или Baseline документ для любого проекта**?
    - Да → `promt-mvp-baseline-generator-universal.md` (после project-stack-dump)
11. Нужно **адаптировать AI-агента / новый промпт к текущему проекту** по MVP/Baseline файлу?
    - Да → `promt-project-adaptation.md` (7-step onboarding с маппингом к коду)
12. Нужно **расширить ADR идеями из внешнего документа** (how-to, спецификации, design doc)?
    - Да → `promt-feature-add.md` (с анализом по 4 критериям)

**Top 3-prompt workflow для быстрого старта в любом проекте:**
```
1. promt-project-stack-dump.md          # Шаг 1: Полный дамп состояния
   ↓
2. promt-mvp-baseline-generator.md      # Шаг 2: Генерация MVP/Baseline
   ↓
3. promt-project-adaptation.md          # Шаг 3: Адаптация + Onboarding
   ↓
   [Ready to work: код, PR, backlog]
```

---

### 4) Рекомендуемый порядок для любых изменений

1. Выбрать промпт из таблиц выше (или через decision tree).
2. Сформулировать задачу в шаблоне «Используя `<prompt>.md`, …».
3. Зафиксировать expected output: какие файлы должны быть обновлены.
4. После выполнения прогнать guards:
   - `make docs-prompt-guard`
   - `make docs-check-mkdocs-nav`
5. При изменении состава/версий промптов — обновить этот README.

### 4.1) Порядок промптов для специфичных сценариев

#### Сценарий 1: Добавили новый ADR целиком (вручную или через feature-add)

```
1. promt-index-update.md
   └─ Обновить index.md: добавить новый ADR в таблицу, граф, статистику
   └─ Пересчитать очередь внедрения

2. promt-verification.md
   └─ Проверить структуру нового ADR (dual-status, чеклист)
   └─ Проверить соответствие коду (если есть реализация)
   └─ Убедиться, что граф зависимостей верный

3. promt-adr-implementation-planner.md (опционально)
   └─ Если нужен детальный план реализации нового ADR

4. Guards (ОБЯЗАТЕЛЬНО):
   ├─ make docs-prompt-guard
   └─ make docs-check-mkdocs-nav
```

#### Сценарий 2: Feature + новый ADR (через promt-feature-add)

```
1. promt-feature-add.md
   └─ Добавить функциональность И СОЗДАТЬ новый ADR в одном промпте

2. promt-index-update.md
   └─ Регенерировать index.md с новым ADR

3. promt-verification.md
   └─ Полная верификация: код ↔ ADR ↔ граф

4. Guards:
   ├─ make docs-prompt-guard
   ├─ make docs-check-mkdocs-nav
   └─ make test
```

#### Сценарий 3: Слияние существующих ADR (через promt-consolidation)

```
1. promt-consolidation.md
   └─ Объединить дублирующиеся ADR

2. promt-index-update.md
   └─ Обновить индекс (удалить старые, добавить новый merged)

3. promt-verification.md
   └─ Проверить целостность после consolidation

4. Guards:
   ├─ make docs-prompt-guard
   └─ make docs-check-mkdocs-nav
```

#### Сценарий 4: Просто добавили ADR-файл (минимум)

```
1. promt-index-update.md
   └─ Обновить index.md

2. make docs-prompt-guard
   └─ Проверить структуру ADR
```

#### Сценарий 5: Сжатие документации project-rules.md

```
1. promt-documentation-refactoring-standards-2026.md
   └─ Аудит структуры, Diátaxis scorecard, план сжатия с целевыми метриками

2. promt-documentation-quality-compression.md
   └─ Качественное сжатие на основе плана аудита: Protected Content Registry + обоснование каждого изменения

3. promt-verification.md
   └─ Проверка ADR↔код соответствия после изменений

4. Guards (ОБЯЗАТЕЛЬНО):
   ├─ make docs-prompt-guard
   └─ make docs-check-mkdocs-nav
```

#### Сценарий 6: Сборка полной AI-системы с нуля

```
ФАЗА 1 — ИНИЦИАЛИЗАЦИЯ
1. promt-agent-init.md
   └─ Загрузить контекстные файлы, зафиксировать ADR pass rate
   └─ Задекларировать инварианты, выбрать промпт по decision tree

2. promt-project-stack-dump.md
   └─ Получить полный baseline: стек, архитектура, ADR-прогресс, roadmap

ФАЗА 2 — АУДИТ
3. promt-verification.md
   └─ Полная верификация ADR↔код, Mermaid-граф, Critical Path, блокеры

4. promt-index-update.md
   └─ Регенерировать index.md с актуальными статусами и графом

5. promt-sync-optimization.md
   └─ Аудит prompt-системы: drift, версии, legacy, Sync Report

ФАЗА 3 — ПЛАНИРОВАНИЕ И РЕАЛИЗАЦИЯ
6. promt-adr-implementation-planner.md
   └─ Приоритизированный план по Layer 0→5, очередь спринтов

7. promt-feature-add.md / promt-bug-fix.md / promt-refactoring.md
   └─ Выбрать один по задаче, выполнить с Context7 и ADR-обновлением

8. promt-verification.md + promt-index-update.md
   └─ Верификация после изменений, обновление index.md

ФАЗА 4 — СИНХРОНИЗАЦИЯ ДОКУМЕНТАЦИИ
9. promt-copilot-instructions-update.md
   └─ Синхронизировать .github/copilot-instructions.md и project-rules.md

10. promt-project-rules-sync.md
    └─ Аудит project-rules.md: topic slugs, AI Sync Rules, раздел «Рабочие процессы»

11. promt-readme-sync.md
    └─ Проверить навигационную таблицу README: версии, добавить/убрать строки

12. promt-quality-test.md
    └─ QA-проверка ключевых промптов, PASS/FAIL отчёт

Guards (ОБЯЗАТЕЛЬНО после каждой фазы):
   ├─ make docs-prompt-guard
   └─ make docs-check-mkdocs-nav
```

**Шпаргалка по ситуациям:**

| Ситуация | Минимальный набор |
|---|---|
| Начало сессии | `promt-agent-init.md` |
| Первый запуск проекта | Фазы 1+2 полностью |
| Добавить фичу | `agent-init` → `feature-add` → `verification` → `index-update` |
| Исправить баг | `agent-init` → `bug-fix` → `verification` |
| Ревью архитектуры | `verification` → `adr-implementation-planner` |
| Онбординг нового разработчика | `project-stack-dump` → `mvp-baseline-generator-universal` → `project-adaptation` |
| Раз в спринт | `verification` → `index-update` → `sync-optimization` |
| После массовых изменений | Фазы 2+4 полностью |

---

### 5) Post-rename runbook (после массовых rename/update операций)

1. Прогнать Source of Truth: `meta-promt-adr-system-generator.md`
2. Прогнать синхронизационный аудит: `promt-sync-optimization.md`
3. Прогнать функциональный QA: `promt-quality-test.md`
4. Подтвердить версионирование и реестр: `promt-versioning-policy.md`
5. Экспортировать машинно-читаемый отчёт (опционально): `promt-sync-report-export.md`

Рекомендуемые команды проверки:
- `make docs-prompt-guard`
- `make docs-check-mkdocs-nav`
- `make docs-prompt-version-check`

---

## Реестр версий промптов

| Тип | Файл | Версия |
|-----|------|--------|
| Meta | `meta-promptness/meta-promt-adr-system-generator.md` | 2.4 |
| Meta | `meta-promptness/meta-promt-adr-implementation-planner.md` | 2.1 |
| Meta | `meta-promptness/meta-promt-prompt-generation.md` | 3.0 |
| Meta | `meta-promptness/meta-promt-universal-prompt-generator.md` | 1.1 |
| Meta | `meta-promptness/meta-promt-sync-init-generator.md` | 1.0 |
| Operational | `promt-agent-init.md` | 1.0 |
| Operational | `promt-verification.md` | 3.4 |
| Operational | `promt-consolidation.md` | 2.5 |
| Operational | `promt-index-update.md` | 2.6 |
| Operational | `promt-feature-add.md` | 1.5 |
| Operational | `promt-feature-remove.md` | 1.5 |
| Operational | `promt-adr-template-migration.md` | 1.4 |
| Operational | `promt-adr-implementation-planner.md` | 2.3 |
| Operational | `promt-bug-fix.md` | 1.2 |
| Operational | `promt-refactoring.md` | 1.2 |
| Operational | `promt-security-audit.md` | 1.2 |
| Operational | `promt-db-baseline-governance.md` | 1.2 |
| Operational | `promt-ci-cd-pipeline.md` | 1.2 |
| Operational | `promt-onboarding.md` | 1.2 |
| Operational | `promt-sync-optimization.md` | 1.8 |
| Operational | `promt-quality-test.md` | 1.2 |
| Operational | `promt-versioning-policy.md` | 1.2 |
| Operational | `promt-workflow-orchestration.md` | 1.2 |
| Operational | `promt-sync-report-export.md` | 1.2 |
| Operational | `promt-copilot-instructions-update.md` | 2.1 |
| Operational | `promt-system-evolution.md` | 1.2 |
| Operational | `promt-documentation-refactoring-standards-2026.md` | 1.2 |
| Operational | `promt-documentation-quality-compression.md` | 1.1 |
| Operational | `promt-project-stack-dump.md` | 1.1 |
| Operational | `promt-mvp-baseline-generator-universal.md` | 1.3 |
| Operational | `promt-project-adaptation.md` | 1.1 |
| Operational | `promt-readme-sync.md` | 1.0 |
| Operational | `promt-project-rules-sync.md` | 1.1 |

---

## Дополнительная документация

- [Working with Diataxis Documentation](../how-to/working-with-diataxis-documentation.md) — ADR guidelines
- [ADR Index](../explanation/adr/index.md) — Полный список ADR
- `docs/official_document/` — READ-ONLY эталон терминов и API
- [Анализ пробелов системы промптов](../explanation/ai-prompt-system-gap-analysis.md) — Dual Schema + план расширения

---

## Журнал изменений README

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.59 | 2026-03-07 | Создан `promt-documentation-quality-compression.md` v1.0 (качество > объём, Protected Content Registry, алгоритм принятия решений). Депрекирован `promt-documentation-compression-executor.md` (60%-таргет). Обновлены: навигационная таблица, сценарий 5, реестр версий. |
| 1.58 | 2026-03-06 | Gate I compliance migration: добавлены `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений` во все 28 промптов. Версии всех файлов bumped (+0.1). Исправлено несоответствие версии `promt-project-rules-sync.md` (1.0→1.1). |
| 1.57 | 2026-03-06 | Полная перезапись README: удалены разделы «Доступные промпты» (~826 строк) и «Быстрый старт» (~637 строк) — вся документация промптов перенесена в сами файлы промптов (принцип самодокументации). Добавлены в навигационную таблицу: `promt-documentation-compression-executor.md`, `meta-promt-sync-init-generator.md`, `meta-promt-universal-prompt-generator.md`. Обновлён «Реестр версий промптов» — все 33 файла. README сокращён с 1971 до ~430 строк. |
| 1.56 | 2026-03-06 | Сценарий 6 «Сборка полной AI-системы с нуля» добавлен в 4.1; исправлены описания секций 26/27/28 в «Доступные промпты» и строк навигационной таблицы для `promt-readme-sync.md`/`promt-project-rules-sync.md` — приведены к новому scope (не 6 секций) |
| 1.55 | 2026-03-06 | Регенерация трёх промптов по `meta-promt-sync-init-generator.md` v1.0 — новая самодокументирующаяся структура (gates I+J): `promt-agent-init.md` v1.0, `promt-project-rules-sync.md` v1.0, `promt-readme-sync.md` v1.0 |
| 1.54 | 2026-03-06 | Полная проверка синхронизации 6 секций README.md: все 28 промптов присутствуют во всех секциях, нарушения topic slug-first отсутствуют |
| 1.53 | 2026-03-06 | Добавлен `promt-project-rules-sync.md` v1.0 |
| 1.52 | 2026-03-05 | Добавлен `promt-agent-init.md` v1.0 |
| 1.51 | 2026-03-05 | Добавлен `promt-readme-sync.md` v1.0 |
| 1.50 | 2026-03-05 | Добавлен Вариант 20 в «Быстрый старт» (раздел удалён в v1.57) |
| 1.44 | 2026-03-01 | Полная синхронизация prompt-системы: +4 новых промпта, обновлены версии, Sync Report в `artifacts/SYNC-REPORT-20260301.md` |
| 1.43 | 2026-02-27 | Добавлен `promt-project-adaptation.md` v1.0; расширен decision tree |
| 1.42 | 2026-02-27 | Создан `meta-promt-universal-prompt-generator.md` v1.0 |
| 1.41 | 2026-02-27 | Добавлены `promt-project-stack-dump.md` v1.0 и `promt-mvp-baseline-generator-universal.md` v1.2 |
| 1.38 | 2026-02-26 | Добавлен post-rename runbook |
| 1.32 | 2026-02-25 | Добавлен единый раздел «Шаблоны запросов и навигация» |
| 1.29 | 2026-02-25 | Приведение 8 операционных промптов к каноническому скелету |
| 1.14 | 2026-02-24 | Добавлены 6 операционных промптов: bug-fix/refactoring/security-audit/db-governance/ci-cd/onboarding |
