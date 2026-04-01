# Промпт: Адаптация к проекту по MVP/Baseline

**Версия:** 1.1  
**Дата создания:** 2026-02-27  
**Статус:** active  
**Тип:** Universal (project-agnostic)  
**Слой:** Planning → Transformation  
**Зависимости:** `promt-project-stack-dump.md`, `promt-mvp-baseline-generator-universal.md`

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Operational (Universal) |
| **Время выполнения** | 30–60 мин |
| **Домен** | Planning — адаптация к проекту по MVP/Baseline |

**Пример запроса:**

> «Используя `promt-project-adaptation.md`, адаптируй меня под текущий проект
> по файлу MVP.md / BASELINE.md: 7-step workflow, маппинг к коду,
> выявление gaps, onboarding-чеклист и Adaptation Report с Next 5 Steps.»

**Ожидаемый результат:**
- Adaptation Report: маппинг требований → конкретные файлы/модули
- Список gaps (не реализовано, но требуется по MVP)
- Onboarding-чеклист для немедленного старта
- Next 5 Steps с конкретными задачами

---

## Когда использовать

- После `promt-mvp-baseline-generator-universal.md` — адаптация к сгенерированному документу
- При onboarding нового AI-агента или разработчика к существующему проекту
- При возврате к проекту после длительного перерыва
- Для создания персонализированного action plan по MVP-документу

> **Шаг 3 в universal onboarding:** `promt-project-stack-dump.md` →
> `promt-mvp-baseline-generator-universal.md` → **`promt-project-adaptation.md`**.

---

## 1. Миссия

Помочь AI-агенту или новому разработчику **быстро "въехать" в текущий проект**, используя существующий MVP или Baseline документ как первоисточник истины.

**Выходные артефакты:**
- Markdown-отчёт: "Адаптация к [Project]"
- Mapping: конкретные файлы/модули, соответствующие каждому requirement
- Немедленные действия (Next 5 Steps)
- Риск-анализ: что НЕ реализовано и почему важно

**Примусловие:** Должен быть создан файл `MVP.md` или `BASELINE.md` через `promt-mvp-baseline-generator-universal.md`.

---

## 2. Синхронизационный контракт

| Аспект | Требование | Источник Истины |
|--------|-----------|-----------------|
| **Проект-агностицизм** | Должен работать с ANY стеком (Backend, Frontend, Mobile, Infrastructure, SaaS, Library, API) | `meta-promt-universal-prompt-generator.md` |
| **MVP/Baseline как вход** | Обязательно принимает `.md` файл с структурой Must/Should/Could/Won't | `promt-mvp-baseline-generator-universal.md` v1.2+ |
| **Context7-gate** | Шаг 1 workflow = Context7 research на best practices 2026 для "rapid project onboarding" | `meta-promt-adr-system-generator.md` |
| **Dual-status** | Работает для обоих статусов: in-progress проектов и завершённых | Не требует ADR системы |
| **Никаких legacy паттернов** | Не упоминать: PHASE_*.md, *_SUMMARY, *_REPORT статических docs | Anti-legacy gate |

---


## Назначение

Помочь AI-агенту или новому разработчику быстро адаптироваться к текущему проекту, используя MVP или Baseline документ как источник истины, с маппингом к коду и выявлением gaps.

## Входы

- MVP или Baseline документ проекта (`MVP.md` / `BASELINE.md`)
- Исходный код проекта (для маппинга требований к файлам)
- Project Stack Dump (из `promt-project-stack-dump.md`)

## Выходы

- Adaptation Report: маппинг требований → файлы/модули
- Список gaps (не реализовано, но требуется по MVP)
- Onboarding-чеклист + Next 5 Steps

## Ограничения / инварианты

См. `## 2. Синхронизационный контракт` выше. Не изменять исходный MVP-документ. Маппинг должен ссылаться на конкретные файлы и строки кода.

## Workflow шаги

См. `## 4. Workflow (7 шагов)` ниже: Загрузка MVP → Анализ стека → Маппинг → Gap Analysis → Risk Assessment → Recommendations → Next 5 Steps.

## Проверки / acceptance criteria

См. `## 5. Quality Checklist` ниже. Adaptation Report завершён, когда: все Must-Have mapped, gaps идентифицированы, Next 5 Steps конкретны и actionable.

## 3. Контекст (project-agnostic)

### 3.1 Когда использовать этот промпт

✅ **Используй**, когда нужно:
- Быстро разобраться в новом проекте (~30 минут активной работы)
- Спланировать first pull request или first task в существующем проекте
- Адаптировать новый prompt-шаблон под текущий project context
- Выявить gaps между документированным MVP и реальной реализацией
- Создать onboarding-checklist для новой role (DevOps, Full-stack, etc)

❌ **НЕ используй**, когда:
- Нужна глубокая верификация всего кода (используй `promt-verification.md`)
- Нужна консолидация или рефакторинг архитектуры (используй соответствующие ADR prompts)
- MVP/Baseline файл НЕ создан (сначала запусти `promt-mvp-baseline-generator-universal.md`)

### 3.2 Примеры входных файлов

**Вход 1: Típичный MVP документ**
```markdown
# MVP: E-Commerce Platform (2026)

## Must Have (Deadline: 2026-Q1)
- User registration + JWT auth
- Product catalog (CRUD)
- Shopping cart
- Payment integration (N/A)

## Should Have (Deadline: 2026-Q2)
- Admin dashboard
- Search + filtering
- Email notifications
- Inventory management

...

## Critical Path
[Product Catalog] → [Inventory] → [Shopping Cart] → [Payments]
```

**Вход 2: Típичный Baseline документ**
```markdown
# Technical Baseline: SaaS K8s Platform

## Chosen Stack
- Backend: Python 3.10 + FastAPI + async
- DB: PostgreSQL 14 + Alembic migrations
- K8s: k3s + Helm + Traefik + cert-manager
- Infrastructure: GitOps + ArgoCD

## Critical Status
[✓] K8s cluster + storage provisioning
[✓] Database baseline (init-saas-database.sql)
[⏳] Payment gateway integration (70% done)
[✗] Admin dashboard (0% done — blocked on auth)

...
```

### 3.3 Связь с другими промптами

```
┌─────────────────────────────────────────┐
│ promt-project-stack-dump (Discovery)    │ ← Шаг 0 (опционально)
└────────────┬────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────┐
│ promt-mvp-baseline-generator (Planning) │ ← Шаг 0 (обязательно)
│                                         │    Создаёт MVP.md или BASELINE.md
└────────────┬────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────┐
│ THIS: promt-project-adaptation          │ ← Шаг 1 (адаптация)
│ (Rapid Onboarding)                      │    Читает MVP.md / BASELINE.md
└────────────┬────────────────────────────┘    Выдает Adaptation Report
             │
             ↓
     [Next Task / PR]
```

---

## 4. Workflow (7 шагов)

### Шаг 1: Context7 Research — Best Practices для Rapid Onboarding

**Цель:** Получить contemporary подход к быстрому разбору незнакомых проектов.

**Что делать:**
1. Спроси Context7 (MCP):
   - `"rapid project onboarding best practices 2026"`
   - `"gap analysis between documentation and code"`
   - `"how to create effective project adaptation playbooks"`
2. Выбери **3 ключевых принципа** из результатов.
3. Запиши их как backlog в Adaptation Report (раздел "Principles Used").

**Выходные:** 3–5 ключевых идей для шагов 2–7.

### Шаг 2: Парсинг MVP/Baseline файла

**Входные данные:**
- MVP.md или BASELINE.md (путь на файл или полный текст)
- Project name + domain (e.g., "E-Commerce", "K8s SaaS", "Mobile App")

**Что делать:**
1. Даступи файл, выдели ключевые блоки:
   - Must/Should/Could/Won't (если MVP)
   - Chosen Stack (если Technical Baseline)
   - Critical Path
   - Dependencies + Blockers
   - Risks + Assumptions

2. Создай **структурированный extractv (JSON-like)**:
   ```python
   extracted = {
       "project_name": "...",
       "mvp_deadline": "2026-Q1",
       "must_haves": [...],
       "should_haves": [...],
       "critical_path": [...],
       "tech_stack": {...},
       "blockers": [...],
       "risks": [...]
   }
   ```

3. **Валидируй:**
   - Все Must-items имеют ответственного
   - Critical Path ациклическая (DAG)
   - Нет противоречий в зависимостях

**Выходные:** Структурированный дамп данных из MVP/Baseline.

### Шаг 3: Маппинг к Codebase

**Что делать:**
1. Для каждого Must/Should item → найди соответствующее **имя модуля / файл / функцию** в реальном коде.
   ```markdown
   | MVP Requirement | Code Location | Status | Completeness |
   |---|---|---|---|
   | User registration | `app/auth/users.py` | ✓ Done | 100% |
   | Payment integration | `app/payments/yookassa.py` | ⏳ In Progress | 70% |
   | Admin dashboard | NOT FOUND | ✗ Not Started | 0% |
   ```

2. Для каждого **blockers → найди причину**:
   - Missing dependency?
   - Design decision not documented?
   - Technical debt?
   - Team bottleneck?

3. Стройка **Dependency Graph** (можешь ASCII):
   ```
   [Auth] ──→ [Cart] ──→ [Payments]
      ↗             ↘
   [User Mgmt]  [Inventory]
   ```

**Выходные:** Таблица маппинга + граф зависимостей.

### Шаг 4: Анализ Current State vs MVP

**Что делать:**
1. Для каждого Must-item: **% реализации** (0%, 25%, 50%, 75%, 100%).
2. Для каждого должен быть **владелец** или **reason why blocked**.
3. Выдели **Critical Path items** vs **Nice-to-have**.

   ```markdown
   ## Implementation Status

   ### 🟢 Done (100%)
   - [ ] Item: User auth (JWT)
   - [ ] Complexity: Medium
   - [ ] Owner: Backend team
   - [ ] Code: `app/auth/`

   ### 🟡 In Progress (50–99%)
   - [ ] Item: Payment integration (N/A)
   - [ ] Complexity: High
   - [ ] Owner: Integration lead
   - [ ] Code: `app/payments/`
   - [ ] Blocker: Awaiting keys from vendor

   ### 🔴 Not Started (0%)
   - [ ] Item: Admin dashboard
   - [ ] Complexity: High
   - [ ] Owner: UNASSIGNED ⚠️
   - [ ] Reason: Dependency on auth (85% done, not ready yet)
   ```

4. **Выпиши все Assumptions** из MVP, которые актуальны:
   - "Используем async PostgreSQL"
   - "K8s ingress решена через Traefik"
   - "Mobile app будет на React Native"

**Выходные:** Status table + Assumptions + Critical path timeline.

### Шаг 5: Выявление Gaps между Doc и Code

**Что делать:**
1. Найди **всё, что документировано в MVP но НЕ в коде** или наоборот:
   ```markdown
   | Gap | Where | Severity | Action |
   |---|---|---|---|
   | "Weekly summary emails" in MVP, no code | MVP/Baseline | Medium | Add to backlog or remove from MVP |
   | "Redis caching" implemented but not in MVP | Code | High | Update MVP to match reality |
   | "Database migration system" — assumptions differ | Both | Medium | Align: use Alembic or raw SQL? |
   ```

2. Классифицируй по severity:
   - 🔴 CRITICAL: Affects timeline / safety / compliance
   - 🟠 HIGH: Affects performance / UX / maintenance
   - 🟡 MEDIUM: Nice-to-have, update docs
   - 🟢 LOW: Documentation typos, minor inconsistencies

**Выходные:** Gap table + remediation actions.

### Шаг 6: Создание Adaptation Report

**Структура файла `ADAPTATION-[Project]-[Date].md`:**

```markdown
# Adaptation Report: [Project Name]

**Adapted:** [Date]  
**Adapted by:** [Context: AI-agent / Prompt / Dev name]  
**Based on:** [MVP.md / BASELINE.md] v[version]

## 1. Executive Summary
- Project name + domain
- Timeline from MVP
- Current stage (% complete)
- Main blocker (if any)
- Next 72 hours action

## 2. Tech Stack (from Baseline)
- Backend: ...
- Database: ...
- Infrastructure: ...  
- (or "Not in Baseline document")

## 3. Critical Path
```
[A] → [B] → [C]
      ↓
     [D]
```

## 4. Implementation Status
[Table from Шаг 4]

## 5. Gaps & Mismatches
[Table from Шаг 5]

## 6. Risk Assessment
| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| Payment keys missing | Blocks 40% of MVP | High | Obtain keys + test in sandbox |
| Admin dashboard unstarted | Impacts Q2 timeline | Medium | Clarify requirements ASAP |

## 7. Recommendations
- Priority 1: [Immediate action — often a blocker removal]
- Priority 2: [Next logical step]
- Priority 3: [Optimization / debt]

## 8. Next 5 Steps (First Day)
- [ ] Step 1: ...
- [ ] Step 2: ...
- [ ] Step 3: ...
- [ ] Step 4: ...
- [ ] Step 5: ...

## 9. Assumptions & Sync Points
- [Assumption from MVP]
- [Decision needed from team]
- [Risk that needs owner]

## 10. Related Documents
- MVP.md (source)
- docs/architecture/
- docs/rules/
- Roadmap (if exists)

## 11. Questions for Team
- Q: What's blocking admin dashboard?
- Q: Are payment integrations in test or live?
- Q: Who owns the [Module X]?
```

**Выходные:** Полный Adaptation Report в Markdown.

### Шаг 7: Валидация и Экспорт

**Что делать:**
1. **Проверь Adaptation Report**:
   - ✓ Все Must-items have mapping
   - ✓ Critical Path актуальна (no cycles)
   - ✓ Gaps actionable (не просто "написать код")
   - ✓ Next 5 Steps = конкретные PR / meeting / docs update

2. **Экспортируй артефакты**:
   ```bash
   # Output files:
   docs/adaptation/ADAPTATION-[Project]-[Date].md           # Main report
   docs/adaptation/ADAPTATION-[Project]-[Date]-mapping.yaml # Code locations
   docs/adaptation/ADAPTATION-[Project]-[Date]-graph.txt    # Dependency graph
   ```

3. **Создай Checklist для руководителя** (Optional):
   ```markdown
   - [ ] Read Adaptation Report
   - [ ] Confirm Critical Path  
   - [ ] Assign owners to blocked items
   - [ ] Schedule sync on assumptions
   - [ ] Update MVP if needed
   ```

**Выходные:** 3 файла + Ready for first task.

---

## 5. Quality Checklist (для промпта)

Перед тем как выдать результат, проверь:

- [ ] **A. Skeleton Check:** Все 11 разделов Adaptation Report заполнены
- [ ] **B. Source of Truth:** MVP/Baseline файл = единственный источник требований
- [ ] **C. Code Mapping:** Каждый Must/Should item → точное имя файла (или "NOT FOUND" + reason)
- [ ] **D. Dependency Validation:** Critical Path — ациклич, логичен, реалистичен
- [ ] **E. Gap Completeness:** Все различия doc ↔ code задокументированы
- [ ] **F. Actionability:** Next 5 Steps — конкретные действия (не "улучшить код")
- [ ] **G. Context7 Used:** Шаг 1 выполнен, best practices 2026 упомянуты
- [ ] **H. No Legacy Patterns:** Нет стcтик типа "PHASE_*.md", "*_SUMMARY.md"

---

## 6. Anti-patterns (что НЕ делать)

❌ **Don't:**
1. **Пропустить Context7 research** — это шаг 1, без этого потеряешь лучшие практики.
2. **Верить MVP/Baseline на 100%** — always cross-validate с кодом.
3. **Создать Adaptation Report с общими фразами** ("всё хорошо", "нужно улучшить"). Должны быть конкретные файлы + номера строк.
4. **Забыть про Blockers** — если item на 50%, обязательно выпиши причину.
5. **Оставить "Not Started" items без owners** — это красная флаг + должно быть в Risks.
6. **Трактовать MVP как железобетон** — это working document, он может измениться за время разработки.
7. **Экспортировать только .md** — дай тоже mapping.yaml для инструментов.

✅ **Do:**
1. Если блокер — приложи план разблокировки.
2. Если разница doc ↔ code — заполни Gaps table с severity.
3. Если что-то неясно → добавь в "Questions for Team".
4. Если Next 5 Steps не очевидны → переговори с MVП owner перед экспортом.

---

## Связи с другими промптами

| Промпт | Когда использовать |
|--------|-------------------|
| `promt-project-stack-dump.md` | Шаг 0 (опционально): если нужна **чистка** текущего стека перед адаптацией |
| `promt-mvp-baseline-generator-universal.md` | **Обязательно перед этим**: создать MVP.md или BASELINE.md |
| `meta-promt-universal-prompt-generator.md` | Если нужно адаптировать другой промпт под этот specific project |
| `promt-adr-implementation-planner.md` | После adaptation: построить план по Critical Path |
| `promt-feature-add.md` | После adaptation: добавить feature из Should/Could в реализацию |
| `promt-verification.md` (-specific) | Для глубокой верификации ADR↔code (если это проект на базе ) |

---

## 8. Примечания по Integration

### Как использовать в production workflow

```
Вариант A (Manual):
1. Создать MVP.md через `promt-mvp-baseline-generator-universal.md`
2. Запросить: "Используя `promt-project-adaptation.md`, адаптируй меня по файлу MVP.md"
3. Получить ADAPTATION-[Project]-[Date].md + Next Steps

Вариант B (Future Orchestrator):
prompt-runner.sh project-stack-dump \
  && prompt-runner.sh mvp-baseline \
  && prompt-runner.sh adapt-by-mvp docs/mvp/MVP-2026.md
```

### Выходные артефакты для CI/CD

```yaml
artifacts/
  adaptation/
    ADAPTATION-MyProject-20260227.md           # Main report
    ADAPTATION-MyProject-20260227-mapping.yaml # Code locations
    ADAPTATION-MyProject-20260227-graph.txt    # Dependencies
```

---

## 9. Версионирование

| Версия | Дата | Изменение |
|--------|------|-----------|
| 1.0 | 2026-02-27 | Initial release: 7-step workflow, Adaptation Report structure, Quality checklist A-H |

---

## Ресурсы

| Ресурс | Путь | Назначение |
|---|---|---|
| **MVP/Baseline** | `docs/ai-agent-prompts/promt-mvp-baseline-generator-universal.md` | Reference document |
| **Планирование реализации** | `docs/ai-agent-prompts/promt-adr-implementation-planner.md` | Implementation roadmap |
| **ADR-файлы** | `docs/explanation/adr/ADR-*.md` | Architecture constraints |
| **Верификация** | `docs/ai-agent-prompts/promt-verification.md` | Validation workflow |
| **Правила проекта** | `.github/copilot-instructions.md` | Development conventions |
| **Официальная документация** | `docs/official_document/` | **READ-ONLY** эталон |
| **Meta-prompt** | `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md` | Source of truth |

---

## 10. Footer (Sync Metadata)

**Статус:** active ✓  
**Layer:** Planning → Transformation  
**Domain:** Universal (любой проект, любой стек)  
**Constraint:** Требует MVP/Baseline файл  
**Last Sync:** 2026-02-27  
**Source of Truth:** `meta-promt-adr-system-generator.md` (Quality gates A-H)  
**Registry Entry:** See `docs/ai-agent-prompts/README.md` (Table 2, Row: "Адаптация к проекту по MVP/Baseline")

---

**Удачной адаптации! 🚀**

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|----------|
| 1.1 | 2026-03-06 | Добавлены секции Gate I: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`. |
| 1.0 | 2026-02-27 | Первая версия: 7-step adaptation workflow с маппингом к коду. |
