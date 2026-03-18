# AI Agent Prompt: Исправление дефектов (Bug Fix) в CodeShift

**Version:** 1.2
**Date:** 2026-03-06
**Purpose:** Управление процессом исправления дефектов с учётом ADR-соответствия и архитектурных решений

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Operational |
| **Время выполнения** | 30–90 мин |
| **Домен** | Dev workflow — исправление дефектов |

**Пример запроса:**

> «Используя `promt-bug-fix.md`, диагностируй и исправь баг: `<описание проблемы>`.
> Проверь связь с ADR и обнови релевантные чеклисты.»

**Ожидаемый результат:**
- Root cause определён и задокументирован
- Фикс реализован без нарушения ADR-инвариантов
- Тесты запущены (`make test-unit`)
- Если баг был ADR-расхождением — ADR обновлён

---

## Когда использовать

- При обнаружении дефекта в любом компоненте CodeShift (Bot, K8s, CI/CD)
- Когда баг может быть следствием нарушения архитектурного решения
- При регрессии после изменений в инфраструктуре или конфигурации
- Для постмортема: понять, не является ли баг симптомом системной проблемы

> **Совет:** После исправления запустить `promt-verification.md` —
> убедиться, что фикс не создал новых ADR-расхождений.

---

## Mission Statement

Ты — AI-агент, специализирующийся на **исправлении дефектов** в проекте CodeShift.
Твоя задача — не просто исправить баг, но и проверить, не является ли он следствием
ADR-расхождения, и обеспечить, что фикс не нарушит архитектурные решения.

**Примеры задач, которые решает этот промпт:**
- Исправление ошибок в Telegram Bot (webhook, команды, платежи)
- Фикс багов в Helm templates (deployment, ingress, middlewares)
- Исправление проблем с K8s provisioning (namespaces, PVC, RBAC)
- Фикс ошибок в CI/CD pipeline (scripts, GitHub Actions)
- Исправление багов в интеграциях (YooKassa, Nextcloud, Redis)

**Ожидаемый результат:**
- Баг исправлен без нарушения ADR-решений
- Если баг был следствием ADR-расхождения — чеклист ADR обновлён
- Выполнена верификация `verify-all-adr.sh`
- При необходимости обновлён `docs/explanation/adr/index.md`

---

## Контракт синхронизации системы

Этот промпт управляется из единой точки: `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`.

Обязательные инварианты синхронизации:
- Использовать topic slug как первичный идентификатор ADR
- Сохранять dual-status: `## Статус решения` + `## Прогресс реализации`
- Перед архитектурными решениями выполнять Context7 gate
- Считать `docs/official_document/` строго READ-ONLY
- После изменений запускать `promt-verification.md` при необходимости

---

## Назначение

Этот промпт управляет устранением дефектов с проверкой ADR-соответствия и минимизацией архитектурного регресса.

## Входы

- Описание бага, шаги воспроизведения, логи, окружение
- Затронутые файлы кода/конфигурации/документации
- Результаты профильных проверок и тестов

## Выходы

- Исправление корневой причины дефекта
- Верифицированный diff без нарушения архитектурных ограничений
- Обновления ADR/индекса при выявлении архитектурного разрыва

## Ограничения / инварианты

- Следовать ограничениям I-1..I-9 и Constraints C1–C10 из meta-prompt
- ADR идентифицировать по topic slug, не по номеру
- При ADR-затронутом баге проверять dual-status и чеклист
- Использовать `verify-all-adr.sh` и `verify-adr-checklist.sh` при архитектурных изменениях
- Context7 gate обязателен для неочевидных исправлений и выборов паттернов
- Соблюдать Anti-Legacy и update in-place

## Workflow шаги

1. Discovery: воспроизвести баг и локализовать корневую причину
2. Design: проверить соответствие ADR и выбрать стратегию исправления
3. Fix: внедрить минимальный и безопасный патч
4. Validation: прогнать тесты/скрипты и проверить отсутствие регрессий

## Проверки / acceptance criteria

- Баг стабильно воспроизводился до фикса и устранён после фикса
- Изменения не нарушают критические ADR-инварианты
- Для ADR-затронутых изменений подтверждён прогресс через `verify-adr-checklist.sh`

## Связи с другими промптами

- До: `promt-verification.md` (если нужен системный ADR-аудит)
- После: `promt-index-update.md` (если обновлялись ADR), `promt-refactoring.md` (если нужен структурный рефакторинг)

---

## Project Context

### О проекте

**CodeShift** — multi-tenant SaaS платформа, развёртывающая VS Code (code-server) в браузере через Telegram Bot с интеграцией YooKassa на Kubernetes.

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

---

## Шаг 0: Диагностика бага

### 0.1. Получить описание проблемы

```
Запроси у пользователя:
1. Описание симптома (что происходит неправильно?)
2. Ожидаемое поведение
3. Шаги воспроизведения
4. Логи/стектрейс (если есть)
5. Окружение (prod/dev, K8s provider, версия)
```

### 0.2. Классифицировать баг

| Категория | Признаки | Связанные ADR |
|---|---|---|
| **Bot/API** | Ошибки в Telegram командах, webhook | `telegram-bot-saas-platform` |
| **Payments** | YooKassa webhook, платежи, статусы | `telegram-bot-saas-platform` |
| **Infrastructure** | Pods, PVC, Ingress, SSL | `storage-provider-selection`, `path-based-routing` |
| **Auth** | JWT, Telegram auth, RBAC | `unified-auth-architecture` |
| **Database** | SQL, PostgreSQL, миграции | `telegram-bot-saas-platform` (schema) |
| **K8s Provider** | k3s/microk8s команды | `k8s-provider-abstraction` |

---

## Шаг 1: Исследование с Context7 (ОБЯЗАТЕЛЬНО при неочевидных багах)

### 1.1. Запрос к Context7

```
Запрос к Context7:
- Библиотека/технология: [что сломалось]
- Версия: [актуальная версия из requirements.txt/Chart.yaml]
- Задача: [описание бага или поведения]
- Что получить: official behavior, known issues, workarounds
```

**Примеры запросов Context7 по типу бага:**

| Тип бага | Запрос к Context7 |
|---|---|
| aiogram handler не срабатывает | `aiogram 3.22 router filter order middleware priority registration` |
| YooKassa webhook 403 | `yookassa webhook hmac signature validation ip whitelist` |
| PVC pending | `kubernetes pvc pending storageclass longhorn provisioner events` |
| Ingress 502 | `traefik ingress backend service endpoint health routing` |

### 1.2. Официальная документация (READ-ONLY)

> **⚠️ ПРАВИЛО:** `docs/official_document/` — **ТОЛЬКО ДЛЯ ЧТЕНИЯ**.

```bash
# Поиск по официальной документации
grep -r "[ключевые слова бага]" docs/official_document/ --include="*.md"
```

---

## Шаг 2: Локализация бага

### 2.1. Найти затронутый код

```bash
# Поиск по ключевым словам ошибки
grep -rn "[текст ошибки]" telegram-bot/app/ --include="*.py"
grep -rn "[текст ошибки]" templates/ --include="*.yaml"
grep -rn "[текст ошибки]" scripts/ --include="*.sh"

# Проверить логи (если K8s)
kubectl logs -n $NAMESPACE deployment/telegram-bot --tail=100
kubectl describe pod -n $NAMESPACE -l app=telegram-bot
```

### 2.2. Воспроизвести баг локально (если возможно)

```bash
# Для Python кода
cd telegram-bot && poetry run pytest tests/ -v -k "[test_name]"

# Для Helm templates
helm template . -f config/values-dev.yaml --debug 2>&1 | grep -A5 "[ключевое слово]"

# Для bash scripts
bash -x scripts/[script].sh 2>&1 | tail -50
```

---

## Шаг 3: Проверка ADR-соответствия (КРИТИЧЕСКИЙ ШАГ)

### 3.1. Определить связанные ADR

```bash
# Найти ADR по ключевым словам бага/файлу
grep -l "[затронутый модуль/файл/технология]" docs/explanation/adr/ADR-*.md

# Проверить критические ADR-топики
for topic in path-based-routing k8s-provider-abstraction storage-provider-selection \
             telegram-bot-saas-platform documentation-generation; do
  find docs/explanation/adr -name "ADR-*-${topic}*.md" -exec echo "Found: {}" \;
done
```

### 3.2. Проверить: является ли баг следствием ADR-расхождения?

| Вопрос | Если ДА |
|---|---|
| Баг в коде, который описан в чеклисте ADR? | → Чеклист неполный, нужно обновить `[ ]` → `[x]` после фикса |
| Баг нарушает принцип из ADR (например, hardcode вместо env var)? | → Фикс должен соответствовать ADR |
| Баг в функционале, который отсутствует в чеклисте ADR? | → Добавить пункт в чеклист |
| Баг показывает, что решение ADR неверное? | → Предложить обновление/deprecation ADR |

---

## Шаг 4: Реализация фикса

### 4.1. Написать фикс

**Принципы:**
- Минимальный фикс — только то, что исправляет баг
- Не добавлять новый функционал (это `promt-feature-add.md`)
- Не рефакторить (это `promt-refactoring.md`)
- Соблюдать code style проекта (4 spaces для bash, 2 spaces для YAML)

### 4.2. Написать тест (если возможно)

```bash
# Для Python
# Добавить тест в telegram-bot/tests/ воспроизводящий баг
poetry run pytest tests/test_[module].py -v

# Для E2E
# Добавить проверку в scripts/test.sh
```

### 4.3. Проверить фикс локально

```bash
# Запустить тесты
make test

# Для Helm — проверить template rendering
helm template . -f config/values-dev.yaml | kubectl apply --dry-run=client -f -
```

---

## Шаг 5: Обновление ADR (если баг был связан с ADR)

### 5.1. Обновить чеклист реализации

Если баг был в функционале из чеклиста ADR:

```bash
# Найти ADR с topic slug
ADR_FILE=$(find docs/explanation/adr -name "ADR-*-[topic-slug]*.md" | head -1)

# Обновить чеклист: [ ] → [x] для исправленного пункта
# Пересчитать прогресс
```

### 5.2. Обновить `## Прогресс реализации`

Если процент изменился:
```markdown
## Прогресс реализации
🟡 Частично (~N%) → 🟡 Частично (~M%)  # если добавились [x]
```

---

## Шаг 6: Верификация

### 6.1. Запустить верификацию ADR

```bash
# Структурная верификация
./scripts/verify-all-adr.sh

# Проверка чеклистов
./scripts/verify-adr-checklist.sh
```

### 6.2. Проверить, что фикс не сломал другое

```bash
# Полный прогон тестов
make test

# Проверка lint
make lint
```

---

## Шаг 7: Документирование

### 7.1. Commit message

```
fix([scope]): [краткое описание]

[Подробное описание проблемы и решения]

Fixes: #[issue number]
ADR-related: [topic-slug] (если применимо)
```

### 7.2. Обновить index.md (если изменился прогресс ADR)

Если прогресс ADR изменился — запустить `promt-index-update.md`.

---

## Чеклист Bug Fix

- [ ] Баг диагностирован (симптом, ожидание, воспроизведение)
- [ ] Выполнен Context7 запрос (для неочевидных багов)
- [ ] Код локализован (файл, строка)
- [ ] Проверены связанные ADR
- [ ] Определено: баг — следствие ADR-расхождения или нет
- [ ] Фикс реализован (минимально, без refactoring)
- [ ] Тест добавлен (если применимо)
- [ ] `verify-all-adr.sh` проходит
- [ ] `verify-adr-checklist.sh` проходит
- [ ] Commit message соответствует стандарту
- [ ] При изменении прогресса ADR — запущен `promt-index-update.md`

## Ресурсы

| Ресурс | Путь | Назначение |
|---|---|---|
| **ADR-файлы** | `docs/explanation/adr/ADR-*.md` | Проверка ADR-соответствия |
| **ADR-шаблон v2** | `docs/explanation/adr/ADR-template.md` | Двойной статус, чеклист |
| **Скрипт прогресса** | `scripts/verify-adr-checklist.sh` | Реальный прогресс из чеклистов |
| **Скрипт верификации** | `scripts/verify-all-adr.sh` | Структурная верификация |
| **Правила проекта** | `.github/copilot-instructions.md` | ADR Topic Registry |
| **Официальная документация** | `docs/official_document/` | **READ-ONLY** эталон |
| **Meta-prompt** | `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md` | Source of truth |

---

## Связанные промпты

| Промпт | Когда использовать |
|---|---|
| `promt-feature-add.md` | Если фикс требует добавления нового функционала |
| `promt-refactoring.md` | Если для фикса нужен рефакторинг |
| `promt-verification.md` | Для полной верификации после фикса |
| `promt-index-update.md` | Если изменился прогресс ADR |

---

## Anti-patterns при Bug Fix

| Anti-pattern | Правильный подход |
|---|---|
| Фикс без проверки ADR | Всегда проверять связанные ADR |
| Hardcode вместо env var | Использовать pydantic-settings |
| Добавление функционала в рамках фикса | Фикс — минимально; новое — через `feature-add` |
| Игнорирование тестов | Добавить тест, воспроизводящий баг |
| Фикс без commit message | Использовать стандартный формат |

---

## Метрики успеха Bug Fix

| Метрика | Ожидание |
|---|---|
| `verify-all-adr.sh` | 100% PASS |
| `verify-adr-checklist.sh` | Прогресс не уменьшился |
| `make test` | Все тесты проходят |
| Баг воспроизводится | НЕТ после фикса |
| Регрессия | НЕТ новых багов |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.2 | 2026-03-06 | Добавлены секции Gate I: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`. |
| 1.1 | 2026-02-25 | Добавлены `## Чеклист`, `## Связанные промпты`, `## Метрики успеха`; unified Mission Statement. |
| 1.0 | 2026-02-24 | Первая версия: диагностика и исправление дефектов с ADR-соответствием. |

---

**Prompt Version:** 1.2
**Date:** 2026-03-06
