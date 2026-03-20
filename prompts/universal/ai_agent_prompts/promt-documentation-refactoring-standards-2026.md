# AI Agent Prompt: CodeShift Documentation Refactoring & Standards 2026

**Version:** 1.2
**Date:** 2026-02-25
**Purpose:** Системный рефакторинг и модернизация документации CodeShift по стандартам 2026 без нарушения архитектурных инвариантов проекта.

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Operational |
| **Время выполнения** | 60–90 мин |
| **Домен** | Docs governance — рефакторинг документации 2026 |

**Пример запроса:**

> «Используя `promt-documentation-refactoring-standards-2026.md`, выполни системный аудит
> и план рефакторинга документации по стандартам 2026 с Diátaxis scorecard
> и проверками через make-команды.»

**Ожидаемый результат:**
- Diátaxis scorecard по каждому разделу документации
- План рефакторинга с приоритетами и метриками (целевой % сокращения)
- Список нарушений (дубли, устаревшее, нарушения Diátaxis)
- Конкретные задачи для `promt-documentation-quality-compression.md`

---

## Когда использовать

- При плановом annual review документации
- При обнаружении значительного разрастания документов (>600 строк в project-rules.md)
- Перед началом работы с `promt-documentation-quality-compression.md` (нужен план)
- После крупных изменений в архитектуре (документация устарела)

> **Связка:** этот промпт даёт **план**; `promt-documentation-quality-compression.md` **выполняет** план.

---

## Mission Statement

Ты проводишь аудит и улучшение документации проекта CodeShift в режиме **Docs as Code**,
строго по Diátaxis и правилам репозитория.

Ты формируешь проверяемый план улучшений и точечные предложения изменений по файлам,
не нарушая архитектурные и операционные инварианты системы.

Ты не выполняешь кодовые/инфраструктурные изменения вне области документации и не изменяешь
`docs/official_document/`.

---

## Назначение

Обеспечить системный аудит качества документации CodeShift и подготовить приоритизированный,
проверяемый план рефакторинга по стандартам 2026 (Diátaxis + Docs as Code + governance),
с привязкой к конкретным файлам и обязательной валидацией через make-команды.

---

## Входы

- `docs/` (вся документация)
- `mkdocs.yml`
- `docs/explanation/adr/index.md`
- `docs/ai-agent-prompts/README.md`
- `docs/templates/DOCUMENTATION_DECISION_TREE.md`
- `docs/rules/project-rules.md`
- `docs/official_document/` (только чтение)

---

## Выходы

- Аудит-отчёт в строгом формате `CodeShift Documentation 2026 Audit & Refactoring Plan`
- Diátaxis scorecard по 4 категориям
- Приоритизированный план (`Critical / High / Medium / Low`) с файлами, рисками и критериями готовности
- Контрольный список соблюдения инвариантов
- Команды валидации и последовательность следующих шагов

---

## Ограничения / инварианты

1. Diátaxis обязателен: `docs/tutorials`, `docs/how-to`, `docs/reference`, `docs/explanation`.
2. `docs/reference/` — **только AUTO-GENERATED** (обязателен маркер `<!-- AUTO-GENERATED -->`).
3. `docs/official_document/` — **READ-ONLY**.
4. ADR идентифицируются по **topic slug** (не по номеру).
5. Dual-status в ADR обязателен: `## Статус решения` + `## Прогресс реализации`.
6. Канонический источник схемы БД: `scripts/utils/init-saas-database.sql`.
7. Активный контур деплоя: `Helm + config/manifests`; `k8s/` — legacy-контур.
8. Не создавать legacy-документы: `PHASE_*.md`, `*_COMPLETE.md`, `*_SUMMARY.md`, `*_REPORT.md`, `*_STATUS.md`, `NEXT_STEPS*.md`.
9. Перед созданием нового `.md` сначала искать и обновлять существующий релевантный документ.
10. Для архитектурных/библиотечных решений обязателен **Context7 gate**.
11. Для проверки фактического прогресса ADR использовать `./scripts/verify-adr-checklist.sh --topic <slug>`.

---

## Контракт синхронизации системы

> **Source of truth:** `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`
> Этот промпт подчиняется source of truth. При конфликте формулировок приоритет у meta-prompt.

Дополнительные обязательные правила этого промпта:
- Любые предложения по структуре docs не должны нарушать Diátaxis-категоризацию.
- Ручные правки в `docs/reference/` запрещены; для reference-раздела допустимы только авто-генерационные потоки.
- Любые ссылки на `k8s/` в документации должны быть явно помечены как legacy/deprecated контекст.
- Изменения `README.md` в корне репозитория выполняются только через `make docs-readme`.

---

## Project Context

### О проекте

**CodeShift** — multi-tenant SaaS-платформа, развёртывающая VS Code (code-server)
в браузере через Telegram Bot + YooKassa на Kubernetes.

### Документационный контекст

- Проект использует Diátaxis как обязательную модель структуры документации.
- Для prompt-системы действует governance через `docs/ai-agent-prompts/README.md` и Prompt Guard.
- `docs/official_document/` служит эталонным источником терминов/API и всегда только для чтения.

### ADR Topic Registry

> **КРИТИЧНО:** ADR ищутся и идентифицируются по topic slug.
> Пример поиска: `find docs/explanation/adr -name "ADR-*-{slug}*.md" | head -1`

Релевантные topic slugs:
- `documentation-generation`
- `telegram-bot-saas-platform`
- `k8s-provider-abstraction`
- `path-based-routing`
- `storage-provider-selection`

---

## Workflow шаги

Выполняй шаги строго по порядку, без пропуска фаз.

### Шаг 1: Discovery

1. Проанализируй текущую структуру `docs/`.
2. Найди дубли, legacy-следы, не-Diátaxis контент.
3. Определи, какие файлы нужно обновить, а не создавать заново.

### Шаг 2: Diátaxis Audit

1. Проверь полноту и качество по 4 категориям Diátaxis.
2. Отдельно проверь, что `docs/reference/` не редактируется вручную.
3. Зафиксируй score и краткое обоснование для каждой категории.

### Шаг 3: Context7 Gate (обязательный)

Для каждого архитектурного улучшения выполни запросы:

- `Context7: best practices for Diátaxis in Kubernetes + Helm + SaaS docs 2026`
- `Context7: best practices for MkDocs Material navigation and docs automation 2026`
- `Context7: best practices for ADR documentation governance 2026`

Фиксируй, какие выводы действительно применяются к CodeShift.

### Шаг 4: Refactoring Plan

1. Сформируй план по приоритетам: `Critical / High / Medium / Low`.
2. Для каждого пункта укажи:
   - цель,
   - затрагиваемые файлы,
   - риск,
   - оценку усилий,
   - критерий готовности.

### Шаг 5: Implementation Proposal

1. Дай точечные изменения по файлам.
2. Не изменяй `docs/official_document/`.
3. Для prompt-файлов предложи version bump.
4. При изменении состава/версий prompt-файлов синхронизируй реестр в `docs/ai-agent-prompts/README.md`.

### Шаг 6: Validation

Обязательные проверки:

- `make docs-prompt-guard`
- `make docs-check-mkdocs-nav`

Если затронут корневой `README.md`, обновление выполнять только через `make docs-readme`.

---

## Проверки / acceptance criteria

- План улучшений привязан к конкретным файлам.
- Нет нарушений инвариантов проекта.
- Нет создания запрещённых legacy-документов.
- Все предложенные изменения проверяемы через make-команды.
- Вывод сформирован строго в требуемом шаблоне output.

---

## Output Format (строго)

```markdown
# CodeShift Documentation 2026 Audit & Refactoring Plan

**Дата аудита:** YYYY-MM-DD
**Общий уровень зрелости:** X/10

## 1) Diátaxis Scorecard
| Раздел | Оценка (1-10) | Статус | Комментарий |
|---|---:|---|---|
| Tutorials | ... | ... | ... |
| How-to | ... | ... | ... |
| Reference (AUTO-GENERATED only) | ... | ... | ... |
| Explanation / ADR | ... | ... | ... |

## 2) Ключевые находки
### Сильные стороны
- ...
### Проблемы и риски
- ...

## 3) Приоритизированный план
### Critical
- [ ] ... (файлы: ...)
### High
- [ ] ... (файлы: ...)
### Medium
- [ ] ... (файлы: ...)
### Low
- [ ] ... (файлы: ...)

## 4) Контроль инвариантов
- [ ] Topic slug-first соблюдён
- [ ] Dual-status для ADR соблюдён
- [ ] `docs/official_document/` не изменялся
- [ ] `reference/` только auto-generated
- [ ] Нет новых legacy-файлов/директорий
- [ ] Нет ссылок на `k8s/` как active contour
- [ ] DB schema source = `scripts/utils/init-saas-database.sql`

## 5) Команды проверки
- `make docs-prompt-guard`
- `make docs-check-mkdocs-nav`
- `make docs-readme` (если изменён корневой README)

## 6) Следующие шаги
1. ...
2. ...
3. ...
```

---

## Anti-patterns

- Создавать новый markdown-файл без проверки существующих релевантных документов.
- Редактировать вручную файлы в `docs/reference/`.
- Изменять `docs/official_document/` или трактовать его как editable source.
- Использовать номер ADR как первичный идентификатор вместо topic slug.
- Предлагать изменения, не проверяемые через `make docs-prompt-guard` и `make docs-check-mkdocs-nav`.

---

## Ресурсы

| Ресурс | Путь | Назначение |
|---|---|---|
| **Исходная docs** | `docs/` | Target for refactoring |
| **mkdocs.yml** | `mkdocs.yml` | Navigation |
| **ADR-стандарты** | `docs/explanation/adr/ADR-template.md` | Doc patterns |
| **Скрипты docs** | `scripts/check-mkdocs-nav.sh` | Validation |
| **Diátaxis** | `.github/copilot-instructions.md` | Structure rules |
| **Официальная документация** | `docs/official_document/` | **READ-ONLY** эталон |
| **Meta-prompt** | `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md` | Source of truth |

---

## Связи с другими промптами

| Промпт | Когда использовать |
|--------|--------------------|
| `promt-verification.md` | После внедрения документационных изменений для общей проверки ADR↔код консистентности |
| `promt-index-update.md` | Если обновления затрагивают ADR-структуру и требуют синхронизации индекса |
| `promt-sync-optimization.md` | Для аудита согласованности всей prompt-системы после структурных правок |
| `promt-versioning-policy.md` | Для формального решения о version bump при изменении prompt-контрактов |
| `promt-system-evolution.md` | Когда изменение затрагивает системные инварианты prompt-системы, а не только docs-аудит |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|----------|
| 1.2 | 2026-03-06 | Добавлены секции Gate I: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`. |
| 1.1 | 2026-02-25 | Diátaxis scorecard, make-команды проверки, Anti-Legacy compliance. |
| 1.0 | 2026-02-24 | Первая версия: аудит документации 2026. |

---

**Prompt Version:** 1.2
**Date:** 2026-03-06
**Maintainer:** @perovskikh
**Date:** 2026-02-25