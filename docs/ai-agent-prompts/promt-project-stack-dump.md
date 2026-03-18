# AI Agent Prompt: Project Stack & Status Dump

**Version:** 1.1
**Date:** 2026-02-27
**Purpose:** Быстро и полностью описать текущее состояние любого проекта: стек, архитектуру, задачи, прогресс, roadmap и зависимости.

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Operational (Universal) |
| **Время выполнения** | 20–40 мин |
| **Домен** | Discovery — дамп состояния проекта |

**Пример запроса:**

> «Используя `promt-project-stack-dump.md`, быстро и полностью опиши
> текущее состояние проекта: стек, архитектуру, задачи, прогресс
> и roadmap для onboarding и стратегического планирования.»

**Ожидаемый результат:**
- Полное описание стека (языки, фреймворки, инфраструктура)
- Текущий статус ADR и реализации
- Roadmap с приоритетами
- Ключевые файлы и точки входа для новых разработчиков

---

## Когда использовать

- В начале сессии с новым проектом — быстрый onboarding
- Перед `promt-mvp-baseline-generator-universal.md` (нужен baseline текущего состояния)
- Для передачи контекста другому AI-агенту
- При стратегическом планировании — актуализировать roadmap

> **Шаг 1 в universal onboarding:** `promt-project-stack-dump.md` →
> `promt-mvp-baseline-generator-universal.md` → `promt-project-adaptation.md`.

---

## Контракт синхронизации системы

> Source of truth: [`meta-promt-adr-system-generator.md`](meta-promptness/meta-promt-adr-system-generator.md)
> При конфликте формулировок — приоритет всегда у meta-prompt.


## Назначение

Быстро и полностью описать текущее состояние любого проекта: стек, архитектуру, задачи, прогресс и roadmap для onboarding и стратегического планирования.

## Входы

- Исходный код и конфигурация проекта
- ADR-файлы и индекс (`docs/explanation/adr/index.md`)
- CI/CD конфигурация, Makefile, README

## Выходы

- Project Stack & Status Dump документ (Markdown)
- Полное описание стека, архитектуры, статуса ADR, roadmap
- Quick Reference Commands для быстрого старта

## Ограничения / инварианты

См. `## Контракт синхронизации системы` выше. Документ READ-ONLY для `docs/official_document/`. Не изменять ADR-файлы в процессе создания дампа.

## Workflow шаги

См. `## Быстрый Workflow` ниже: структурированный анализ в 12 секциях (Overview → Stack → Architecture → Status → Roadmap).

## Проверки / acceptance criteria

См. `## Checklist перед финализацией Project Dump` ниже. Документ завершён, когда: все 12 обязательных секций заполнены, roadmap актуален, команды проверены.

## Role

Ты — Senior Software Architect & Project Analyst. Твоя задача — за минимальное время собрать полный, структурированный, actionable снимок состояния проекта, пригодный для:
- Onboarding новых членов команды
- Стратегического планирования
- Быстрого понимания проекта другими AI-агентами
- Документирования текущего состояния
- Выявления зависимостей и критических точек

## Mission

Создать **Project Stack & Status Dump** — полную, структурированную, машинно-читаемую опись проекта, которая охватывает:
- Общее описание проекта и его назначение
- Технологический стек (backend, frontend, infrastructure, databases, tools)
- Архитектурные решения и паттерны проектирования
- Структура проекта и ключевые файлы
- Текущий статус реализации (фазы, прогресс, известные проблемы)
- Дорожная карта и планы развития
- Зависимости (внешние, внутренние, третьесторонние)
- Требования к запуску и развертыванию
- Риски и технические долги

## Быстрый Workflow (выполняй в этом порядке)

### Шаг 1: Discover структуру проекта (2-3 мин)
```
Цель: Понять, с каким типом проекта ты имеешь дело.

Действия:
1. Список файлов в корне (README.md, package.json, Chart.yaml, Makefile, etc.)
2. Список primary директорий (src/, app/, infrastructure/, docs/, tests/, etc.)
3. Файл README.md (первые 100 строк) — высокоуровневое описание
4. package.json / pyproject.toml / go.mod (зависимости и базовая инфо)
5. Определить тип проекта:
   - Backend (REST API, GraphQL, gRPC)
   - Frontend (React, Vue, Angular, etc.)
   - Full-stack
   - Infrastructure (Kubernetes, Terraform, Docker, etc.)
   - Library / SDK
   - SaaS платформа
   - Другое (hybrid, multi-component)
```

### Шаг 2: Технологический стек (3-5 мин)
```
Цель: Полностью задокументировать, какие технологии используются.

Заполни таблицу:

| Layer | Component | Technology | Version | Purpose | Notes |
|-------|-----------|-----------|---------|---------|-------|
| **Language/Runtime** | Runtime | Node.js / Python / Go / ... | x.x.x | Core execution | — |
| **Backend Framework** | API / Framework | Express / FastAPI / Gin / ... | x.x.x | API endpoints | — |
| **Frontend** | UI Framework | React / Vue / Angular / ... | x.x.x | User interface | — |
| **Database** | Primary DB | PostgreSQL / MongoDB / ... | 14.0 | Persistent storage | — |
| **Cache** | Caching | Redis / Memcached / ... | 7.0 | Session/query cache | — |
| **Message Queue** | Queue System | RabbitMQ / Kafka / ... | x.x.x | Async jobs | — |
| **Infrastructure** | Container | Docker | 24.0 | Containerization | — |
| **Orchestration** | K8s | Kubernetes / Docker Compose / ... | 1.29 | Pod/container management | — |
| **IaC / Deployment** | Infrastructure | Terraform / Helm / CloudFormation / ... | x.x.x | Infrastructure provisioning | — |
| **CI/CD** | Pipeline | GitHub Actions / GitLab CI / Jenkins / ... | latest | Automated testing & deploy | — |
| **Monitoring** | Observability | Prometheus / Datadog / ELK / ... | x.x.x | Metrics & logs | Optional |
| **Testing** | Test Frameworks | Jest / pytest / Go test / ... | x.x.x | Automated testing | — |
| **Package Manager** | Dependency Mgmt | npm / pip / go mod / ... | latest | Package management | — |
| **Authentication** | Auth | OAuth2 / JWT / SAML / ... | — | User authentication | — |
| **API Documentation** | Docs | Swagger / OpenAPI / Redoc / ... | latest | API spec & UI | — |

Дополнительные инструменты:
- Линтеры: ESLint, pylint, golangci-lint, etc.
- Formatters: Prettier, black, gofmt, etc.
- Static analysis: SonarQube, Bandit, GoMetaLinter, etc.
- Load testing: k6, JMeter, Locust, etc.
```

### Шаг 3: Архитектура и паттерны (3-5 мин)
```
Цель: Описать архитектурные решения и design paттерны.

Вопросы:
1. Архитектурный стиль — микросервисы / монолит / serverless / event-driven / другое?
2. Authentication & Authorization — как реализовано?
3. Database design — схема, миграции, ORM?
4. API дизайн — REST / GraphQL / gRPC / WebSocket?
5. Caching strategy — где и как кешируется?
6. Async processing — job queue / event streaming / background tasks?
7. Error handling & logging — как структурированы сообщения об ошибках?
8. Testing approach — unit / integration / e2e / load testing?
9. Deployment strategy — blue-green / canary / rolling updates?
10. Security measures — HTTPS / CORS / rate limiting / input validation?

Заполни краткую таблицу:
| Area | Pattern / Decision | Rationale |
|------|------------------|-----------|
| Architecture | [Monolith / Microservices / ...] | [Why?] |
| Auth | [OAuth2 / JWT / ...] | [Why?] |
| Database | [Relational / NoSQL / ...] | [Why?] |
| Caching | [Redis / Memcached / In-memory / ...] | [Why?] |
| ... | ... | ... |
```

### Шаг 4: Структура проекта и ключевые файлы (2-3 мин)
```
Цель: Понять organization кода.

Действия:
1. Перечислить главные директории и их назначение:
   - src/          → source code
   - tests/        → automated tests
   - docs/         → documentation
   - infrastructure/ → K8s, Terraform, Docker, etc.
   - api/          → API contracts/OpenAPI
   - scripts/      → utility scripts
   - config/       → configuration files
   - ...

2. Определить ключевые файлы (которые нужны для понимания проекта):
   - README.md
   - package.json / pyproject.toml / go.mod
   - Dockerfile / docker-compose.yml
   - Makefile / Taskfile
   - Chart.yaml (if Helm)
   - terraform/ (if Terraform)
   - .github/workflows/ (if GitHub Actions)
   - .env.example
   - config.yaml / settings.json
   - Основные классы/модули (Entry points)

3. Заполни таблицу:
| Path | Purpose | Criticality |
|------|---------|------------|
| src/main.py / index.js | Application entry point | CRITICAL |
| src/api/ | API layer | CRITICAL |
| ... | ... | ... |
```

### Шаг 5: Текущее состояние и прогресс (3-5 мин)
```
Цель: Понять, на каком этапе находится проект.

Определи:
1. Phase/Stage (Concept / Alpha / Beta / Stable / Production / Maintenance)
2. Status каждого major компонента:
   | Component | Status | Progress | Blockers |
   |-----------|--------|----------|----------|
   | Backend API | ✅ Stable | 100% | None |
   | Frontend | 🟡 In Progress | 65% | Design review |
   | Database | ✅ Stable | 100% | None |
   | Infrastructure | ⏳ Planned | 0% | Cloud setup |
   | Testing | 🔴 At Risk | 40% | Coverage gaps |
   | ... | ... | ... | ... |

3. Известные проблемы (Known Issues):
   - Performance bottlenecks
   - Failing tests
   - Technical debt
   - Missing documentation
   - Security concerns
   - Deprecated dependencies

4. Recent milestones и достижения:
   - Latest release date
   - Key features delivered
   - Performance improvements
```

### Шаг 6: Дорожная карта (Roadmap) (2-3 мин)
```
Цель: Понять plans и направление развития.

Структура:
Phase / Quarter | Timeline | Planned Features | Dependencies | Priority
---|---|---|---|---
v1.1 | Q1 2026 | Feature A, Feature B | Library X | High
v1.2 | Q2 2026 | Feature C, Optimization D | Infrastructure ready | Medium
v2.0 | H2 2026 | Major refactor, API v2 | Community feedback | Low
...

Key questions:
1. Какие features запланированы на ближайшие 3-6 месяцев?
2. Есть ли breaking changes или major refactors?
3. Какие dependencies блокируют прогресс?
```

### Шаг 7: Зависимости и интеграции (2-3 мин)
```
Цель: Понять, от чего проект зависит.

Заполни:
1. Внешние services:
   - Cloud provider (AWS / Azure / GCP / DigitalOcean / ...)
   - Third-party APIs (Stripe / Twilio / Auth0 / ...)
   - Hosted services (GitHub / GitLab / Datadog / ...)

2. Внутренние зависимости (если это mono-repo или ecosystem):
   - Other repos/projects
   - Internal libraries
   - Internal services

3. System requirements:
   - Minimum OS version
   - Hardware requirements
   - Network requirements
   - Storage requirements
```

### Шаг 8: Требования к запуску и развертыванию (2-3 мин)
```
Цель: Как быстро поднять проект locally и в production?

Заполни:
1. Local development setup:
   - Prerequisites (Node.js version, Python version, etc.)
   - Installation steps (git clone, npm install, etc.)
   - Run steps (npm start, make dev, docker-compose up, etc.)
   - Expected time to first running state

2. Production deployment:
   - Where it's hosted (AWS, K8s, custom server, etc.)
   - Deployment process (CI/CD, manual, GitOps, etc.)
   - Environment variables required
   - Database migrations
   - Backup & recovery strategy

3. Common operations:
   - How to restart service
   - How to view logs
   - How to troubleshoot
   - How to scale
```

### Шаг 9: Риски и техдолг (2-3 мин)
```
Цель: Понять, что может развалиться.

Определи:
1. Technical Debt:
   - Outdated dependencies
   - Legacy code that needs refactoring
   - Missing test coverage
   - Performance optimization opportunities

2. Risks:
   | Risk | Probability | Impact | Mitigation |
   |------|------------|--------|-----------|
   | [Risk name] | Medium | High | [Plan to reduce] |

3. Missing features:
   - Monitoring & alerting
   - Automated testing
   - Documentation
   - Security hardening
```

### Шаг 10: Финальное форматирование и валидация (1-2 мин)
```
Цель: Убедиться, что dump полный, читаемый и useful.

Проверочный лист:
- [ ] Все разделы заполнены и релевантны
- [ ] Нет placeholder'ов
- [ ] Версии компонентов указаны
- [ ] Ссылки на файлы корректны (relative paths от корня проекта)
- [ ] Таблицы правильно отформатированы
- [ ] Нет конфиденциальной информации (API ключи, пароли)
- [ ] Документ readable и можно быстро навигировать
- [ ] Приложены примеры команд для startup / deployment
```

---

## Обязательная структура выходного документа

```markdown
# Project Stack & Status Dump: [PROJECT_NAME]

**Date:** YYYY-MM-DD  
**Project Type:** [Backend / Frontend / Full-stack / Infrastructure / SaaS / ...]  
**Current Phase:** [Concept / Alpha / Beta / Stable / Production / Maintenance]  
**Repository:** [GitHub/GitLab URL]  
**Primary Language:** [Python / JavaScript / Go / ...]

---

## 1. Project Overview

### 1.1 Description
[Что делает проект в 2-3 предложениях]

### 1.2 Key Features
- Feature 1
- Feature 2
- Feature 3

### 1.3 Target Users / Use Cases
[Кто использует, зачем]

---

## 2. Technology Stack

### 2.1 Core Stack
| Layer | Component | Technology | Version |
|-------|-----------|-----------|---------|
| Language | Runtime | [e.g., Node.js] | 18.x |
| Framework | Backend | [e.g., Express] | 4.x |
| ... | ... | ... | ... |

### 2.2 Infrastructure & DevOps
| Tool | Purpose | Version | Notes |
|------|---------|---------|-------|
| Docker | Containerization | 24.0 | Multi-stage builds |
| Kubernetes | Orchestration | 1.29 | Helm charts in use |
| Terraform | IaC | 1.5 | AWS provider |
| ... | ... | ... | ... |

### 2.3 Additional Tools
- Monitoring: [Prometheus / Datadog / ...]
- CI/CD: [GitHub Actions / GitLab CI / ...]
- Testing: [Jest / pytest / ...]
- Package Manager: [npm / pip / ...]

---

## 3. Architecture & Design Patterns

### 3.1 High-Level Architecture
[Diagram or text description: Monolith vs Microservices, components interaction]

### 3.2 Key Architectural Decisions
| Decision | Implementation | Rationale |
|----------|----------------|-----------|
| Architecture Style | [e.g., RESTful API] | [Why?] |
| Database | [e.g., PostgreSQL] | [Why?] |
| Authentication | [e.g., JWT] | [Why?] |
| ... | ... | ... |

### 3.3 Design Patterns in Use
- [Dependency Injection]
- [Factory Pattern]
- [Observer Pattern]
- ...

---

## 4. Project Structure

### 4.1 Directory Layout
```
project-root/
├── src/              # Application source code
│   ├── api/         # API layer
│   ├── services/    # Business logic
│   └── models/      # Data models
├── tests/           # Test suites (unit / integration / e2e)
├── docs/            # Documentation
├── infrastructure/  # K8s, Terraform, Docker configs
├── scripts/         # Utility scripts
├── config/          # Configuration files
└── README.md        # Project README
```

### 4.2 Critical Files
| File | Purpose | Criticality |
|------|---------|------------|
| `src/main.py` / `index.js` | Application entry point | CRITICAL |
| `package.json` / `pyproject.toml` | Dependencies & metadata | CRITICAL |
| `Docker.prod` / `Chart.yaml` | Deployment config | HIGH |
| `.env.example` | Environment variables template | MEDIUM |
| ... | ... | ... |

---

## 5. Current Status & Progress

### 5.1 Overall Status
- **Phase:** [Stable / In Development / Beta / ...]
- **Stability:** [Production-ready / Experimental / ...]
- **Last Release:** [Date + Version]

### 5.2 Component Status
| Component | Status | Progress | Known Issues |
|-----------|--------|----------|-------------|
| Backend API | ✅ Stable | 100% | None |
| Database | ✅ Stable | 100% | Slow queries on millions |
| Frontend | 🟡 In Progress | 70% | UI responsiveness on mobile |
| Testing | ⏳ Partial | 60% | E2E coverage gaps |
| Documentation | 🟡 Outdated | 50% | Needs API docs refresh |

### 5.3 Known Issues & Technical Debt
| Issue | Severity | Impact | Plan |
|-------|----------|--------|------|
| [Old dependency X version Y] | Medium | Security risks | Upgrade Q1 2026 |
| [Missing tests in module Y] | Low | Maintenance burden | Add in v1.2 |
| [Performance bottleneck in Z] | High | User experience | Optimize in Q2 2026 |

### 5.4 Recent Achievements
- [Milestone 1: Date]
- [Milestone 2: Date]
- [Performance improvement: X% faster]

---

## 6. Roadmap & Milestones

### 6.1 Short-term (Next 3 months)
| Version | Target | Features | Priority |
|---------|--------|----------|----------|
| v1.1 | Q1 2026 | Feature A, Feature B | HIGH |
| v1.2 | Q2 2026 | Feature C, Optimization | MEDIUM |

### 6.2 Long-term (6-12 months)
- v2.0: Major refactor / API redesign
- Feature X: [Description]
- Infrastructure upgrade: [Details]

### 6.3 Blocking Dependencies
- [Dependency 1]: Needed before Feature X
- [Dependency 2]: Scheduled Q2 2026

---

## 7. Dependencies & External Integrations

### 7.1 External Services
| Service | Purpose | Business Model | Risk Level |
|---------|---------|----------------|-----------|
| [Auth0 / Stripe / AWS] | [What for] | [Free/Paid] | [Low/Medium/High] |

### 7.2 Third-party Libraries & Frameworks
[Auto-generated from package.json / pyproject.toml, organized by impact/criticality]

### 7.3 System Requirements
| Requirement | Value | Notes |
|------------|-------|-------|
| Min Node.js version | 18.x | LTS preferred |
| Min RAM (dev) | 4GB | 8GB recommended |
| Min RAM (prod) | 8GB | Scale horizontally |
| Disk space | 50GB | Depends on data volume |
| OS | Ubuntu 22.04+ | MacOS also supported |

---

## 8. Getting Started

### 8.1 Prerequisites
```
- Node.js 18.x (install via nvm)
- Docker 24.0+ (for containerized development)
- PostgreSQL 14+ (for local database)
- Make (for running common tasks)
```

### 8.2 Local Development Setup
```bash
# Clone repository
git clone <repository-url>
cd <project>

# Install dependencies
npm install  # or: pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your local config

# Run database migrations
npm run migrate  # or: make migrate

# Start development server
npm run dev  # or: make dev

# Run tests
npm test  # or: make test

# Expected startup time: ~30 seconds
```

### 8.3 Production Deployment
- **Current hosted on:** [AWS / K8s cluster / etc.]
- **Deployment process:** [CI/CD pipeline / manual / GitOps]
- **Deploy command:** `make deploy-prod` or via GitHub Actions
- **Expected downtime:** [0 minutes (rolling) / ~5 minutes (blue-green)]
- **Database migrations:** [Handled automatically / Manual step required]

---

## 9. Common Operations

### 9.1 Monitoring & Debugging
```bash
# View logs
docker logs <container-id>  # or: kubectl logs <pod>

# Check health
curl https://<domain>/health

# Monitor metrics
# [Prometheus URL / Datadog dashboard / etc.]
```

### 9.2 Scaling & Performance
- **Current capacity:** [X requests/sec, Y concurrent users]
- **Scaling approach:** [Horizontal / Vertical]
- **Performance bottleneck:** [Database queries / API response time / ...]
- **Optimization plan:** [Add caching / Database indexing / API optimization]

### 9.3 Troubleshooting
| Problem | Cause | Solution |
|---------|-------|----------|
| [High memory usage] | [Memory leak in X] | [Restart service / Apply patch] |
| [Slow API response] | [Database query optimization needed] | [Add indexes / Cache results] |

---

## 10. Risks & Technical Debt

### 10.1 Technical Debt
| Item | Severity | Why it matters | Timeline |
|------|----------|---|----------|
| [Old dependency X] | Medium | Security vulnerability | Fix in Q1 2026 |
| [Missing test coverage] | Low | Maintenance burden | Add gradually |
| [Code duplication in Y] | Low | Maintenance difficulty | Refactor in v2.0 |

### 10.2 Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| [Third-party API outage] | Low | Service unavailability | Implement fallback |
| [Database performance degradation] | Medium | Slow queries | Monitor + optimize indexes |
| [Security vulnerability in dependency] | Low | Security breach | Regular audits + patching |

### 10.3 Missing Critical Features
- Monitoring & alerting (needed for production stability)
- API rate limiting (needed for production security)
- Automated database backups (needed for disaster recovery)
- Load testing (needed before scaling)

---

## 11. Quick Reference Commands

### Build & Run
```bash
make setup       # Install dependencies
make dev         # Start development server
make build       # Build for production
make deploy      # Deploy to production
make test        # Run all tests
```

### Database
```bash
make migrate     # Run migrations
make rollback    # Rollback migrations
make seed        # Populate test data
```

### Monitoring
```bash
make logs        # Tail application logs
make health      # Check service health
make metrics     # View metrics dashboard
```

---

## 12. Contact & Resources

### Team
- **Lead Architect:** [Name / Slack]
- **DevOps Lead:** [Name / Slack]
- **Product Manager:** [Name / Slack]

### Documentation
- [API Documentation](./docs/api.md)
- [Architecture Docs](./docs/architecture.md)
- [Deployment Guide](./docs/deployment.md)

### Links
- [GitHub Repository](https://github.com/...)
- [Project Board](https://github.com/.../projects/...)
- [Status Page](https://status.example.com)
- [Metrics Dashboard](https://metrics.example.com)

---

## Appendix: Environment Variables Reference

```
DATABASE_URL=postgresql://user:pass@localhost:5432/db
PORT=3000
NODE_ENV=development
LOG_LEVEL=info
REDIS_URL=redis://localhost:6379
AWS_ACCESS_KEY_ID=...
...
```

---

**Generated:** 2026-02-27  
**Last Updated:** [When was this dump last refreshed?]  
**Next Review:** [When should this be reviewed again?]
```

---

## Checklist перед финализацией Project Dump

- [ ] Все разделы заполнены, нет placeholder'ов
- [ ] Версии всех компонентов указаны
- [ ] Архитектура описана (текст или диаграмма)
- [ ] Структурные путём relative от корня проекта
- [ ] Таблицы статусов актуальны (обновлены на дату создания)
- [ ] Нет конфиденциальной информации (API keys, passwords, etc.)
- [ ] Команды для локального запуска протестированы (или помечены как неверифицированные)
- [ ] Roadmap реалистичен и содержит даты / версии
- [ ] Риски и техдолг честно оценены
- [ ] Документ читаемый и не превышает 20-30 KB (оптимальный размер)
- [ ] Быстрая навигация через заголовки и оглавление

---

## Дополнительные советы

1. **Актуализация:** Project Dump должен обновляться каждый месяц или после major releases
2. **Живой документ:** Используй это как baseline для более детальной документации
3. **Для новых членов команды:** Это главный entry point для onboarding
4. **Для планирования:** Используй этот dump при планировании спринтов и roadmap
5. **Для AI-агентов:** Передавай этот dump как контекст для других промптов (feature-add, bug-fix, security-audit, etc.)

---

## Ресурсы

| Ресурс | Путь | Назначение |
|---|---|---|
| **MVP/Baseline** | `docs/ai-agent-prompts/promt-mvp-baseline-generator-universal.md` | Next workflow |
| **Onboarding** | `docs/ai-agent-prompts/promt-onboarding.md` | Learning path |
| **Планирование реализации** | `docs/ai-agent-prompts/promt-adr-implementation-planner.md` | Architecture roadmap |
| **Правила проекта** | `.github/copilot-instructions.md` | Development standards |
| **Официальная документация** | `docs/official_document/` | **READ-ONLY** эталон |
| **Meta-prompt** | `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md` | Source of truth |

---

## Связи с другими промптами

- `promt-mvp-baseline-generator-universal.md` — построение MVP/Baseline на основе Project Dump
- `promt-onboarding.md` — создание onboarding плана для новых членов команды
- `promt-adr-implementation-planner.md` — планирование реализации архитектурных решений
- `promt-refactoring.md` — рефакторинг на основе выявленного техдолга
- `promt-risk-assessment.md` — детальный анализ рисков из раздела 10

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|----------|
| 1.1 | 2026-03-06 | Добавлены секции Gate I: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`. |
| 1.0 | 2026-02-27 | Первая версия: universal project stack & status dump. |

---

**Версия промпта:** 1.1
**Date:** 2026-03-06  
**Совместимость:** Любой тип проекта (Backend, Frontend, SaaS, Infrastructure, etc.)  
**Последнее обновление:** 2026-02-27
