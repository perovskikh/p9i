# AI Agent Prompt: Developer Onboarding (Universal)

> **NOTE:** This is a UNIVERSAL prompt that auto-adapts to any project structure.
> All project-specific references use `${VARIABLE}` placeholders.

**Version:** 1.2
**Date:** 2026-03-06
**Purpose:** Помощь новым разработчикам в понимании архитектуры проекта через систему ADR

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Operational |
| **Время выполнения** | 45–90 мин |
| **Домен** | DevEx — онбординг разработчика |

**Пример запроса:**

> «Используя `promt-onboarding.md`, составь onboarding-план для роли
> `<Bot-разработчик / DevOps / Full-stack>`
> с файлами для изучения, командами для запуска и FAQ.»

**Ожидаемый результат:**
- Персонализированный onboarding-план по роли
- Список ключевых файлов и ADR для изучения (приоритизированный)
- Команды для быстрой проверки среды (`make status`, `make test`)
- FAQ с частыми вопросами новичков по архитектуре

---

## Когда использовать

- При появлении нового разработчика в команде
- При смене роли (Bot → DevOps или наоборот)
- Для AI-агента: перед первым выполнением задач в проекте
- После длительного перерыва — как «обновление контекста»

> **Альтернатива для AI-агента:** `promt-agent-init.md` →
> `promt-project-stack-dump.md` → `promt-project-adaptation.md`.

---

## Mission Statement

Ты — AI-агент, специализирующийся на **онбординге разработчиков** в проект .
Твоя задача — провести «экскурсию» по архитектуре проекта, объяснить ключевые ADR-решения
и помочь новому участнику быстро стать продуктивным.

**Примеры задач, которые решает этот промпт:**
- Объяснение архитектуры проекта новому разработчику
- Показ ключевых ADR и их связей
- Генерация персонализированного плана онбординга
- Ответы на вопросы о «почему так сделано»
- Направление к правильным документам и коду

**Ожидаемый результат:**
- Разработчик понимает структуру проекта
- Знает ключевые ADR по своей области
- Имеет план первых задач
- Знает, где искать информацию

---

## Контракт синхронизации системы

Этот промпт управляется из единой точки: `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`.

Обязательные инварианты:
- ADR идентифицируются по topic slug
- `docs/official_document/` — READ-ONLY эталон
- Документация по Diátaxis структуре

---

## Назначение

Этот промпт формирует управляемый onboarding-разбор  по ролям с привязкой к ADR, процессам и ограничениям проекта.

## Входы

- Роль и уровень участника (Bot/DevOps/Full-stack)
- Текущий контекст проекта и обязательные архитектурные правила
- Приоритетные зоны обучения и рабочие задачи

## Выходы

- Персонализированный onboarding-план с шагами и checkpoints
- Список обязательных файлов/команд/ADR для старта
- Рекомендованный следующий workflow-промпт для практики

## Ограничения / инварианты

- Следовать ограничениям I-1..I-9 и Constraints C1–C10 из meta-prompt
- Использовать topic slug-first при разборе ADR
- Учитывать dual-status и фактический прогресс по `verify-adr-checklist.sh`
- Использовать Context7 для подготовки role-specific best practices, если у новичка нет доменного контекста
- Не нарушать read-only зоны и правила Diátaxis
- Соблюдать Anti-Legacy и update in-place

## Workflow шаги

1. Discovery: определить профиль участника и стартовые пробелы
2. Mapping: связать роль с ключевыми ADR, файлами и командами
3. Plan: сформировать последовательность обучения и практики
4. Validation: зафиксировать критерии успешного завершения онбординга

## Проверки / acceptance criteria

- План включает обязательные архитектурные инварианты проекта
- Для роли определены практические шаги и измеримые checkpoints
- Следующие workflow-подсказки согласованы с текущим прогрессом

## Связи с другими промптами

- До: `promt-verification.md` (быстрая картина состояния ADR)
- После: `promt-bug-fix.md`, `promt-feature-add.md`, `promt-refactoring.md`

---

## Project Context

### О проекте (для новичков)

**${PROJECT_NAME}** — ${PROJECT_TYPE}, которая:
- Развёртывает ${PRIMARY_SERVICE} в браузере
- Управляется через ${PRIMARY_INTERFACE}
- Принимает оплату через ${PAYMENT_PROVIDER}
- Работает на Kubernetes (${K8S_PROVIDER})

**Основной flow:**
```
${PRIMARY_INTERFACE} → План подписки → ${PAYMENT_PROVIDER} оплата → ${K8S_PROVIDER} provisioning → ${PRIMARY_SERVICE} в браузере
```

### Структура проекта (overview)

```
/
├── Chart.yaml           # Helm chart definition
├── values.yaml          # Default Helm values
├── templates/           # Kubernetes manifests (Helm)
├── config/              # Configuration
│   ├── variables/       # Config hierarchy (global → env → domain)
│   └── manifests/       # Additional K8s manifests
├── src/                 # Application code
│   └── app/             # Application code
├── scripts/             # Bash scripts (deploy, test, helpers)
├── makefiles/           # Make modules
├── docs/                # Documentation (Diátaxis)
│   ├── tutorials/       # Step-by-step learning
│   ├── how-to/          # Task-oriented guides
│   ├── reference/       # AUTO-GENERATED reference
│   └── explanation/     # Architecture, ADR
│       └── adr/         # Architecture Decision Records
└── gitops/              # ArgoCD applications
```

---

## Шаг 0: Определение роли разработчика

### 0.1. Спросить о роли

```
Запроси у пользователя:
1. Какая твоя роль? (Backend / Frontend / DevOps / Full-stack)
2. С чем будешь работать? (Bot / Infrastructure / Payments / All)
3. Какой опыт? (Python / K8s / Helm / ${PRIMARY_INTERFACE} API)
```

### 0.2. Матрица ролей и ADR

| Роль | Ключевые директории | Ключевые ADR Topics |
|---|---|---|
| **Bot Developer** | `${PROJECT_ROOT}/src/` | `${PLATFORM_SLUG}`, `unified-auth-architecture` |
| **DevOps/Infra** | `templates/`, `scripts/`, `config/` | `k8s-provider-abstraction`, `storage-provider-selection`, `path-based-routing` |
| **Payment Integration** | `${PROJECT_ROOT}/src/payments/` | `${PLATFORM_SLUG}` (webhooks) |
| **Full-stack** | All | All critical ADRs |

---

## Шаг 1: Экскурсия по слоям ADR

### 1.1. Layer 0: Foundation (начни здесь)

**ADR в этом слое:**
- `sysbox-choice` — почему Sysbox для Docker-in-Docker
- `bash-formatting-standard` — стиль bash скриптов
- `documentation-generation` — reference docs AUTO-GENERATED
- `e2e-testing-new-features` — как тестируем

**Что нужно знать:**
```bash
# Стиль bash: 4 spaces, set -euo pipefail
head -10 scripts/deploy/deploy.sh

# Reference docs авто-генерируются, не редактируй вручную
ls docs/reference/

# Тесты
make test
```

### 1.2. Layer 1: K8s Abstraction

**ADR в этом слое:**
- `k8s-provider-abstraction` — **КРИТИЧНЫЙ**: никогда не hardcode kubectl
- `k8s-provider-unification` — унификация ${K8S_PROVIDER}
- `k3s-vs-microk8s` — почему поддерживаем оба

**Что нужно знать:**
```bash
# НИКОГДА так:
# k3s kubectl get pods   ❌

# ВСЕГДА так:
source scripts/helpers/k8s-exec.sh
KUBECTL_CMD=$(get_kubectl_cmd)
$KUBECTL_CMD get pods    ✅
```

### 1.3. Layer 2: Networking & Storage

**ADR в этом слое:**
- `path-based-routing` — **КРИТИЧНЫЙ**: single domain, path routing
- `storage-provider-selection` — Longhorn (prod), local-path (dev)
- `websocket-fix` — WebSocket через Traefik
- `automatic-lets-encrypt` — SSL сертификаты

**Что нужно знать:**
```yaml
# Один домен, разные paths:
# https://example.com/          → ${CODE_SERVER}
# https://example.com/nextcloud → Nextcloud
# https://example.com/telegram  → Bot webhooks

# НЕ используем субдомены:
# code.example.com      ❌
# nextcloud.example.com ❌
```

### 1.4. Layer 3: Application

**ADR в этом слое:**
- `multi-user-approach` — namespace per user
- `unified-auth-architecture` — JWT + Telegram auth
- `shared-storage-${CODE_SERVER}-nextcloud` — общий PVC

**Что нужно знать:**
```python
# Конфигурация через pydantic-settings
from app.config import settings

# Все env vars типизированы
settings.TELEGRAM_BOT_TOKEN  # str
settings.JWT_EXPIRE_MINUTES  # int
```

### 1.5. Layer 4: Observability & SaaS

**ADR в этом слое:**
- `telegram-bot-saas-platform` — **КРИТИЧНЫЙ**: вся SaaS логика
- `gitops-validation` — ArgoCD deployment
- `metrics-alerting-strategy` — Prometheus + Grafana

**Что нужно знать:**
```bash
# Структура приложения
${PROJECT_ROOT}/src/
├── config.py       # pydantic Settings
├── handlers/       # ${PRIMARY_INTERFACE} handlers
├── payments/       # ${PAYMENT_PROVIDER} integration
├── k8s/            # K8s provisioner
└── models/         # SQLAlchemy models
```

### 1.6. Layer 5: Polish

**ADR в этом слое:**
- `centralized-logging-grafana-loki` — логирование
- `readme-autogeneration-solution` — README.md автогенерация
- `helm-chart-structure-optimization` — (Proposed)

---

## Шаг 2: Ключевые файлы и команды

### 2.1. Файлы, которые нужно знать

| Файл | Для чего | Роли |
|---|---|---|
| `${PROJECT_ROOT}/src/config.py` | Все env vars | Bot, Payment |
| `scripts/helpers/k8s-exec.sh` | K8s abstraction | DevOps |
| `templates/_helpers.tpl` | Helm helpers | DevOps |
| `config/variables/global.yaml` | Базовые настройки | All |
| `scripts/utils/init-saas-database.sql` | DB schema | Bot, Backend |
| `.github/copilot-instructions.md` | AI guidelines | All |

### 2.2. Команды для начала

```bash
# Первичная настройка (один раз)
cp .env.example .env
# Отредактировать .env

# Посмотреть доступные команды
make help

# Быстрый старт (если есть K8s)
make quickstart

# Запустить тесты
make test

# Проверить ADR-соответствие
./scripts/verify-all-adr.sh

# Статус развёртывания
make status
```

### 2.3. Полезные make targets

| Target | Описание | Роль |
|---|---|---|
| `make help` | Все команды | All |
| `make dev` | Dev deployment | DevOps |
| `make test` | Запуск тестов | All |
| `make lint` | Линтеры | All |
| `make bot-logs` | Логи бота | Bot |
| `make status` | Статус K8s | DevOps |
| `make generate-dev` | Генерация configs | DevOps |

---

## Шаг 3: Персонализированный план онбординга

### 3.1. Bot Developer (первая неделя)

```markdown
## Онбординг: Bot Developer

### День 1-2: Понимание контекста
- [ ] Прочитать ADR `${PLATFORM_SLUG}`
- [ ] Изучить `${PROJECT_ROOT}/src/config.py` — все settings
- [ ] Запустить бота локально (если есть тестовый токен)
- [ ] Посмотреть handlers в `${PROJECT_ROOT}/src/handlers/`

### День 3-4: Handlers и модели
- [ ] Изучить `${PROJECT_ROOT}/src/models/` — SQLAlchemy models
- [ ] Понять flow: user → subscription → payment
- [ ] Прочитать ADR `unified-auth-architecture`
- [ ] Написать простой handler (тренировка)

### День 5: Интеграции
- [ ] Изучить `${PROJECT_ROOT}/src/payments/` — ${PAYMENT_PROVIDER}
- [ ] Изучить `${PROJECT_ROOT}/src/k8s/` — provisioner
- [ ] Запустить тесты: `cd ${PROJECT_ROOT} && poetry run pytest`

### Ресурсы:
- [$(FRAMEWORK) 3.x:
- `docs/official_document/${PAYMENT_PROVIDER_lower}/` — ${PAYMENT_PROVIDER} API
```

### 3.2. DevOps/Infrastructure (первая неделя)

```markdown
## Онбординг: DevOps

### День 1-2: K8s и Helm
- [ ] Прочитать ADR `k8s-provider-abstraction` — **КРИТИЧНО**
- [ ] Изучить `scripts/helpers/k8s-exec.sh`
- [ ] Понять структуру `templates/`
- [ ] Запустить `make dev` или `make quickstart`

### День 3-4: Storage и Networking
- [ ] Прочитать ADR `storage-provider-selection`
- [ ] Прочитать ADR `path-based-routing`
- [ ] Изучить `templates/ingress*.yaml`
- [ ] Изучить `config/variables/` — иерархия конфигов

### День 5: GitOps
- [ ] Прочитать ADR `gitops-validation`
- [ ] Изучить `gitops/codeshift-application.yaml`
- [ ] Понять sync waves и ArgoCD flow

### Ресурсы:
- `docs/official_document/k3s/` — k3s docs
- `docs/official_document/longhorn/` — Longhorn docs
```

### 3.3. Full-stack (первые две недели)

```markdown
## Онбординг: Full-stack

### Неделя 1: Foundation
- [ ] День 1-2: Прочитать все критические ADR (5 штук)
- [ ] День 3: Setup локального окружения
- [ ] День 4: Запустить `make quickstart`, понять flow
- [ ] День 5: Изучить структуру ${PROJECT_ROOT}/src/

### Неделя 2: Глубокое погружение
- [ ] День 1: Изучить Helm templates
- [ ] День 2: Изучить payments flow (${PAYMENT_PROVIDER})
- [ ] День 3: Изучить K8s provisioning
- [ ] День 4: Изучить CI/CD (GitHub Actions, ArgoCD)
- [ ] День 5: Первая задача из backlog
```

---

## Шаг 4: FAQ для новичков

### 4.1. Частые вопросы

**Q: Почему нет субдоменов?**
A: Прочитай ADR `path-based-routing`. TL;DR: проще SSL, один wildcard не нужен, меньше DNS записей.

**Q: Почему не Alembic для миграций?**
A: Alembic удалён 2026-02-08. Используем baseline SQL (`scripts/utils/init-saas-database.sql`). Применение: `make init-saas-db`.

**Q: Как добавить новую переменную окружения?**
A:
1. Добавь в `${PROJECT_ROOT}/src/config.py` как поле Settings
2. Добавь в `.env.example`
3. Добавь в Makefile exports (если нужно)
4. Обнови `config/manifests/${PROJECT_NAME_LOWER}.yaml`

**Q: Как добавить новый Helm template?**
A:
1. Создай файл в `templates/`
2. Используй helpers из `_helpers.tpl`
3. Добавь условие `{{- if .Values.feature.enabled }}`
4. Протестируй: `helm template . -f config/values-dev.yaml`

**Q: Куда логировать?**
A: Используй стандартный logging Python. В prod логи собирает Loki (ADR `centralized-logging`).

---

## Шаг 5: Следующие шаги

### 5.1. После онбординга

```markdown
1. Получить доступ к репозиторию
2. Настроить локальное окружение (.env)
3. Пройти план онбординга по своей роли
4. Взять первую задачу из backlog
5. При добавлении функционала использовать `promt-feature-add.md`
6. При багфиксах использовать `promt-bug-fix.md`
```

### 5.2. Ресурсы для дальнейшего изучения

| Ресурс | Где |
|---|---|
| Все ADR | `docs/explanation/adr/` |
| Project rules | `docs/rules/project-rules.md` |
| Contribution guide | `CONTRIBUTING.md` |
| Official docs | `docs/official_document/` (READ-ONLY) |
| AI prompts | `docs/ai-agent-prompts/` |

---

## Чеклист онбординга

- [ ] Роль определена
- [ ] Критические ADR прочитаны (5 штук)
- [ ] Локальное окружение настроено
- [ ] `make help` изучен
- [ ] Персонализированный план получен
- [ ] Первая задача взята

---

## Ресурсы

| Ресурс | Путь | Назначение |
|---|---|---|
| **ADR-файлы** | `docs/explanation/adr/ADR-*.md` | Паттерны для новичков |
| **Шаблон ADR** | `docs/explanation/adr/ADR-template.md` | Структура решения |
| **Скрипт верификации** | `scripts/verify-all-adr.sh` | Валидация |
| **Индекс ADR** | `docs/explanation/adr/index.md` | Каталог всех ADR |
| **Правила проекта** | `.github/copilot-instructions.md` | Conventions overview |
| **Официальная документация** | `docs/official_document/` | **READ-ONLY** эталон |
| **Meta-prompt** | `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md` | Source of truth |

---

## Связанные промпты

| Промпт | Когда использовать |
|---|---|
| `promt-feature-add.md` | При добавлении нового функционала |
| `promt-bug-fix.md` | При исправлении багов |
| `promt-verification.md` | Для понимания текущего состояния ADR |
| `promt-security-audit.md` | Для понимания security требований |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.2 | 2026-03-06 | Добавлены секции Gate I: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`. |
| 1.1 | 2026-02-25 | Добавлены onboarding-план по ролям, FAQ, `## Связанные промпты`. |
| 1.0 | 2026-02-24 | Первая версия: developer onboarding через систему ADR. |

---

**Prompt Version:** 1.2
**Date:** 2026-03-06
