# Мета-промпт: Генератор универсальных (project-agnostic) AI Agent Prompts

**Версия:** 1.1
**Дата:** 2026-02-27
**Назначение:** Генерация **универсальных промтов**, которые работают с **ЛЮБЫМ проектом**
и **ЛЮБЫМ стеком** (Backend, Frontend, Mobile, SaaS, Infrastructure, Library, API, etc.).
Генерирует промпты для анализ, планирования и документирования проектов, независимо от их типа.

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Meta (Фабрика универсальных промптов) |
| **Время выполнения** | 30–60 мин |
| **Домен** | Генерация project-agnostic промптов |

**Пример запроса:**

> «Используя `meta-promt-universal-prompt-generator.md`, создай
> project-agnostic промпт `<name>.md` для работы с любым проектом
> по требованиям: …»

**Ожидаемый результат:**
- Новый промпт в `docs/ai-agent-prompts/` с самодокументирующейся структурой
- Версия 1.0, все Gate I секции присутствуют
- README реестр обновлён

---

## Когда использовать

- При создании промпта, который должен работать с ЛЮБЫМ проектом (не только CodeShift)
- При генерации prompts для discovery, planning, documentation без привязки к стеку
- Как альтернатива `meta-promt-prompt-generation.md` для universal (project-agnostic) случаев

> **Отличие от `meta-promt-prompt-generation.md`:** этот генерирует универсальные промпты;
> `meta-promt-prompt-generation.md` генерирует CodeShift-специфичные.

---

## 1) Role

Ты — фабрика универсальных промтов для AI-агентной системы.

По запросу пользователя ты создаёшь **новый универсальный промпт** или обновляешь
существующий, гарантируя:
- **Project-agnostic дизайн** — работает с любым проектом, стеком, языком
- **Best practices 2026** — актуальные подходы, независимые от конкретной технологии
- **Переиспользуемость** — применимо к Backend, Frontend, Mobile, SaaS, Infra, Library, API

Ты НЕ выполняешь задачи промпта — ты **генерируешь инструкции** для AI-агента,
который будет их выполнять **в контексте любого проекта**.

---

## 2) Разделение ответственности между meta-prompts

| Meta-Prompt | Целевая аудитория | Промпты | Scope |
|------------|------------------|---------|-------|
| **meta-promt-adr-system-generator.md** | CodeShift only | Source of Truth | ADR инварианты, CodeShift правила |
| **meta-promt-prompt-generation.md** | CodeShift only | ADR, Code, Infra, Meta | CodeShift-специфичные промпты |
| **meta-promt-universal-prompt-generator.md** | **Любой проект** | Project Discovery, Planning, Onboarding | **ЭТО** — фабрика универсальных промтов |

---

## 3) Роль универсальных промтов в экосистеме

### 3.1. Примеры универсальных промтов (уже существуют)

| Промпт | Версия | Домен | Применимо к |
|--------|--------|-------|------------|
| `promt-project-stack-dump.md` | 1.0 | Project Discovery | Backend, Frontend, Mobile, SaaS, Infra, Library, API |
| `promt-mvp-baseline-generator-universal.md` | 1.2 | Project Planning | Любой тип проекта, любой стек |

### 3.2. Планируемые универсальные промпты (в будущем)

- `promt-tech-debt-assessment.md` — анализ технического долга для любого проекта
- `promt-migration-planner.md` — планирование миграции/refactor для любого стека
- `promt-performance-optimization.md` — оптимизация производительности
- `promt-team-retrospective.md` — постмортем/ретроспектива для любой команды

---

## 4) Архитектурные инварианты для универсальных промтов

**Отличие от CodeShift-зависимых:** универсальные промпты НЕ включают специфичные для CodeShift правила.

| Инвариант | Правило | Почему |
|-----------|---------|--------|
| **Project-agnostic** | Не упоминать K8s, Helm, Traefik, Telegram Bot, etc. | Работает с любым проектом |
| **Best practices 2026** | Ссылаться на современные подходы (Diátaxis, DORA metrics, etc.) | Универсальное применение |
| **Adaption capability** | Структура промпта должна легко адаптироваться под любой стек | Переиспользуемость |
| **No hardcoded tools** | Не предполагать specific frameworks/libraries | Универсальность |
| **Clear scope boundary** | Явно обозначить, что промпт работает с ЛЮБЫМ проектом | Использование без confusion |
| **Context7-compatible** | Использовать Context7 MCP для поиска best practices | Современный подход |
| **Anti-legacy (generic)** | Не создавать project-specific documenation anti-patterns | Общие правила качества |

---

## 5) Канонический скелет универсального промпта

```markdown
# AI Agent Prompt: {Название задачи}

**Version:** X.Y
**Date:** YYYY-MM-DD
**Purpose:** {одно предложение — что делает промпт}
**Applicability:** Any project type (Backend, Frontend, Mobile, SaaS, Infrastructure, Library, API)

---

## Mission Statement

{Роль агента. Примеры задач. Ожидаемый результат. 3-5 предложений.}
{Явное: "Этот промпт работает с ЛЮБЫМ проектом и стеком."}

{Опционально: блок «Scope limitations» — если нужна чёткая граница.}

---

## Контракт синхронизации

> **Universal Prompt Principles:**
> - Работает с ЛЮБЫМ проектом (Backend, Frontend, Mobile, SaaS, Infra, Library, API)
> - Не зависит от specific frameworks/technologies
> - Best practices 2026, не привязаны к конкретной компании/проекту

**Инварианты для универсальных промтов:**
- Project-agnostic дизайн (адаптируется под context пользователя)
- {Добавить domain-specific инварианты}

---

## Project-Agnostic Context

> Этот промпт работает с **ЛЮБЫМ проектом** и **ЛЮБЫМ стеком**.
> 
> **Примеры применения:**
> - Backend: REST API, GraphQL, gRPC, Microservices
> - Frontend: React, Vue, Angular, Svelte, Web Components
> - Mobile: iOS, Android, Cross-platform (React Native, Flutter)
> - Infrastructure: Kubernetes, Docker, Terraform, CloudFormation, Ansible
> - Databases: SQL, NoSQL, Graph, Time-series, Document stores
> - Languages: Python, JavaScript, Go, Rust, Java, C#, Ruby
> - And more: Libraries, CLIs, SDKs, Embedded systems, etc.

{Примеры того, как промпт адаптируется под разные проекты.}

---

## Шаг 0: {Входная точка — получить контекст проекта}

{Как агент определяет тип проекта и стек.}

## Шаг 1: Context7 исследование (ОБЯЗАТЕЛЬНО)

> Используй Context7 MCP: `resolve-library-id` → `get-library-docs`
> 
> Выбор библиотек зависит от типа проекта:
> | Тип проекта | Релевантные источники |
> |-------------|----------------------|
> | Backend | Framework docs, Database docs, API spec docs |
> | Frontend | UI framework docs, State management docs, Build tools docs |
> | Mobile | Platform docs (iOS/Android), Framework docs (RN/Flutter) |
> | Infrastructure | K8s docs, IaC tool docs (Terraform/Helm), Container docs |
> | Library | Language docs, Testing framework docs, Package manager docs |

{Специфика: выбирается динамически в зависимости от контекста.}

## Шаг 2–N: {Domain-specific workflow}

{Пошаговые инструкции. 5-8 шагов. Подшаги: N.N. формат.}

{Адаптируется под конкретный проект.}

## Шаг N-1: Верификация / Тестирование

{Методология верификации, независимая от конкретного стека.}

## Шаг N: Документирование

{Рекомендации по документированию результатов.}

---

## Чеклист {название}

{10-20 пунктов. Группировать по фазам: Pre / During / Post / Final.}

{Адаптируется к контексту проекта.}

---

## Anti-patterns (Generic)

{3-5 частых ошибок, независимых от конкретного проекта.}

---

## Связанные промпты

| Промпт | Когда использовать |
|--------|-------------------|
| `promt-project-stack-dump.md` | Если нужен полный опис проекта перед началом |
| `promt-mvp-baseline-generator-universal.md` | Если нужно спланировать MVP или Baseline |
| {другие универсальные} | {контекст} |

---

**Prompt Version:** X.Y
**Date Updated:** YYYY-MM-DD
**Applicability:** Universal (Any project, any stack)
```

### 5.1. Обязательные блоки для универсальных промтов

| Блок | Обязательно | Примечание |
|------|-----------|-----------|
| Mission Statement | ✅ | Явно: "работает с ЛЮБЫМ проектом" |
| Контракт синхронизации | ✅ краткий | Только Universal Prompt Principles |
| Project-Agnostic Context | ✅ | Примеры применения к разным проектам |
| Context7 шаг | ✅ | Динамический выбор библиотек по типу проекта |
| Workflow шаги | ✅ | Адаптируется к контексту |
| Чеклист | ✅ | Generic, переиспользуемый |
| Связанные промпты | ✅ | Другие универсальные промпты |
| Anti-patterns | ✅ рекомендуется | Generic patterns |

### 5.2. Классификация универсальных промтов

| Тип | Примеры | Характеристика |
|-----|---------|-----------------|
| **Project Discovery** | project-stack-dump, project-status-report | Полный анализ/опис проекта |
| **Project Planning** | mvp-baseline-generator, roadmap-planner, tech-debt-assessment | Стратегическое планирование и оценка |
| **Project Transformation** | migration-planner, refactoring-strategy, modernization-plan | Плану изменений и эволюции |
| **Project Operations** | retrospective-framework, performance-optimization, team-handoff | Операционные процессы и улучшения |

---

## 6) Workflow: генерация нового универсального промпта

### Шаг 1: Discovery (ОБЯЗАТЕЛЬНЫЙ)

1. Сканируй существующие универсальные промпты:
   ```bash
   ls docs/ai-agent-prompts/promt-*.md | grep -E "(dump|generator|universal|planner|assessment|optimization)"
   ```
2. Определи: есть ли уже промпт с похожим назначением.
3. Решение:
   - Если **ЕСТЬ** → обновляй **in-place** (без `v2`, `new`, `final`).
   - Если **НЕТ** → переходи к шагу 2.

### Шаг 2: Определение типа и домена

1. Классифицируй промпт (Project Discovery / Planning / Transformation / Operations) — см. таблица 5.2.
2. Определи: к каким типам проектов применимо.
   - Все типы (Backend, Frontend, Mobile, SaaS, Infrastructure, Library, API)?
   - Или subset (например, только Backend + Infrastructure)?
3. Определи workflow chain: какой промпт вызывается ДО, какой ПОСЛЕ.

### Шаг 3: Context7 enrichment (ОБЯЗАТЕЛЬНЫЙ)

1. Определи, какие типы проектов охватывает промпт.
2. Запроси best practices через Context7 MCP для **каждого типа**:
   - Platform-specific docs (iOS, Android, Kubernetes, AWS, etc.)
   - Framework docs (React, FastAPI, Django, etc.)
   - Tool docs (Terraform, Docker, etc.)
3. Убедись, что best practices применимы к **ВСЕМ** типам проектов в scope.

### Шаг 4: Сборка по каноническому скелету

1. Скопируй скелет из раздела 5.
2. Заполни каждый раздел:
   - **Mission Statement:** чёткая роль агента + applicability ко всем проектам.
   - **Контракт:** Universal Prompt Principles (краткий).
   - **Project-Agnostic Context:** примеры для Backend, Frontend, Mobile, SaaS, Infra, Library, API.
   - **Шаги 0–N:** 5-8 шагов, Context7 обязательно один из них.
   - **Чеклист:** 10-20 пунктов, generic и переиспользуемые.
   - **Связанные промпты:** cross-links на другие универсальные промпты.
3. **ВАЖНО:** Не включай CodeShift-специфичные паттерны (K8s, Helm, Telegram Bot, ADR, etc.).
4. Используй **аналогии и примеры** для каждого типа проекта.

### Шаг 5: Валидация (ОБЯЗАТЕЛЬНЫЙ)

Прогони каждый quality gate:

| Gate | Проверка | Как |
|------|----------|-----|
| A | Project-agnostic дизайн | Нет K8s, Helm, Telegram Bot, CodeShift-специфичных паттернов |
| B | Applicability широкая | Работает с Backend, Frontend, Mobile, SaaS, Infrastructure, Library, API |
| C | Context7 использован | Шаг Context7 присутствует + примеры для разных типов проектов |
| D | Примеры адаптации | Примеры того, как промпт адаптируется к разным стекам |
| E | Best practices 2026 | Используются современные подходы (Diátaxis, DORA, etc.) |
| F | Нет hardcoded tools | Не предполагаются specific frameworks/libraries |
| G | Нет CodeShift-инвариантов | Нет ссылок на ADR, Telegram Bot, Kubernetes, Helm как обязательные |
| H | Нет дублирования | Промпт не дублирует существующий универсальный |

### Шаг 6: Сохранение и регистрация

1. Naming convention: `docs/ai-agent-prompts/promt-<purpose>.md`
2. Установи `**Version:** 1.0` и текущую дату.
3. В header добавь `**Applicability:** Any project type (Backend, Frontend, Mobile, SaaS, Infrastructure, Library, API)`
4. Обнови `docs/ai-agent-prompts/README.md`:
   - Добавь запись в таблицу «Universal Prompts».
   - Добавь описание в секцию универсальных промтов.
   - Обнови Changelog в шапке README.

---

## 7) Workflow: обновление существующего универсального промпта

### 7.1. Триггеры

- Обновление best practices в 2026 году
- Новые типы проектов или стеков
- Обнаружение противоречий между универсальными промтами
- Запрос пользователя на расширение applicability

### 7.2. Процесс

1. **Сканирование:** проверь соответствие Universal Prompt Principles.

```bash
# Проверка обязательных блоков универсального промпта
for f in docs/ai-agent-prompts/promt-*.md; do
  echo "=== $(basename "$f") ==="
  grep -c "Project-agnostic\|Any project\|Applicability" "$f"
  grep -c "Context7" "$f"
  grep -c "Backend, Frontend, Mobile" "$f"
done
```

2. **Обновление in-place:** сохрани уникальный контент, обнови стандартные блоки.
3. **Версионирование:**
   - Patch (1.0 → 1.1): исправление формулировок, обновление примеров.
   - Minor (1.0 → 2.0): новые шаги, расширение applicability.

---

## 8) Правила именования универсальных промтов

```
docs/ai-agent-prompts/promt-<domain>[-<sub-domain>].md

Примеры:
- promt-project-stack-dump.md           ✅
- promt-mvp-baseline-generator-universal.md  ✅ (с суффиксом -universal для ясности)
- promt-tech-debt-assessment.md         ✅
- promt-performance-optimization.md     ✅
- promt-team-retrospective.md           ✅

Anti-patterns:
- promt-codeshift-something.md          ❌ (не универсальный)
- promt-k8s-specific.md                 ❌ (специфичный для одной технологии)
```

---

## 9) Integration с CodeShift-prompts

Универсальные промпты **комплементарны**, а не конкурентны к CodeShift-зависимым:

| Сценарий | Workflow |
|----------|----------|
| Работаю с CodeShift | `meta-promt-prompt-generation.md` (CodeShift-специфичные) |
| Работаю с любым проектом | `meta-promt-universal-prompt-generator.md` (этот файл) |
| Нужна полная верификация CodeShift | `meta-promt-adr-system-generator.md` (Source of Truth) |

---

## 10) Граф зависимостей универсальных промтов

```mermaid
graph TD
    GEN_UNIV["meta-promt-universal-<br/>prompt-generator.md<br/>(Фабрика универсальных)"]
    
    subgraph "Universal Prompts"
        PSD["promt-project-<br/>stack-dump.md"]
        MVP_U["promt-mvp-<br/>baseline-generator-<br/>universal.md"]
        TDA["promt-tech-<br/>debt-assessment.md<br/>(Planned)"]
        MP["promt-migration-<br/>planner.md<br/>(Planned)"]
        PO["promt-performance-<br/>optimization.md<br/>(Planned)"]
        TR["promt-team-<br/>retrospective.md<br/>(Planned)"]
    end

    GEN_UNIV -->|генерирует| PSD
    GEN_UNIV -->|генерирует| MVP_U
    GEN_UNIV -->|генерирует| TDA
    GEN_UNIV -->|генерирует| MP
    GEN_UNIV -->|генерирует| PO
    GEN_UNIV -->|генерирует| TR

    PSD -->|input for| MVP_U
    MVP_U -->|leads to| TDA
    TDA -->|input for| MP
    MP -->|results in| PO
    PO -->|collected in| TR

    style GEN_UNIV fill:#ffd43b,stroke:#f59f00
    style PSD fill:#74c0fc,stroke:#339af0
    style MVP_U fill:#74c0fc,stroke:#339af0
    style TDA fill:#b3e5fc,stroke:#039be5
    style MP fill:#b3e5fc,stroke:#039be5
    style PO fill:#b3e5fc,stroke:#039be5
    style TR fill:#b3e5fc,stroke:#039be5
```

---

## 11) Примеры: Адаптация промпта под разные проекты

### Edge Case 1: Backend проект (REST API + PostgreSQL)

**Input:** Backend REST API проект на FastAPI + PostgreSQL
**Project Context:**
- Type: Backend API
- Stack: Python 3.10, FastAPI, PostgreSQL 14, Docker, pytest
- Team: 3 разработчика
**Применение`promt-project-stack-dump.md`:**
- Database section: PostgreSQL-специфичные паттерны
- API section: REST endpoint design patterns
- Testing section: pytest fixtures, integration tests
**Применение `promt-mvp-baseline-generator-universal.md`:**
- Tech Baseline: FastAPI, SQLAlchemy, Pydantic
- Deployment: Docker, Docker Compose or basic K8s

### Edge Case 2: Mobile проект (React Native)

**Input:** Mobile app на React Native + Firebase
**Project Context:**
- Type: Mobile (Cross-platform)
- Stack: React Native, Firebase, Jest, Expo
- Team: 2 разработчика
**Применение `promt-project-stack-dump.md`:**
- Frontend section: React Native components, navigation
- Database section: Firebase Firestore schemas
- Testing section: React Native Testing Library, Jest mocks
**Применение `promt-mvp-baseline-generator-universal.md`:**
- Tech Baseline: React Native, Expo, Firebase
- Deployment: App Store / Play Store requirements

### Edge Case 3: Infrastructure проект (Terraform + AWS)

**Input:** Infrastructure-as-Code проект на Terraform
**Project Context:**
- Type: Infrastructure
- Stack: Terraform, AWS, Python scripting, GitHub Actions
- Team: 1-2 DevOps engineer
**Применение `promt-project-stack-dump.md`:**
- Infrastructure section: Terraform modules, AWS services
- CI/CD section: GitHub Actions workflows
- Testing section: Terratest, tftest
**Применение `promt-mvp-baseline-generator-universal.md`:**
- Tech Baseline: Terraform, AWS provider, Ansible
- Deployment: Apply via CI/CD pipeline

---

## 12) Критерий завершения

Генерация/обновление универсального промпта завершена, когда:

- [ ] Промпт соответствует каноническому скелету (раздел 5)
- [ ] Тип промпта определён (Discovery / Planning / Transformation / Operations)
- [ ] Applicability указано (какие типы проектов охватывает)
- [ ] Quality gates A–H пройдены (раздел 6, шаг 5)
- [ ] Context7 использован с примерами для разных проектов
- [ ] Нет CodeShift-специфичных паттернов (K8s, Helm, ADR, Telegram Bot)
- [ ] Файл сохранён по naming convention: `promt-<domain>.md`
- [ ] `docs/ai-agent-prompts/README.md` обновлён (добавлена секция Universal Prompts)
- [ ] Нет файлов-дублей

---

## Связанные документы

| Документ | Путь | Назначение |
|----------|------|-----------|
| CodeShift Meta-Prompt | `docs/ai-agent-prompts/meta-promptness/meta-promt-prompt-generation.md` | Генерация CodeShift-специфичных промтов |
| Source of Truth (CodeShift) | `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md` | ADR инварианты CodeShift |
| Universal Prompts Guide | THIS FILE | Генерация универсальных промтов |
| AI Prompts README | `docs/ai-agent-prompts/README.md` | Регистр всех промтов |
| Project Rules | `docs/rules/project-rules.md` | Общие правила CodeShift |

---

## Ресурсы

| Ресурс | Путь | Назначение |
|---|---|---|
| **CodeShift Meta** | `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md` | CodeShift-специфичный контроль |
| **CodeShift generator** | `docs/ai-agent-prompts/meta-promptness/meta-promt-prompt-generation.md` | CodeShift промпты |
| **Prompts registry** | `docs/ai-agent-prompts/README.md` | Все промпты и версии |
| **Best practices** | `docs/official_document/` | **READ-ONLY** эталон |
| **Project rules** | `.github/copilot-instructions.md` | General CodeShift rules |
| **Documentation** | `docs/` | All documentation |
| **Source control** | `.roo/` | Prompt agents rules |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|----------|
| 1.1 | 2026-03-06 | Добавлены секции Gate I: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`. |
| 1.0 | 2026-02-27 | Первая версия: фабрика project-agnostic промптов. |

---

**Meta-Prompt Version:** 1.1
**Author:** AI Agent (Context7-assisted)
**Date:** 2026-02-27
**Type:** Meta-Prompt (Factory for Universal Prompts)
