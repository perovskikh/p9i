---
name: promt-feature-add
version: "1.5"
type: ai-prompt-system
layer: Operations
status: active
tags: [feature, adr, context7]
---

# AI Agent Prompt: Добавление нового функционала в 

**Version:** 1.5
**Date:** 2026-03-06
**Purpose:** Управление полным жизненным циклом добавления нового функционала: исследование, ADR-решения, реализация, верификация

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Operational |
| **Время выполнения** | 60–120 мин |
| **Домен** | Lifecycle — добавление функционала |

**Пример запроса:**

> «Используя `promt-feature-add.md`, исследуй best practices через Context7,
> прими ADR-решение и добавь функционал: `<описание фичи>`
> с верификацией кода после изменений.»

**Ожидаемый результат:**
- ADR-решение создано/обновлено с dual-status и чеклистом
- Код реализован в соответствии с архитектурными инвариантами
- Верификация ADR↔код пройдена (`promt-verification.md`)
- `promt-index-update.md` запущен для обновления `index.md`

---

## Когда использовать

- При добавлении нового функционала в  (Telegram Bot, API, K8s, CI/CD)
- При расширении ADR идеями из внешних документов (how-to, спецификации, design doc)
- Когда требуется новое ADR-решение перед реализацией
- При интеграции новой зависимости или сервиса в стек

> **Context7 gate обязателен:** перед реализацией исследовать best practices
> через Context7 для ключевых библиотек/инструментов.

---

## Mission Statement

Ты — AI-агент, специализирующийся на **добавлении нового функционала** в проект .
Твоя задача — провести полный цикл: от исследования best practices до реализации и верификации соответствия ADR.

**Примеры задач, которые решает этот промпт:**
- Добавление новой команды или функции в Telegram Bot и т.д.
- Интеграция нового способа оплаты (ЮKassa, Stripe, Telegram Payments и т.д.)
- Создание Web UI/UX интерфейса для управления пользователями
- Добавление нового способа аутентификации (GitHub OAuth, Google, Telegram Login Widget и т.д.)
- Интеграция с новым облачным провайдером или сервисом и т.д.
- Добавление нового типа K8s storage, ingress-контроллера или middleware и т.д.
- Любое другое расширение функциональности проекта!

**Ожидаемый результат (обязательный для каждого запуска):**
- После добавления/обновления ADR выполнена проверка на дубликаты и пересечения
- При пересечениях запущен `promt-consolidation.md` (merge/deprecate/renumber/update references)
- Сохранён двойной статус: `## Статус решения` + `## Прогресс реализации` (ход реализации по чеклисту)
- Обновлены `docs/explanation/adr/index.md` и Mermaid-граф зависимостей
- Перестроена очередь внедрения по Critical Path и слоям Layer 0 → Layer 5

---

## Контракт синхронизации системы

Этот промпт управляется из единой точки: `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`.

Обязательные инварианты синхронизации:
- Использовать topic slug как первичный идентификатор ADR
- Сохранять dual-status: `## Статус решения` + `## Прогресс реализации`
- Перед архитектурными решениями выполнять Context7 gate
- Считать `docs/official_document/` строго READ-ONLY
- После изменений запускать связку: `consolidation`/`verification`/`index-update` при необходимости

> **⚠️ ПЕРЕД НАЧАЛОМ:** Получи описание задачи от пользователя. Если задача не указана явно,
> запроси: «Что именно нужно добавить? (Функция / модуль / интеграция / UI?)»

---

## Назначение

Этот промпт управляет добавлением нового функционала с обязательной ADR-оценкой, Context7 gate и post-sync в индекс.

## Входы

- Инициатива/требование на новый функционал
- Текущие ADR, кодовые артефакты и ограничения платформы
- Результаты Discovery и Context7-исследования

## Выходы

- Реализация функционала и связанный ADR-результат (новый/обновлённый/без изменений)
- Проверенный план интеграции без нарушения существующей архитектуры
- Синхронизация индекса/очереди внедрения при необходимости

## Ограничения / инварианты

- Следовать ограничениям I-1..I-9 и Constraints C1–C10 из meta-prompt
- Идентифицировать ADR только по topic slug
- Поддерживать dual-status и корректность чеклистов
- Для архитектурных решений использовать `verify-all-adr.sh` и `verify-adr-checklist.sh`
- Context7 gate обязателен до решения о реализации
- Соблюдать Anti-Legacy и update in-place

## Workflow шаги

1. Discovery: определить scope и архитектурное влияние
2. Context7: собрать релевантные best practices
3. ADR Decision: выбрать стратегию ADR (new/update/no-change)
4. Implementation + Validation: реализовать и проверить результат

## Проверки / acceptance criteria

- Реализация подтверждена тестами/валидациями
- ADR-решение аргументировано и согласовано с topic slug-first
- Индекс и связанные артефакты синхронизированы при изменениях ADR

## Связи с другими промптами

- До: `promt-verification.md` / `promt-consolidation.md` (при необходимости)
- После: `promt-index-update.md`, `promt-adr-implementation-planner.md`

---

## Project Context

### О проекте

**** — multi-tenant SaaS платформа, развёртывающая VS Code (code-server) в браузере через Telegram Bot с интеграцией YooKassa на Kubernetes.

**Стек:**
- **Infrastructure:** Kubernetes (k3s/microk8s), Helm, Traefik, cert-manager
- **Bot:** Python, aiogram 3.x / python-telegram-bot, FastAPI webhooks
- **Payments:** YooKassa API (HMAC webhook validation, idempotency keys)
- **Storage:** Longhorn (prod), local-path (dev)
- **Database:** PostgreSQL (SQL baseline `scripts/utils/init-saas-database.sql`)
- **GitOps:** ArgoCD

### ADR Topic Registry

> **КРИТИЧНО:** ADR идентифицируются по **topic slug** (не по номеру). Номера нестабильны.
> Поиск: `find docs/explanation/adr -name "ADR-*-{slug}*.md" | head -1`

| Topic Slug | Краткое описание | Критический |
|---|---|---|
| `path-based-routing` | Single domain, path-based routing | ⭐ |
| `k8s-provider-abstraction` | `$KUBECTL_CMD`, never hardcode | ⭐ |
| `storage-provider-selection` | Longhorn (prod), local-path (dev) | ⭐ |
| `telegram-bot-saas-platform` | pydantic-settings, env vars, PLAN_SPECS | ⭐ |
| `documentation-generation` | Reference docs AUTO-GENERATED only | ⭐ |
| `unified-auth-architecture` | JWT + Telegram auth |  |
| `e2e-testing-new-features` | E2E тестирование новых функций |  |
| `helm-chart-structure-optimization` | Оптимизация Helm chart |  |
| `gitops-validation` | ArgoCD + GitOps |  |
| `metrics-alerting-strategy` | Prometheus + Grafana alerting |  |

---

## Шаг 0: Исследование с Context7 (ОБЯЗАТЕЛЬНО)

> **ПРАВИЛО:** Перед любой реализацией **ОБЯЗАТЕЛЬНО** используй Context7 MCP для получения
> актуальной документации и best practices по технологиям, которые будут задействованы.

### 0.1. Запрос к Context7

Сформулируй запрос к Context7 на основе задачи:

```
Запрос к Context7:
- Библиотека/технология: [название, версия]
- Задача: [что нужно реализовать]
- Что получить: best practices, примеры кода, официальные паттерны
```

**Примеры запросов Context7 по типу задачи:**

| Тип функционала | Запрос к Context7 |
|---|---|
| Telegram Bot команды | `aiogram 3.22 router middleware flags dependency injection error handling` |
| YooKassa платежи | `yookassa python sdk payment create webhook idempotency` |
| GitHub OAuth | `fastapi oauth2 github authlib httpx social login` |
| Web UI управления | `fastapi jinja2 templates admin dashboard htmx` |
| K8s provisioning | `kubernetes python client namespace pvc deployment create` |
| PostgreSQL async | `sqlalchemy 2.0 asyncio async_session create query` |
| Redis caching | `redis asyncio aioredis python cache patterns` |
| Helm chart dependencies | `helm chart dependencies Chart.yaml helm dependency update subcharts globals` |

**Context7-факты, которые учитывать в реализации:**
- **aiogram 3.x:** middleware-context проходит end-to-end через middlewares/filters/handlers; использовать flags для классификации handler-логики; DI через type hints; ошибки обрабатывать локально (`try/except`) и на уровне router/dispatcher.
- **Helm:** зависимости описывать в `Chart.yaml`, синхронизировать через `helm dependency update`; subcharts stand-alone; общие параметры прокидывать через global values.

### 0.2. Официальная документация (READ-ONLY)

> **⚠️ ПРАВИЛО:** `docs/official_document/` — **ТОЛЬКО ДЛЯ ЧТЕНИЯ**.
> Никогда не изменять, не перемещать, не удалять файлы в этой директории.
> Использовать только как эталон терминов, API-сигнатур и примеров реализации.

Доступные официальные документы:

| Технология | Путь | Использовать для |
|---|---|---|
| **code-server** | `docs/official_document/code-server/` | Параметры запуска, настройка workspace |
| **k3s** | `docs/official_document/k3s/` | K8s API, CNI, storage classes |
| **Longhorn** | `docs/official_document/longhorn/` | StorageClass, PVC, volume lifecycle |
| **local-path-provisioner** | `docs/official_document/local-path-provisioner/` | Dev storage, PVC имена |
| **Nextcloud Helm** | `docs/official_document/nextcloud_helm/` | Chart values, ingress интеграция |
| **OpenEBS** | `docs/official_document/openebs/` | Enterprise storage альтернатива |
| **Sysbox** | `docs/official_document/sysbox/` | Docker-in-K8s паттерны |
| **YooKassa** | `docs/official_document/yookassa/` | ⭐ API endpoints, webhook events, статусы платежей |

**Команды для чтения официальной документации:**
```bash
# Список файлов официальной документации
find docs/official_document -name "*.md" | sort

# Прочитать конкретный документ
cat docs/official_document/yookassa/README.md

# Поиск по официальной документации
grep -r "payment_id\|idempotencyKey" docs/official_document/yookassa/
```

---

## Шаг 1: Анализ существующего состояния

### 1.1. Понять задачу

```bash
# Просмотреть текущую структуру проекта
tree -L 2 telegram-bot/app/ 2>/dev/null || find telegram-bot/app -maxdepth 2 -type f | sort
ls templates/ | head -20
ls makefiles/
```

### 1.2. Найти связанный код

```bash
# Поиск по ключевым словам задачи
grep -r "[ключевые слова задачи]" telegram-bot/app/ --include="*.py" -l
grep -r "[ключевые слова]" templates/ --include="*.yaml" -l

# Просмотр конфигурации
cat telegram-bot/app/config.py
cat telegram-bot/requirements.txt
```

### 1.3. Изучить смежные ADR

```bash
# Найти ADR, релевантные задаче
ls docs/explanation/adr/ADR-*.md
grep -l "[ключевые слова задачи]" docs/explanation/adr/*.md 2>/dev/null
```

---

## Шаг 2: ADR-решение (ОБЯЗАТЕЛЬНЫЙ)

> **ПРАВИЛО:** Любое изменение, затрагивающее архитектуру, ДОЛЖНО сопровождаться
> ADR-решением. Пропуск этого шага недопустим.

### 2.1. Дерево решений: нужен ли новый ADR?

Ответь на каждый вопрос последовательно:

```
1. Изменяется ли архитектурный принцип или технологический выбор?
   → НЕТ: перейди к вопросу 2
   → ДА:  → требуется новый ADR или обновление существующего

2. Затрагивает ли изменение один из 5 критических ADR-топиков?
   (path-based-routing, k8s-provider-abstraction, storage-provider-selection,
    telegram-bot-saas-platform, documentation-generation)
   → НЕТ: перейди к вопросу 3
   → ДА:  → ОБЯЗАТЕЛЬНО обновить соответствующий ADR

3. Добавляется ли новая интеграция (внешний сервис, протокол, API)?
   → НЕТ: перейди к вопросу 4
   → ДА:  → требуется новый ADR (решение об интеграции)

4. Изменяется ли структура базы данных, K8s-ресурсов или Helm chart?
   → НЕТ: перейди к вопросу 5
   → ДА:  → требуется обновление или новый ADR

5. Это небольшое улучшение в рамках уже зафиксированного ADR-решения?
   → ДА:  → ADR не нужен, только комментарий в коде и PR description
   → НЕТ: → создать новый ADR
```

### 2.2. Действия по результатам дерева решений

#### Вариант A: Нужен НОВЫЙ ADR

```bash
# 1. Получить текущий максимальный номер ADR
ls docs/explanation/adr/ADR-[0-9]*.md | sort -V | tail -1

# 2. Создать новый ADR по шаблону
cp docs/explanation/adr/ADR-template.md docs/explanation/adr/ADR-NNN-{slug}.md

# 3. Заполнить секции:
# - Статус: Proposed (до реализации) → Accepted (после)
# - Дата, Контекст, Решение, Последствия, Реализация, Тестирование
# - Добавить ссылку на Context7-исследование в секцию ## Ссылки
# - Добавить ссылки на official_document в секцию ## Ссылки

# 4. Добавить в index.md
cat docs/ai-agent-prompts/promt-index-update.md
```

**Обязательная структура нового ADR:**
```markdown
# ADR-NNN: {Краткое описание новой функции}

## Статус решения
Proposed

## Прогресс реализации
🔴 Не начато

**Дата:** {YYYY-MM-DD}

**Автор:** AI Agent (Context7 research & analysis)

**Теги:** #{технология} #{область}

## Контекст
[Зачем нужна эта функция? Что не хватало?]

## Решение
[Конкретное решение с кодом/командами]

## Последствия
- Положительные: [список]
- Отрицательные: [риски]

## Рассмотренные варианты
[Альтернативы, рассмотренные через Context7 и official_document]

## Реализация
[Ключевые файлы, команды, конфигурации]

## Тестирование
[Как верифицировать через ./scripts/verify-all-adr.sh + ./scripts/verify-adr-checklist.sh]

## Чеклист реализации
[По шаблону из ADR-template.md — 4 категории: Обязательные / Условные / Специфичные / Интеграция]

## Связанные ADR
[Ссылки на связанные topic slugs]

## Ссылки
- Context7: [что исследовалось]
- Official docs: `docs/official_document/{технология}/`
- Issue/PR: [ссылка]
```

#### Вариант B: Нужно ОБНОВИТЬ существующий ADR

```bash
# 1. Найти релевантный ADR по topic slug
find docs/explanation/adr -name "ADR-*-{slug}*.md" | head -1

# 2. Обновить секции:
# - Добавить новое решение/расширение в ## Решение
# - Обновить ## Реализация
# - Отметить дату обновления
# - Добавить примечание о том, что обновлено

# 3. Проверить, не вступает ли обновление в конфликт с другими ADR
grep -l "{slug}" docs/explanation/adr/*.md
```

#### Вариант C: Нужна КОНСОЛИДАЦИЯ ADR

Если новый функционал пересекается с несколькими существующими ADR и создаёт дубликаты:

```bash
# Запустить промпт консолидации
cat docs/ai-agent-prompts/promt-consolidation.md
# Контекст: Вариант C — перед добавлением нового ADR NNN.
# Обнаружены пересечения с: ADR-{X}, ADR-{Y}.
# Действие: Консолидировать перед добавлением нового.
```

#### Вариант D: ADR не нужен

Оставить комментарий в PR description:
```
ADR Decision: Not required.
Reason: This change is a minor improvement within the existing [topic-slug] decision.
Related ADR: docs/explanation/adr/ADR-NNN-{slug}.md
```

---

## Шаг 3: Исследование реализации (Context7 + official_document)

### 3.1. Получить best practices через Context7

```
Конкретный запрос к Context7:
«Покажи best practices для [технология + задача] на примере production-ready кода.
Включи: обработку ошибок, логирование, тестирование, async паттерны»
```

### 3.2. Сверить с official_document

```bash
# Сверить API с официальной документацией (READ-ONLY)
# Пример для YooKassa:
cat docs/official_document/yookassa/README.md | grep -A5 "payment"

# Пример для code-server:
find docs/official_document/code-server -name "*.md" | xargs grep -l "config"

# Пример для K3s:
grep -r "StorageClass\|PersistentVolume" docs/official_document/k3s/
```

### 3.3. Проверить архитектурные принципы

```bash
# 1. Проверить отсутствие hardcoded kubectl
grep -r "k3s kubectl\|microk8s kubectl" scripts/ makefiles/ telegram-bot/
# → Должно быть пусто. Использовать: $KUBECTL_CMD

# 2. Проверить pydantic-settings для Python
grep "pydantic_settings\|BaseSettings" telegram-bot/app/config.py
# → Должно присутствовать

# 3. Проверить path-based routing (no subdomains)
grep -E "host:.*\.(com|ru|io)" templates/ingress.yaml
# → Все новые маршруты должны быть path-based

# 4. Проверить отсутствие hardcoded secrets
grep -rE "(password|secret|token)\s*=\s*['\"][^{]" telegram-bot/app/ --include="*.py"
# → Должно быть пусто
```

---

## Шаг 4: Реализация

### 4.1. Правила реализации

> **ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА:**
>
> 1. **Python:** pydantic-settings для конфигурации, env vars из `.env`
> 2. **Bash:** `set -euo pipefail`, использовать `$KUBECTL_CMD`
> 3. **K8s:** `kubectl apply` (idempotent), никогда `kubectl create`
> 4. **Helm:** `--wait=false` + отдельный `kubectl wait`
> 5. **Secrets:** никогда в коде, только через env vars / K8s secrets
> 6. **Routing:** path-based (no subdomains), через Traefik middleware
> 7. **Make targets:** не создавать alias targets (только dependency + own commands)
> 8. **Docs:** reference docs только AUTO-GENERATED
> 9. **Official docs:** НЕ изменять `docs/official_document/`

### 4.2. Структура изменений

В зависимости от типа функционала:

**Telegram Bot (новая команда/функция):**
```bash
# Файлы для изменения:
# telegram-bot/app/bot/  — handlers
# telegram-bot/app/config.py  — новые env vars через pydantic-settings
# telegram-bot/requirements.txt  — новые зависимости (если нужны)
# scripts/utils/init-saas-database.sql  — если нужны новые таблицы (КАНОНИЧЕСКИЙ)
```

**Новый способ оплаты:**
```bash
# Файлы для изменения:
# telegram-bot/app/payments/  — новый payment provider
# telegram-bot/app/config.py  — credentials через env vars
# docs/explanation/adr/ADR-NNN-{slug}.md  — новый ADR (обязательно)
# docs/official_document/{payment}/  — READ-ONLY, не изменять
```

**Web UI/UX:**
```bash
# Файлы для создания/изменения:
# telegram-bot/app/admin/  — FastAPI admin роуты
# templates/ingress.yaml  — path-based route /admin
# templates/  — новый Helm template если нужен
# docs/explanation/adr/ADR-NNN-{slug}.md  — новый ADR
```

**Новый способ аутентификации:**
```bash
# Файлы для изменения:
# telegram-bot/app/auth/  — новый auth provider
# telegram-bot/app/config.py  — OAuth credentials
# templates/ingress.yaml  — auth middleware
# docs/explanation/adr/ADR-NNN-{slug}.md  — обновить ADR unified-auth
```

**Новый K8s компонент:**
```bash
# Файлы для создания:
# templates/{component}.yaml  — Helm template
# config/variables/components/  — конфигурационные переменные
# (НЕ редактировать config/values*.yaml напрямую — AUTO-GENERATED)
# docs/explanation/adr/ADR-NNN-{slug}.md  — новый ADR
```

### 4.3. Шаблоны кода (Context7 pattern)

**Python — новая конфигурация:**
```python
# Intent: Add new feature config to pydantic-settings
# Input: Env vars NEW_FEATURE_API_KEY, NEW_FEATURE_ENABLED
# Expected: Typed settings with validation and defaults

class Settings(BaseSettings):
    # ... existing fields ...

    # New feature: [название функции]
    new_feature_enabled: bool = Field(default=False, env="NEW_FEATURE_ENABLED")
    new_feature_api_key: str = Field(default="", env="NEW_FEATURE_API_KEY")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
```

**Python — новый payment provider:**
```python
# Intent: Integrate new payment provider following YooKassa pattern
# Input: payment_data dict, idempotency_key str
# Expected: Payment object with status and confirmation_url

from app.config import settings
import hmac, hashlib

class NewPaymentProvider:
    """New payment provider following YooKassa patterns.
    
    Context7 metadata:
    Intent: Implement payment provider abstraction
    Input: PaymentRequest with amount, currency, description
    Expected output: PaymentResponse with payment_id, status, redirect_url
    Preconditions: NEW_PAYMENT_API_KEY set in settings
    """
    def __init__(self):
        self.api_key = settings.new_payment_api_key
    
    async def create_payment(self, amount: float, description: str,
                             idempotency_key: str) -> dict:
        ...
```

**Bash — новый скрипт:**
```bash
#!/bin/bash
# Purpose: [описание скрипта]
# Usage: ./scripts/[name].sh [args]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MY_ROOT_DIR="$SCRIPT_DIR/.."  # CRITICAL: preserve before sourcing helpers

source "$MY_ROOT_DIR/scripts/lib/utils.sh"

# Используем абстракцию K8s провайдера (ОБЯЗАТЕЛЬНО)
source "$MY_ROOT_DIR/scripts/helpers/k8s-exec.sh"
KUBECTL_CMD=$(get_kubectl_cmd)

print_header "New Feature Script"
$KUBECTL_CMD apply -f manifest.yaml  # НЕ kubectl create
```

---

## Шаг 5: Тестирование

### 5.1. Unit тесты (Python)

```bash
# Запустить существующие тесты
cd telegram-bot
python -m pytest tests/ -v

# Тесты для нового функционала должны быть в:
# tests/unit/test_{new_feature}.py
# Использовать: unittest.mock, AsyncMock (по образцу существующих тестов)
```

### 5.2. Lint и проверки

```bash
# Python lint
cd telegram-bot && python -m flake8 app/ tests/

# Bash lint
shellcheck scripts/**/*.sh

# YAML lint
yamllint config/ templates/

# Helm lint
helm lint .

# Makefile: проверка alias targets
make validate-make-no-aliases
```

### 5.3. E2E верификация

```bash
# Если функционал затрагивает K8s/Helm
make test

# Проверка документации
make docs-validate
make validate-docs-structure
```

---

## Шаг 6: Верификация ADR-соответствия

### 6.1. Запустить верификацию

```bash
# Полная верификация
./scripts/verify-all-adr.sh

# Быстрая верификация (критические ADR)
./scripts/verify-all-adr.sh --quick

# Проверка прогресса реализации по чеклистам (ДВОЙНОЙ СТАТУС)
./scripts/verify-adr-checklist.sh --topic {new-feature-slug}

# Сгенерировать отчёт
./scripts/generate-adr-verification-report.sh
```

### 6.2. Целевые показатели

| Метрика | Требование |
|---|---|
| Pass rate | ≥ 95% |
| Hardcoded kubectl | 0 |
| Missing pydantic-settings | 0 |
| Missing AUTO-GENERATED markers | 0 |
| Subdomains в ingress | 0 |

### 6.3. Обновить index.md

После успешной верификации:
```bash
# Запустить index-update-prompt:
cat docs/ai-agent-prompts/promt-index-update.md
# Контекст: Вариант C — После добавления нового ADR NNN-{slug}.
# Действие: Добавить новый ADR в index.md и обновить статистику.
```

### 6.4. ADR Normalization Gate (ОБЯЗАТЕЛЬНО после feature-add)

После добавления/обновления ADR запусти обязательный шлюз нормализации:

```bash
# 1) Поиск дубликатов/пересечений
./scripts/find-duplicate-adr.sh

# 2) Если найдены пересечения с новым ADR — запустить консолидацию
cat docs/ai-agent-prompts/promt-consolidation.md
# Контекст: После feature-add для ADR-NNN-{slug}, обнаружены пересечения с ADR-{X}, ADR-{Y}

# 3) Проверка прогресса реализации (реальный ход реализации)
./scripts/verify-adr-checklist.sh --format short

# 4) Перестроение очереди внедрения по Critical Path + Layer hierarchy
cat docs/ai-agent-prompts/promt-verification.md
# Контекст: После feature-add, пересчитать planned/partial/full и обновить очередь внедрения
```

**Критерий прохождения gate:**
- Нет неразрешённых дублей/пересечений для нового topic slug
- Если было слияние, контент не потерян (`verify-adr-merge.sh`)
- Статусы planned/partial/full отражают реальное состояние чеклистов
- Mermaid-граф и очередь внедрения синхронизированы с текущим состоянием ADR

---

## Шаг 7: Документация

### 7.1. Обязательные обновления

```bash
# Если изменились Make-цели:
make docs-readme  # Регенерация README.md

# Если изменились конфигурационные переменные:
make generate-dev  # ИЛИ make generate-prod

# Rebuild docs:
make docs-build
make docs-validate
```

### 7.2. Правила документирования нового функционала

По Diátaxis:
- **Обучение (как работает):** `docs/tutorials/` — только если новая концепция
- **Задачи (как сделать):** `docs/how-to/` — конкретные шаги
- **Справка:** `docs/reference/` — **только AUTO-GENERATED** (через `make docs-update`)
- **Объяснение (зачем):** `docs/explanation/` — ADR + архитектурные решения

**ЗАПРЕЩЕНО создавать:**
- `PHASE_*.md`, `*_COMPLETE.md`, `*_SUMMARY.md`, `*_REPORT.md`
- Директории: `reports/`, `plans/`, `artifacts/archive/`

---

## Финальный чеклист

По завершении реализации проверить:

```markdown
## Feature Add Checklist: [название функции]

### Исследование
- [ ] Context7 запрошен для best practices по [технология/библиотека]
- [ ] official_document прочитан (READ-ONLY, не изменён)
- [ ] Альтернативные подходы рассмотрены

### ADR
- [ ] ADR-решение принято (новый / обновить / консолидировать / не нужен)
- [ ] ADR файл создан или обновлён: docs/explanation/adr/ADR-NNN-{slug}.md
- [ ] Статус ADR: Proposed (на этапе реализации)
- [ ] Ссылки на Context7-исследование и official_document в ADR ## Ссылки

### Реализация
- [ ] Конфигурация через pydantic-settings (никаких hardcoded values)
- [ ] K8s команды через $KUBECTL_CMD (никаких k3s kubectl / microk8s kubectl)
- [ ] kubectl apply (не kubectl create)
- [ ] Новые маршруты — path-based (no subdomains)
- [ ] Secrets в env vars / K8s secrets (не в коде)
- [ ] Bash скрипты: set -euo pipefail + source helpers

### Тестирование
- [ ] Unit тесты добавлены/обновлены
- [ ] Lint пройден (flake8 / shellcheck / yamllint)
- [ ] make validate-make-no-aliases (если изменены Make-цели)
- [ ] ./scripts/verify-all-adr.sh → pass rate ≥ 95%
- [ ] ./scripts/verify-adr-checklist.sh --topic {slug} → прогресс корректен

### Документация
- [ ] ADR статус решения обновлён на Accepted
- [ ] docs/explanation/adr/index.md обновлён (через index-update-prompt)
- [ ] How-to документ добавлен (если нужен пользовательский guide)
- [ ] make docs-build / make docs-validate — успешно

### Финал
- [ ] PR description содержит: ADR Decision + Context7 research summary
- [ ] ./scripts/verify-all-adr.sh: 100% pass rate (или объяснение отклонений)
- [ ] ADR Normalization Gate выполнен (duplicates/merge/queue/index)
```

---

## Ресурсы

| Ресурс | Путь | Назначение |
|---|---|---|
| **ADR шаблон** | `docs/explanation/adr/ADR-template.md` | Структура нового ADR |
| **ADR индекс** | `docs/explanation/adr/index.md` | Список всех ADR |
| **Правила проекта** | `.github/copilot-instructions.md` | ADR Topic Registry + принципы |
| **Правила проекта и архитектурный контекст** | `docs/rules/project-rules.md` | Полный контекст и правила |
| **Bot конфиг** | `telegram-bot/app/config.py` | Все env vars через pydantic-settings |
| **K8s абстракция** | `scripts/helpers/k8s-exec.sh` | get_kubectl_cmd(), determine_k8s_provider() |
| **DB схема** | `scripts/utils/init-saas-database.sql` | ⭐ Канонический источник схемы |
| **Верификация структуры** | `scripts/verify-all-adr.sh` | Автоматическая проверка ADR |
| **Верификация чеклистов** | `scripts/verify-adr-checklist.sh` | Прогресс реализации из чеклистов |
| **Отчёт** | `scripts/generate-adr-verification-report.sh` | Генерация отчёта |
| **Консолидация** | `docs/ai-agent-prompts/promt-consolidation.md` | При дублировании ADR |
| **Index Update** | `docs/ai-agent-prompts/promt-index-update.md` | После изменений ADR |
| **Верификация ADR** | `docs/ai-agent-prompts/promt-verification.md` | Полная верификация |
| **official_document** | `docs/official_document/` | ⭐ Эталон терминов и API (READ-ONLY) |

---

## Anti-Patterns (ЗАПРЕЩЕНО)

```
❌ k3s kubectl apply            → ✅ $KUBECTL_CMD apply
❌ microk8s kubectl get pods    → ✅ $KUBECTL_CMD get pods
❌ provider: "localpath"        → ✅ provider: "local-path"
❌ TOKEN = "hardcoded_secret"   → ✅ token: str = Field(env="TOKEN")
❌ host: admin.example.com      → ✅ path: /admin на основном домене
❌ kubectl create               → ✅ kubectl apply (idempotent)
❌ Редактировать config/values*.yaml → ✅ Изменять config/variables/, затем make generate-dev
❌ Редактировать docs/reference/ вручную → ✅ make docs-update
❌ Изменять docs/official_document/ → ✅ READ-ONLY, только читать
❌ Создавать PHASE_*.md         → ✅ Обновлять существующий ADR или how-to
❌ Alias Make targets           → ✅ Цели с собственными командами
```

---

## Связанные промпты

| Промпт | Когда использовать |
|--------|-------------------|
| `promt-verification.md` | После добавления — верификация ADR-совместимости |
| `promt-index-update.md` | Если добавлен новый ADR — обновить `index.md` и навигацию |
| `promt-bug-fix.md` | При обнаружении дефектов в новом коде |
| `promt-security-audit.md` | Аудит безопасности новой интеграции |
| `promt-consolidation.md` | Для ADR-нормализации после Feature Add Gate |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.5 | 2026-03-06 | Добавлены секции Gate I: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`. |
| 1.4 | 2026-02-25 | Добавлена секция `## Связанные промпты` по каноническому скелету. |
| 1.3 | 2026-02-24 | Context7 gate, Feature Add Gate (4 критерия), dual-status ADR. |

---

**Prompt Version:** 1.5
**For:** Claude, GPT-4, GitHub Copilot, или любой AI-агент
**Context7:** Использовать обязательно на Шаге 0 для best practices
