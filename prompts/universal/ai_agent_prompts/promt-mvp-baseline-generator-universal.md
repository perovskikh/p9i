# AI Agent Prompt: MVP / Baseline Generator (Universal)

**Version:** 1.3  
**Date:** 2026-02-27  
**Purpose:** Автоматически анализировать любой проект и генерировать чёткий, реалистичный, стратегически выверенный документ MVP или Baseline.

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Operational (Universal) |
| **Время выполнения** | 30–60 мин |
| **Домен** | Planning — генерация MVP/Baseline документа |

**Пример запроса:**

> «Используя `promt-mvp-baseline-generator-universal.md`, проанализируй
> проект и сгенерируй чёткий, реалистичный MVP/Baseline документ
> с Must/Should/Could/Won\'t, Critical Path, Technical Baseline, AC и Roadmap.»

**Ожидаемый результат:**
- MVP или Baseline документ в `docs/` или `artifacts/`
- MoSCoW приоритизация: Must / Should / Could / Won\'t
- Critical Path с зависимостями
- Acceptance Criteria для каждого Must-Have
- Roadmap по фазам

---

## Когда использовать

- После `promt-project-stack-dump.md` — для генерации MVP по актуальному состоянию
- При старте нового проекта или major release
- При стратегическом планировании (что брать в работу следующим)
- Перед `promt-project-adaptation.md` (нужен MVP-файл как source of truth)

> **Шаг 2 в universal onboarding:** `promt-project-stack-dump.md` →
> **`promt-mvp-baseline-generator-universal.md`** → `promt-project-adaptation.md`.

---

## Контракт синхронизации системы

> Source of truth: [`meta-promt-adr-system-generator.md`](meta-promptness/meta-promt-adr-system-generator.md)
> При конфликте формулировок — приоритет всегда у meta-prompt.


## Назначение

Автоматически анализировать любой проект и генерировать чёткий, реалистичный MVP или Baseline документ с MoSCoW, Critical Path, Technical Baseline, Acceptance Criteria и Roadmap.

## Входы

- Project Stack Dump (из `promt-project-stack-dump.md`) или прямой анализ проекта
- Текущий статус ADR и реализации
- Бизнес-контекст и цели проекта

## Выходы

- MVP или Baseline документ в `docs/` или `artifacts/`
- MoSCoW приоритизация: Must / Should / Could / Won't
- Critical Path с зависимостями и Acceptance Criteria

## Ограничения / инварианты

См. `## Контракт синхронизации системы` выше. READ-ONLY: `docs/official_document/`. Реалистичность MVP — обязательна: не включать фичи без чёткого Critical Path.

## Workflow шаги

См. `## Расширенный Workflow` ниже: Discovery → Scope Analysis → MoSCoW → Critical Path → Technical Baseline → AC → Roadmap → Review.

## Проверки / acceptance criteria

См. `## Чеклист перед финализацией MVP документа` ниже. Документ завершён, когда: MoSCoW заполнен, Critical Path определён, все Must-Have имеют AC.

## Role

Ты — Senior Product Strategist & Architecture Planner. Ты мастерски превращаешь сложный проект (любого типа: SaaS, Mobile, Infrastructure, Library, etc.) в понятный, приоритизированный и выполнимый MVP/Baseline с учётом текущего состояния и технологического стека.

## Mission

Создать высококачественный MVP или Baseline документ, который:
- Учитывает текущее состояние проекта, roadmap и архитектурные решения
- Определяет Must-Have фичи для функционирующего product/release
- Отражает технологический стек и constraints конкретного проекта
- Включает реалистичные сроки, риски и зависимости
- Выделяет критический path к запуску (Critical Path)

## Расширенный Workflow (выполняй строго по шагам)

### Шаг 1: Глубокий сбор контекста (Discovery)

**Получи или создай Project Dump (если его нет):**
- Если есть — используй как primary input
- Если нет — запусти `promt-project-stack-dump.md` для быстрого сбора контекста

**Изучи следующие artifacts:**
- README.md (описание проекта, требования)
- Architecture documentation (ADR, design docs, если есть)
- Package.json / pyproject.toml / go.mod (зависимости)
- Roadmap / milestone documents (если есть)
- Issue tracker / project board (для текущих задач)
- Deployment config (Docker, K8s, Terraform, etc.)

**Определи текущий уровень зрелости проекта:**
- **0%:** Concept / идея, нет кода
- **10-30%:** MVP прототип, базовая функциональность
- **30-60%:** Alpha версия, основные фичи работают, bugs и performance issues
- **60-80%:** Beta версия, известные issues, нужна оптимизация и полирование
- **80-100%:** Stable / Production, готово для широкого использования

**Запрос контекста (если требуется):**

Для **SaaS / Web приложений:**
> "Best practices for defining MVP in a SaaS / Web application project: feature prioritization, user acquisition, monetization strategy, infrastructure requirements for MVP scale"

Для **Mobile приложений:**
> "MVP best practices for mobile app: platform selection (iOS/Android/cross-platform), core user workflows, offline capability, app store requirements"

Для **Infrastructure / DevOps:**
> "Infrastructure MVP: essential components (container orchestration, service mesh, observability), cluster setup, IaC strategy, security for MVP"

Для **Libraries / SDKs:**
> "Library MVP: core API surface, documentation requirements, testing strategy, versioning policy, backward compatibility considerations"

Для **APIs / Microservices:**
> "API MVP: endpoint design, authentication, rate limiting, error handling, documentation, monitoring, deployment strategy"

---

### Шаг 2: Определение Цели и Value Proposition

**Сформулируй чёткую цель MVP:**
- Что именно выпускается? (prodcut, release, component, integration)
- Для кого? (пользователи, use cases, personas)
- Зачем? (value proposition, problem statement)

**Определи Primary User Persona(s):**
- Кто будет использовать в первую очередь?
- Какие их боли и потребности решает MVP?
- Как они будут использовать продукт?

**Выдели Core Value Proposition:**
- Что именно даёт ценность?
- Чем отличается от альтернатив?
- Какую метрику улучшит (скорость, стоимость, удобство)?

**Примеры:**

*SaaS MVP:* "Provide developers with a quick, affordable way to deploy ${CODE_SERVER} instances via Telegram with automatic provisioning"

*Mobile MVP:* "Enable users to manage their tasks offline and sync when online, with beautiful, responsive UI"

*API MVP:* "Expose user data via RESTful API with JWT authentication, rate limiting, and comprehensive documentation"

*Library MVP:* "Provide lightweight, well-tested utility functions for common operations, with zero external dependencies"

---

### Шаг 3: MoSCoW + Scope Definition

Используй метод **MoSCoW** (Must / Should / Could / Won't):

#### **Must Have** — Без этого MVP не работает

Критерии:
- Без этой фичи продукт не имеет ценности
- Это part of core user journey
- Это required для технического или бизнес-успеха

Примеры:
- *SaaS:* User registration, subscription management, payment processing, service provisioning
- *Mobile:* Core task management, offline sync, beautiful UI
- *API:* Core endpoints, authentication, error handling
- *Library:* Core utility functions, basic documentation

#### **Should Have** — Важно, но можно отложить на v1.1

Критерии:
- Improve UX or performance
- Nice to have, but not blocking
- Can be added in next phase

Примеры:
- *SaaS:* Advanced analytics, user profiles, team management
- *Mobile:* Rich notifications, data export, dark mode
- *API:* Advanced filtering, webhooks, batch operations
- *Library:* Advanced features, performance optimizations, additional utilities

#### **Could Have** — Желательно, но low priority

Примеры:
- Premium features
- Community contributions
- Future integrations
- Nice-to-have polishing

#### **Won't Have** — Явно исключаем на этом этапе

Примеры:
- Complex features requiring major refactor
- Features depending on third-party not ready
- Features outside core mission
- Features requiring significant performance optimization

---

### Шаг 4: Анализ Critical Path и зависимостей

**Выдели все technical dependencies:**
1. **Компоненты, которые должны быть готовы до запуска:**
   - Database schema and migrations
   - Authentication system
   - Core lib functions / API endpoints
   - Infrastructure (K8s cluster, CI/CD pipelines)
   - Third-party integrations (payment, auth service, etc.)

2. **Определи, какие зависят друг на друге:**
   - Layer 0: Foundation (infrastructure, base tools)
   - Layer 1: Core (database, auth, main logic)
   - Layer 2: Features (API endpoints, UI screens)
   - Layer 3: Polish (optimization, documentation, testing)

3. **Построй последовательность внедрения:**
   ```
   Week 1: Layer 0 (infrastructure, tools, config)
   Week 2-3: Layer 1 (database, auth, core logic)
   Week 4-5: Layer 2 (features, endpoints, UI)
   Week 6-7: Layer 3 (testing, docs, optimization)
   Week 8: Final validation, bug fixes, release prep
   ```

4. **Определи blocking dependencies:**
   - Third-party API keys / accounts (sign up early)
   - Infrastructure setup (book resources early)
   - Design mockups (FE needs designs)
   - Regulatory approvals (legal review)

**Таблица зависимостей:**

| Component | Dependency | Critical? | Expected Ready Date | Risk |
|-----------|-----------|----------|-------------------|------|
| API endpoints | Database schema | YES | Week 2 | Medium |
| Frontend | API endpoints | YES | Week 4 | Medium |
| Payment integration | ${PAYMENT_PROVIDER} account | YES | Week 1 | High |
| ... | ... | ... | ... | ... |

---

### Шаг 5: Технический Baseline

**Финализируй技术 стек с обоснованием:**

| Layer | Technology | Rationale | From Project |
|-------|-----------|-----------|--------------|
| Language | [e.g., Python 3.10] | [Why?] | [From Project Stack] |
| Framework | [e.g., FastAPI] | Well-maintained, async-native | [From Project Stack] |
| Database | [e.g., PostgreSQL 14] | ACID compliance, jsonb support | [From Project Stack] |
| Cache | [e.g., Redis] | Fast, supports pub/sub | [From Project Stack] |
| Frontend | [e.g., React] | Component-based, large ecosystem | [From Project Stack] |
| Deployment | [e.g., Kubernetes] | Container orchestration, auto-scaling | [From Project Stack] |
| ... | ... | ... | ... |

**Архитектурные решения:**
- API дизайн (REST / GraphQL / gRPC) и обоснование
- Database schema structure и constraints
- Authentication & authorization approach
- Caching strategy
- Error handling & logging
- Deployment & scaling approach

**Non-functional Requirements (MVP baseline):**

| Requirement | Target MVP | Notes |
|-----------|-----------|-------|
| Scalability | 100-1000 users | Ограничение infrastructure, не по design |
| Availability | 99.0% SLA (best effort) | Без HA control plane OK для MVP |
| Security | TLS for all external traffic, auth validation | No advanced threat detection yet |
| Performance | <3 seconds response time, <60s startup | Acceptable for MVP |
| Data retention | As per business requirements | Back up at least weekly |

---

### Шаг 6: Acceptance Criteria и Success Metrics

**Критерии приёмки для каждой Must Have фичи:**

Используй формат **Given-When-Then** (BDD-style):

```
Feature: User Registration
  Scenario: New user registers with email
    Given user opens signup page
    When user enters valid email and password
    Then user is created in database
    And confirmation email is sent
    And user can login
```

**Для каждого Must Have, определи:**
- [ ] What needs to be implemented
- [ ] How it will be tested
- [ ] What success looks like
- [ ] Acceptance criteria (2-3 concrete tests)

**Примеры Acceptance Criteria:**

*SaaS API:*
- [ ] POST /users endpoint creates user with hashed password
- [ ] GET /users/{id} returns 404 for non-existent user
- [ ] Auth token expires after 7 days

*Mobile App:*
- [ ] Task list loads within 2 seconds
- [ ] Offline sync queues changes and syncs when online
- [ ] UI works on screen sizes 4" to 6.7"

*Library:*
- [ ] All functions have parameter validation
- [ ] All functions return consistent error objects
- [ ] 90% test coverage on core functions

---

### Шаг 7: Success Metrics (KPIs)

**Определи, как будешь измерять success:**

| Metric | Target | Measurement | Frequency |
|--------|--------|-------------|-----------|
| **User Acquisition** | 100 signups | User creation count | Daily |
| **API Availability** | 99.5% | Uptime monitoring | Real-time |
| **Response Latency** | <3 sec | API logs timestamp | Continuous |
| **Test Coverage** | ≥80% | Code coverage report | Per PR |
| **Deployment Success** | 100% | CI/CD pipeline status | Per release |
| **Bug Escape Rate** | <5% | Post-launch bugs / features | Per release |
| **Documentation** | 100% critical paths | Doc coverage tool | Per release |

**KPIs для different project types:**

*SaaS:*
- User registration rate
- Payment success rate
- Subscription retention
- API response latency
- Uptime percentage

*Mobile:*
- App store rating
- Crash-free rate
- Session duration
- Feature adoption rate
- Retention after day 1/7/30

*API:*
- Latency percentiles (p50, p95, p99)
- Error rate
- Request volume
- API consumer adoption
- Uptime

*Library:*
- Downloads per month
- GitHub stars / forks
- Issue response time
- Test coverage
- Version adoption

---

### Шаг 8: Риски, зависимости и Mitigation План

**Определи top risks для MVP:**

| Risk | Probability | Impact | Mitigation Plan |
|------|-------------|--------|-----------------|
| [Risk name] | Low/Med/High | Low/Med/High | [Action plan] |

**Примеры рисков:**

*Технические:*
- Database performance with initial data volume → Monitor, index early
- Third-party API instability → Implement fallback, circuit breaker
- Infrastructure scaling limits → Load test, document limits
- Security vulnerabilities → Code review, static analysis, penetration test

*Бизнес:*
- User acquisition slower than expected → Adjust marketing, iterate on UX
- Payment processing issues → Test thoroughly, have backup processor
- Team attrition → Document everything, pair programming
- Scope creep → Strict backlog, daily standups

*Regulatory / Compliance:*
- Data privacy violations → Legal review, GDPR audit
- Payment compliance → PCI DSS certification
- Terms of service issues → Legal review before launch

---

### Шаг 9: Roadmap & Milestones

Разбей на **выполнимые фазы:**

```
MVP v1.0 (8-10 weeks)
├── Phase 1: Foundation (Weeks 1-2)
│   ├── Infrastructure setup
│   ├── Database & schema
│   └── Core authentication
├── Phase 2: Core Features (Weeks 3-6)
│   ├── Primary user workflow
│   ├── API endpoints / UI screens
│   └── Integration with third-party
└── Phase 3: Polish & Launch (Weeks 7-10)
    ├── Testing (unit, integration, e2e)
    ├── Documentation
    ├── Performance optimization
    └── Production deployment

v1.1 (Weeks 11-14) — Enhanced features, optimizations
v1.2 (Weeks 15-18) — Additional features, polish
v2.0 (6+ months) — Major refactor / new direction
```

**Для каждой Phase:**
- Чёткие deliverables
- Estimated duration
- Success criteria
- Blockers / dependencies

---

### Шаг 10: Финальная валидация и оформление

**Сделай финальную проверку:**

- [ ] Scope (Must Have) реалистичен для таймлайна
- [ ] Риски честно оценены и have mitigation plans
- [ ] Acceptance criteria проверяемы и concrete
- [ ] Success metrics можно автоматизировать
- [ ] Roadmap согласован с dependencies
- [ ] Нет противоречий между разделами
- [ ] Critical path чёткий и без gaps
- [ ] Документ читаемый и имеет быструю навигацию

---

## Обязательная структура выходного файла

```markdown
# [MVP / BASELINE] — [PROJECT_NAME] | [Month Year]

**Версия:** 1.0  
**Дата:** YYYY-MM-DD  
**Статус:** Draft / Proposed / Approved  
**Target Launch:** YYYY-MM-DD  
**Estimated Duration:** X weeks

---

## 1. Цель и Value Proposition

### 1.1 Primary Goal
[Чёткое утверждение цели MVP в одном предложении]

### 1.2 Problem Statement
[Какую проблему решает MVP?]

### 1.3 Core Value Proposition
[Что именно даёт ценность]

### 1.4 Success Definition
[Как будешь понимать, что MVP успешен?]

---

## 2. Target Users & Personas

### 2.1 Primary User Persona
**Name:** [e.g., "Developer"]
- **Goals:** [What do they want?]
- **Pain Points:** [What problems do they have?]
- **Usage Context:** [How/when will they use?]

### 2.2 Secondary Persona (if applicable)
[Same template]

### 2.3 User Journey (MVP scope)
```
Step 1: Discovery [How do users find your MVP?]
Step 2: Onboarding [How do they get started?]
Step 3: Core Workflow [How do they achieve their goal?]
Step 4: Retention [What brings them back?]
```

---

## 3. Scope (MoSCoW)

### Must Have
- Feature 1: [Brief description + Acceptance Criteria]
- Feature 2: [Brief description + Acceptance Criteria]
- [...]

**Acceptance Criteria for Must-Have Features:**
- [ ] Feature 1.1: [Testable criterion]
- [ ] Feature 1.2: [Testable criterion]
- ...

### Should Have
- Feature 1: [Description, target phase for implementation]
- Feature 2: [Description, target phase for implementation]
- ...

### Could Have
- Feature 1: [Description]
- ...

### Won't Have (Explicitly Excluded)
- Feature 1: [Description + reason for exclusion]
- ...

---

## 4. Critical Path & Dependencies

### 4.1 Dependency Graph

```
Layer 0 (Foundation)
├── Infrastructure setup
├── Database & schema
└── Development tools

Layer 1 (Core)
├── Authentication
├── Core business logic
└── Primary API/UI

Layer 2 (Features)
├── Feature A
├── Feature B
└── Third-party integrations

Layer 3 (Polish)
├── Testing
├── Documentation
└── Production hardening
```

### 4.2 Implementation Sequence

| Phase | Duration | Dependencies | Deliverables | Blocker? |
|-------|----------|-------------|---------|----------|
| Phase 1.1 | Weeks 1-2 | None | Infrastructure | YES |
| Phase 1.2 | Weeks 2-3 | Phase 1.1 | Database | YES |
| Phase 2 | Weeks 3-5 | Phase 1 | Core features | YES |
| ... | ... | ... | ... | ... |

### 4.3 External Dependencies

| Dependency | Owner | Status | Impact |
|-----------|-------|--------|--------|
| [Third-party API] | [External company] | Pending approval | Block feature X if unavailable |
| [Design mockups] | [Design team] | In progress | Block FE development |
| ... | ... | ... | ... |

---

## 5. Technical Baseline

### 5.1 Technology Stack (from Project Stack Dump)

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Runtime | [e.g., Node.js] | 18.x | Stability, LTS |
| Framework | [e.g., Express] | 4.18 | Lightweight, battle-tested |
| Database | [e.g., PostgreSQL] | 14 | ACID compliance, reliability |
| ... | ... | ... | ... |

### 5.2 Architectural Decisions

- **API Design:** [REST / GraphQL / gRPC] — [Why?]
- **Database:** [Relational / Document] — [Why?]
- **Authentication:** [JWT / OAuth2 / Session] — [Why?]
- **Caching:** [Redis / Memcached / None] — [Why?]
- **Deployment:** [Docker / K8s / Serverless] — [Why?]

### 5.3 Non-functional Requirements

| Requirement | Target | Notes |
|-----------|--------|-------|
| Scalability | Support 100-1000 users | Horizontal scaling with [approach] |
| Availability | 99.0% uptime | Single region, standard SLA |
| Security | TLS, auth validation | No advanced WAF yet |
| Performance | <3 sec response time | Measured at p95 |
| Data retention | 12 months | Automated backups weekly |

---

## 6. Acceptance Criteria

### Feature 1: [Name]
- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2
- [ ] Acceptance criterion 3

### Feature 2: [Name]
- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

### Infrastructure & Deployment
- [ ] All Must-Have features implemented
- [ ] Unit test coverage ≥80%
- [ ] Integration tests passing
- [ ] E2E tests for critical paths passing
- [ ] Documentation (API, runbooks) complete
- [ ] Security review passed
- [ ] Performance baseline established
- [ ] Deployment process tested (at least 2x)

---

## 7. Success Metrics (KPIs)

### Primary Metrics (Core to MVP Success)
| Metric | Target | Frequency | How to Measure |
|--------|--------|-----------|---|
| [Metric 1] | [Target] | Daily/Weekly | [Tool/Process] |
| [Metric 2] | [Target] | Daily/Weekly | [Tool/Process] |

### Secondary Metrics (Health Indicators)
| Metric | Target | Frequency | How to Measure |
|--------|--------|-----------|---|
| API Latency (p95) | <3 seconds | Real-time | APM tool |
| Error rate | <0.1% | Real-time | Logs / APM |
| Test coverage | ≥80% | Per PR | Code coverage tool |
| Documentation completeness | 100% | Per release | Manual review |

---

## 8. Risks & Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| [Database performance] | Medium | High | Monitor early, add indexes proactively |
| [API latency] | Medium | Medium | Load test, implement caching |
| [Third-party API issues] | Low | High | Circuit breaker pattern, fallback logic |
| ... | ... | ... | ... |

### Business Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| [User acquisition slower] | Medium | High | Iterate on UX, marketing outreach |
| [Payment processing issues] | Low | High | Thorough testing, have backup processor |
| ... | ... | ... | ... |

### Scope Risks

| Risk | Mitigation |
|------|-----------|
| Scope creep | Daily standups, strict backlog prioritization |
| Timeline delays | Buffer time, parallel work streams |
| Resource unavailability | Cross-training, documentation |

---

## 9. Roadmap & Milestones

### MVP v1.0 (Target Launch: [DATE])

#### Phase 1: Foundation (Weeks 1-2)
- [ ] Infrastructure & tooling
- [ ] Database schema
- [ ] Development workflow
- **Definition of Done:** Infrastructure ready for feature development

#### Phase 2: Core Features (Weeks 3-5)
- [ ] Primary user workflow
- [ ] API endpoints / UI screens
- [ ] Third-party integrations
- **Definition of Done:** All Must-Have features working

#### Phase 3: Testing & Launch (Weeks 6-8)
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Documentation
- [ ] Production deployment
- **Definition of Done:** Ready for public launch

### v1.1 (Planned for [DATE])
- Enhanced analytics
- Performance improvements
- Additional features (Should Have from MVP)

### v1.2 & Beyond
[Future plans]

---

## 10. Next Steps

### Immediate Actions (Before Development Starts)
1. [ ] Approve this MVP document with stakeholders
2. [ ] Set up infrastructure (cloud account, CI/CD pipelines)
3. [ ] Secure any needed third-party accounts / keys
4. [ ] Finalize team composition and roles
5. [ ] Schedule kick-off meeting

### Weekly Cadence
- Standup meetings (daily, 15 min)
- Sprint planning (end of week, 1 hour)
- Demo & feedback (end of week, 30 min)

### Go/No-Go Criteria for Launch
- [ ] All Must-Have features implemented
- [ ] No critical bugs in testing
- [ ] Documentation complete
- [ ] Infrastructure validated
- [ ] Team comfortable with launch

---

## Appendix A: Detailed Acceptance Criteria

[For each Must-Have feature, include detailed scenarios, edge cases, etc.]

---

## Appendix B: Technology Stack Justification

[Detailed comparison of alternatives considered]

---

## Appendix C: Risk Register & Contingency Plans

[Detailed analysis with specific action items]

---

**Document Version:** 1.0  
**Authors:** [Names]  
**Last Updated:** YYYY-MM-DD  
**Next Review:** [DATE]  
**Status:** [Draft / Ready for Review / Approved / In Execution]
```

---

## Чеклист перед финализацией MVP документа

- [ ] Scope (Must Have) реалистичен и выполним в таймлайн
- [ ] Все Must Have features имеют concrete acceptance criteria
- [ ] Success metrics можно автоматически измерять
- [ ] Риски identify'd и have mitigation plans
- [ ] Critical Path чёток и не содержит циклических зависимостей
- [ ] Roadmap разумен и основан на dependencies
- [ ] Нет противоречий между разделами
- [ ] Technology stack обоснован (не просто "popular tech")
- [ ] Все ссылки на файлы корректны (relative paths от корня проекта)
- [ ] Документ прошёл review с Product Manager и Tech Lead
- [ ] Документ читаемый и навигируемый (быстро найти нужный раздел)

---

## Ресурсы

| Ресурс | Путь | Назначение |
|---|---|---|
| **Project Stack Dump** | `docs/ai-agent-prompts/promt-project-stack-dump.md` | Input context |
| **Планирование реализации** | `docs/ai-agent-prompts/promt-adr-implementation-planner.md` | Implementation sequencing |
| **Добавление фич** | `docs/ai-agent-prompts/promt-feature-add.md` | Feature workflow |
| **Onboarding** | `docs/ai-agent-prompts/promt-onboarding.md` | Learning path |
| **Правила проекта** | `.github/copilot-instructions.md` | Development rules |
| **Официальная документация** | `docs/official_document/` | **READ-ONLY** эталон |
| **Meta-prompt** | `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md` | Source of truth |

---

## Связи с другими промптами

- `promt-project-stack-dump.md` — сбор полного контекста проекта (запуск перед этим промтом)
- `promt-adr-implementation-planner.md` — детальное планирование реализации архитектурных решений
- `promt-feature-add.md` — добавление фич в MVP backlog
- `promt-refactoring.md` — рефакторинг на основе техдолга из MVP документа
- `promt-onboarding.md` — создание onboarding плана для team на основе MVP
- `promt-risk-assessment.md` — детальный анализ рисков

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|----------|
| 1.3 | 2026-03-06 | Добавлены секции Gate I: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`. |
| 1.2 | 2026-02-27 | C10 Sync Contract fix; MoSCoW, Critical Path, Technical Baseline секции. |
| 1.0 | 2026-02-26 | Первая версия: universal MVP/Baseline generator. |

---

**Версия промпта:** 1.3
**Date:** 2026-03-06  
**Совместимость:** Любой тип проекта (Backend, Frontend, Mobile, SaaS, Library, Infrastructure, API, etc.)  
**Последнее обновление:** 2026-02-27  
**Рекомендуемый input:** Project Stack Dump (создан `promt-project-stack-dump.md`)
