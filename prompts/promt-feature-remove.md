# AI Agent Prompt: Удаление / Депрекация функционала в CodeShift

**Version:** 1.5
**Date:** 2026-02-25
**Purpose:** Управление полным жизненным циклом удаления или устаревания функционала: анализ зависимостей, ADR-решения, безопасное удаление, верификация

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Operational |
| **Время выполнения** | 45–90 мин |
| **Домен** | Lifecycle — удаление/депрекация функционала |

**Пример запроса:**

> «Используя `promt-feature-remove.md`, безопасно удали/задепрекируй
> функционал: `<описание>` с анализом зависимостей, рисков и ADR-обновлениями.»

**Ожидаемый результат:**
- Анализ зависимостей удаляемого функционала (кто использует)
- ADR обновлён (статус → Deprecated / Superseded)
- Код удалён безопасно, тесты обновлены
- `promt-verification.md` пройден после удаления

---

## Когда использовать

- При удалении legacy-кода или устаревшего функционала
- При депрекации ADR, которое больше не актуально
- При замене технологии/библиотеки (старая → deprecated)
- После consolidation ADR (старые ADR нужно задепрекировать)

> **Context7 gate:** проверить upstream зависимости перед удалением.

---

## Mission Statement

Ты — AI-агент, специализирующийся на **безопасном удалении и депрекации функционала** проекта CodeShift.
Твоя задача — провести полный цикл: от анализа зависимостей до верификации отсутствия «мёртвого кода» и обновления ADR.

**Примеры задач, которые решает этот промпт:**
- Удаление устаревшей команды или функции из Telegram Bot и т.д.
- Отключение или замена устаревшего способа оплаты и т.д.
- Удаление старого способа аутентификации (после миграции на новый) и т.д.
- Удаление неиспользуемого K8s компонента, Helm шаблона или storage provider и т.д.
- Депрекация устаревшего API endpoint или webhook и т.д.
- Очистка «мёртвого» Python-кода, устаревших миграций БД, неиспользуемых конфигов и т.д.
- Замена одной технологии другой (migration + cleanup) и т.д.
- Удаление legacy скриптов или Make-целей и т.д.

**Ожидаемый результат (обязательный для каждого запуска):**
- После удаления/депрекации ADR проверены planned/partial/full статусы по чеклистам
- При пересечениях/дубликатах запущен `promt-consolidation.md`
- Обновлены `docs/explanation/adr/index.md` и Mermaid-граф зависимостей
- Перестроена очередь внедрения по Critical Path и Layer 0 → Layer 5
- Сохранён двойной статус: `## Статус решения` + `## Прогресс реализации`

---

## Контракт синхронизации системы

Этот промпт управляется из единой точки: `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`.

Обязательные инварианты синхронизации:
- Использовать topic slug как первичный идентификатор ADR
- Сохранять dual-status: `## Статус решения` + `## Прогресс реализации`
- Перед архитектурными решениями выполнять Context7 gate
- Считать `docs/official_document/` строго READ-ONLY
- После удаления выполнять Removal Normalization Gate и синхронизацию с `verification`/`index-update`

> **⚠️ ПЕРЕД НАЧАЛОМ:** Получи описание задачи от пользователя. Если задача не указана явно,
> запроси: «Что именно нужно удалить/задепрекировать? (Команда / модуль / компонент / интеграция?)»

> **⚠️ ПРИНЦИП БЕЗОПАСНОГО УДАЛЕНИЯ:**
> Удаление необратимо. Всегда создавать backup-стратегию (deprecation period) перед hard delete,
> если функционал используется в production. Только затем выполнять удаление.

---

## Назначение

Этот промпт обеспечивает безопасную деактивацию/удаление функционала с управлением рисками, зависимостями и ADR-нормализацией.

## Входы

- Запрос на удаление/депрекацию функционала
- Карта зависимостей затронутых модулей/сервисов
- Текущие ADR и ограничения rollout/rollback

## Выходы

- Безопасно удалённый или депрекейтнутый функционал
- Обновлённые ADR-артефакты и статусы при необходимости
- Подтверждённый rollback-план и верификация после изменений

## Ограничения / инварианты

- Следовать ограничениям I-1..I-9 и Constraints C1–C10 из meta-prompt
- Использовать topic slug-first для ADR
- Поддерживать dual-status и консистентность чеклистов
- Проверять изменения через `verify-all-adr.sh` и `verify-adr-checklist.sh`
- Context7 gate обязателен для migration/deprecation стратегий
- Соблюдать Anti-Legacy и update in-place

## Workflow шаги

1. Discovery: определить scope удаления и матрицу риска
2. Impact Analysis: проверить зависимости и обратную совместимость
3. Removal: выполнить удаление/депрекацию с контролем рисков
4. Validation: подтвердить отсутствие регрессий и обновить ADR-контекст

## Проверки / acceptance criteria

- Удаление не ломает критические пользовательские/системные сценарии
- ADR-обновления отражают фактическое состояние после удаления
- Верификация и rollback-план задокументированы

## Связи с другими промптами

- До: `promt-verification.md` / `promt-consolidation.md`
- После: `promt-index-update.md`, `promt-adr-implementation-planner.md`

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
| `unified-auth-architecture` | JWT + Telegram auth |  |
| `e2e-testing-new-features` | E2E тестирование |  |
| `helm-chart-structure-optimization` | Оптимизация Helm chart |  |
| `gitops-validation` | ArgoCD + GitOps |  |
| `metrics-alerting-strategy` | Prometheus + Grafana alerting |  |

---

## Шаг 0: Исследование с Context7 (ОБЯЗАТЕЛЬНО)

> **ПРАВИЛО:** Перед удалением функционала **ОБЯЗАТЕЛЬНО** используй Context7 MCP для:
> - Изучения best practices безопасного удаления или migration patterns
> - Проверки, что заменяющий функционал соответствует текущим best practices
> - Исследования migration guides для технологий, которые заменяются

### 0.1. Запрос к Context7

```
Запрос к Context7:
- Тип задачи: удаление / депрекация / миграция
- Технология: [что удаляется → на что заменяется]
- Задача: [best practices безопасного удаления / migration path]
```

**Примеры запросов Context7 по типу задачи:**

| Тип удаления | Запрос к Context7 |
|---|---|
| Устаревший Telegram handler | `aiogram 3.22 deprecation migration handlers middlewares flags` |
| Замена payment provider | `payment provider migration safe deprecation idempotency` |
| K8s resource cleanup | `kubernetes resource deletion pvc finalizers graceful cleanup` |
| PostgreSQL column removal | `postgresql alter table drop column safe migration alembic` |
| Helm template removal | `helm chart backward compatibility template deprecation` |
| Auth provider migration | `oauth migration safe cutover deprecated provider removal` |

**Context7-факты, которые учитывать при удалении:**
- **Kubernetes:** удаление PVC/PV может блокироваться finalizers (`pvc-protection`/`pv-protection`); учитывать graceful deletion (`deletionTimestamp`) и порядок удаления ресурсов, чтобы избежать resource leaks.
- **Helm:** для депрекации чарта использовать `deprecated: true` в `Chart.yaml` с bump версии; перед удалением шаблонов проверить backward compatibility и обязательно прогнать `helm lint`.

### 0.2. Официальная документация (READ-ONLY)

> **⚠️ ПРАВИЛО:** `docs/official_document/` — **ТОЛЬКО ДЛЯ ЧТЕНИЯ**.
> Никогда не изменять, не перемещать, не удалять файлы в этой директории.
> Использовать только как эталон migration guides, API-изменений и deprecation notices.

Доступные официальные документы:

| Технология | Путь | Использовать для |
|---|---|---|
| **code-server** | `docs/official_document/code-server/` | Migration notes, removed options |
| **k3s** | `docs/official_document/k3s/` | K8s API deprecations, resource removal |
| **Longhorn** | `docs/official_document/longhorn/` | Volume cleanup, StorageClass removal |
| **local-path-provisioner** | `docs/official_document/local-path-provisioner/` | PVC cleanup, provisioner removal |
| **Nextcloud Helm** | `docs/official_document/nextcloud_helm/` | Chart upgrade, value removal |
| **OpenEBS** | `docs/official_document/openebs/` | Migration to/from OpenEBS |
| **Sysbox** | `docs/official_document/sysbox/` | Container runtime migration |
| **YooKassa** | `docs/official_document/yookassa/` | ⭐ API версионирование, deprecated endpoints |

**Команды для чтения официальной документации:**
```bash
# Поиск deprecation notices в официальных доках
grep -r "deprecat\|removed\|migration" docs/official_document/ --include="*.md" -l

# Конкретная документация
cat docs/official_document/yookassa/README.md
```

---

## Шаг 1: Анализ зависимостей

> **КРИТИЧНО:** Перед любым удалением необходимо полностью понять:
> 1. Что зависит от удаляемого функционала
> 2. Какие пользователи/процессы его используют
> 3. Каков план миграции (если используется в prod)

### 1.1. Найти все зависимости

```bash
# Поиск всех использований удаляемого функционала
FEATURE="[ключевые слова удаляемого функционала]"

# Python код
grep -r "$FEATURE" telegram-bot/app/ --include="*.py" -l
grep -r "$FEATURE" telegram-bot/ --include="*.py" -n

# Конфигурации
grep -r "$FEATURE" config/ --include="*.yaml" -n
grep -r "$FEATURE" templates/ --include="*.yaml" -n

# Скрипты
grep -r "$FEATURE" scripts/ --include="*.sh" -n
grep -r "$FEATURE" makefiles/ --include="*.mk" -n

# Тесты
grep -r "$FEATURE" telegram-bot/tests/ --include="*.py" -l

# Документация
grep -r "$FEATURE" docs/ --include="*.md" -l
```

### 1.2. Анализ K8s ресурсов (если применимо)

```bash
# Найти используемые K8s ресурсы
source scripts/helpers/k8s-exec.sh
KUBECTL_CMD=$(get_kubectl_cmd)

# Список ресурсов связанных с функционалом
$KUBECTL_CMD get all -n [namespace] -l app=[label]
$KUBECTL_CMD get pvc -n [namespace]
$KUBECTL_CMD get configmap -n [namespace]
$KUBECTL_CMD get secret -n [namespace]

# Проверить finalizers (могут блокировать удаление)
$KUBECTL_CMD get pv -o json | grep finalizer
```

### 1.3. Анализ базы данных (если применимо)

```bash
# Найти связанные таблицы/колонки в canonical schema
grep -A20 "[table_name]" scripts/utils/init-saas-database.sql

# Проверить Foreign Key зависимости
grep -i "REFERENCES\|foreign key" scripts/utils/init-saas-database.sql
```

### 1.4. Анализ ADR зависимостей

```bash
# Найти ADR, связанные с удаляемым функционалом
grep -rl "[ключевые слова]" docs/explanation/adr/ --include="*.md"

# Проверить связанные ADR
grep -r "Связанные ADR\|Related ADR" docs/explanation/adr/*.md
```

---

## Шаг 2: Оценка риска

### 2.1. Матрица риска

Для каждого удаляемого элемента определи:

| Элемент | Используется в prod? | Зависимостей | Риск | Стратегия |
|---|---|---|---|---|
| [код/конфиг] | Да/Нет | Кол-во | Высокий/Средний/Низкий | Hard delete / Deprecation period |

### 2.2. Стратегии удаления

**Стратегия A: Немедленное удаление (Hard Delete)**
- Применять когда: функционал не используется в prod, нет активных зависимостей
- Действия: удалить файлы, убрать конфиг, удалить K8s ресурсы, обновить ADR

**Стратегия B: Мягкая депрекация (Soft Deprecation)**
- Применять когда: функционал используется, нужен migration period
- Действия:
  1. Добавить deprecation warning в код
  2. Зафиксировать deprecation в ADR
  3. Установить дату hard delete
  4. Уведомить пользователей

**Стратегия C: Замена функционала (Replace & Remove)**
- Применять когда: старый функционал заменяется новым
- Действия:
  1. Реализовать замену (через promt-feature-add.md)
  2. Период параллельной работы (A/B)
  3. Миграция пользователей
  4. Hard delete старого

---

## Шаг 3: ADR-решение (ОБЯЗАТЕЛЬНЫЙ)

> **ПРАВИЛО:** Любое удаление, затрагивающее архитектурный принцип, ДОЛЖНО сопровождаться ADR-решением.

### 3.1. Дерево решений: как обновить ADR?

```
1. Удаляется целый архитектурный принцип (не просто реализация)?
   → ДА:  → ОБЯЗАТЕЛЬНО создать новый ADR о депрекации/замене
   → НЕТ: → перейти к вопросу 2

2. Удаляемый функционал описан в одном из 5 критических ADR?
   (path-based-routing, k8s-provider-abstraction, storage-provider-selection,
    telegram-bot-saas-platform, documentation-generation)
   → ДА:  → ОБЯЗАТЕЛЬНО обновить соответствующий ADR (добавить секцию о депрекации)
   → НЕТ: → перейти к вопросу 3

3. Для удаляемого функционала существует отдельный ADR?
   → ДА:  → обновить статус на Deprecated + добавить секцию ## Причина депрекации
   → НЕТ: → перейти к вопросу 4

4. Удаляемый функционал упоминается в существующих ADR?
   → ДА:  → обновить соответствующие ADR (убрать ссылки, добавить примечание)
   → НЕТ: → ADR действия не нужны, только обновление index.md
```

### 3.2. Действия по результатам дерева решений

#### Вариант A: Создать ADR о депрекации/замене

```bash
# 1. Получить текущий максимальный номер ADR
ls docs/explanation/adr/ADR-[0-9]*.md | sort -V | tail -1

# 2. Создать новый ADR по шаблону
cp docs/explanation/adr/ADR-template.md docs/explanation/adr/ADR-NNN-deprecate-{slug}.md
```

**Обязательная структура ADR о депрекации:**
```markdown
# ADR-NNN: Депрекация {удаляемый функционал}

## Статус решения
Accepted

## Прогресс реализации
🔴 Не начато

**Дата:** {YYYY-MM-DD}

**Автор:** AI Agent (Context7 research & analysis)

**Supersedes:** ADR-XXX-{old-feature-slug} (если применимо)

**Теги:** #deprecation #{технология} #{область}

## Контекст
[Почему функционал устарел? Что его заменяет?]

## Решение
[Депрекировать {X} по следующим причинам: ...]

## Причина депрекации
- Технические причины: [...]
- Замена: [что используется вместо]
- Дата hard delete: {YYYY-MM-DD}

## Последствия
- Положительные: уменьшение технического долга, упрощение архитектуры
- Отрицательные: breaking change для [кого?], требуется миграция

## Migration Guide
[Шаги миграции с Context7 best practices]

## Реализация
[Что конкретно удаляется / изменяется]

## Тестирование
[Как убедиться, что удаление безопасно]

## Чеклист реализации
[По шаблону из ADR-template.md — 4 категории: Обязательные / Условные / Специфичные / Интеграция]

## Связанные ADR
[Ссылки на заменяемые и связанные ADR]

## Ссылки
- Context7: [migration best practices]
- Official docs: `docs/official_document/{технология}/` (migration notes)
- Issue/PR: [ссылка]
```

#### Вариант B: Обновить статус существующего ADR

```bash
# Найти ADR
find docs/explanation/adr -name "ADR-*-{slug}*.md" | head -1

# Обновить секции ADR:
# 1. Статус: Deprecated
# 2. Добавить поле: **Deprecated:** {YYYY-MM-DD}
# 3. Добавить поле: **Superseded by:** ADR-NNN-{new-slug} (если есть замена)
# 4. Добавить секцию: ## Причина депрекации

# Переместить в deprecated/ ТОЛЬКО после hard delete
mv docs/explanation/adr/ADR-NNN-{slug}.md docs/explanation/adr/deprecated/
```

#### Вариант C: Нужна КОНСОЛИДАЦИЯ ADR перед депрекацией

Если ADR дублирует другой и при депрекации появляется возможность слияния:

```bash
# Запустить промпт консолидации
cat docs/ai-agent-prompts/promt-consolidation.md
# Контекст: Вариант C — После депрекации ADR-XXX освобождается возможность слияния
# с ADR-YYY и ADR-ZZZ. Действие: Консолидировать после выполнения депрекации.
```

#### Вариант D: ADR действия не нужны

Оставить комментарий в PR description:
```
ADR Decision: No ADR action required.
Reason: Removing implementation detail not covered by any ADR.
Checked: No references to this feature in docs/explanation/adr/*.md
```

---

## Шаг 4: Удаление кода

### 4.1. Порядок удаления

> **ПРАВИЛО:** Всегда удалять в порядке от зависимых к независимым, чтобы не сломать сборку.

```
Порядок удаления:
1. Тесты (сначала убрать тесты удаляемого функционала)
2. Точки входа (handlers, endpoints, routes)
3. Бизнес-логика (services, providers, managers)
4. Вспомогательный код (utils, helpers)
5. Конфигурация (config.py, env vars)
6. K8s ресурсы (Helm templates, manifests)
7. Database схема (если применимо — с миграцией)
8. Make-цели и скрипты
9. Документация
10. ADR (финально — обновить статус или переместить в deprecated/)
```

### 4.2. Python: удаление кода

```bash
# 1. Убрать импорты (после удаления всех мест использования)
grep -r "from.*{module}.*import\|import.*{module}" telegram-bot/app/ --include="*.py" -n

# 2. Убрать из requirements.txt (если библиотека больше не используется)
grep "[library]" telegram-bot/requirements.txt
# → Удалить строку только если ни один другой модуль не использует эту библиотеку

# 3. Убрать из config.py (pydantic-settings поля)
# → Удалить только те поля, которые больше нигде не используются
grep "[config_field]" telegram-bot/app/ -r --include="*.py"

# 4. Убрать env vars из .env.example (если есть)
# → Оставить комментарий # DEPRECATED: [field] removed in vX.Y
```

### 4.3. K8s и Helm: удаление ресурсов

```bash
# ВАЖНО: Сначала удалить K8s ресурсы, затем Helm template

# 1. Удалить живые K8s ресурсы
source scripts/helpers/k8s-exec.sh
KUBECTL_CMD=$(get_kubectl_cmd)

# Удалить deployment
$KUBECTL_CMD delete deployment {name} -n {namespace}

# Удалить service
$KUBECTL_CMD delete service {name} -n {namespace}

# Удалить PVC (ОСТОРОЖНО: необратимо, данные будут потеряны)
# $KUBECTL_CMD delete pvc {name} -n {namespace}

# Удалить configmap / secret
$KUBECTL_CMD delete configmap {name} -n {namespace}
$KUBECTL_CMD delete secret {name} -n {namespace}

# 2. Удалить Helm template файл
rm templates/{component}.yaml

# 3. Обновить values.yaml и config/variables/ (не config/values*.yaml напрямую!)
# Удалить соответствующие секции из config/variables/
# Затем регенерировать:
make generate-dev  # или make generate-prod
```

### 4.4. Database: удаление схемы

```bash
# ⚠️ КРИТИЧНО: Изменение БД в production требует migration

# 1. Только canonical source of truth:
# scripts/utils/init-saas-database.sql — для новых инстанций

# 2. Для production migration:
# Создать SQL migration script:
# scripts/utils/migrate-YYYYMMDD-remove-{feature}.sql
# Содержимое: ALTER TABLE ... DROP COLUMN ... (если применимо)

# 3. Обновить init-saas-database.sql (убрать устаревшее)

# 4. Выполнить migration:
make init-saas-db  # для новых инстанций (использует init-saas-database.sql)
# Для prod: применить migration вручную с backup
```

### 4.5. Bash скрипты и Make-цели: удаление

```bash
# 1. Найти все Make-цели связанные с удаляемым функционалом
grep -n "{feature}" makefiles/*.mk

# 2. Удалить цели вместе с их командами (не оставлять пустые targets)
# 3. Проверить: не являются ли другие цели зависимыми от удаляемой
grep -n "| {target}\|$(call.*{target}" makefiles/*.mk

# 4. Валидировать: нет alias targets
make validate-make-no-aliases

# 5. Удалить bash скрипты (только если полностью не используются)
grep -r "scripts/{script_name}.sh" makefiles/ Makefile scripts/
```

### 4.6. Документация: удаление / архивация

```bash
# НЕ удалять docs/official_document/ — READ-ONLY

# Для устаревшей документации:
# 1. how-to: удалить файл если функционал полностью удалён
# 2. tutorials: обновить или удалить
# 3. reference: regenerate through make docs-update
# 4. explanation/adr: обновить статус на Deprecated

# Запрещено:
# ❌ Оставлять docs без обновления после удаления функционала
# ❌ Создавать PHASE_*.md или *_REMOVAL.md вместо обновления ADR
```

---

## Шаг 5: Верификация безопасного удаления

### 5.1. Проверка отсутствия мёртвых ссылок

```bash
# Python импорты (должны отсутствовать ссылки на удалённый модуль)
grep -r "from.*{removed_module}\|import.*{removed_module}" telegram-bot/ --include="*.py"
# → Должно быть пусто

# K8s ресурсы
source scripts/helpers/k8s-exec.sh
KUBECTL_CMD=$(get_kubectl_cmd)
$KUBECTL_CMD get all -n {namespace} -l app={removed_label}
# → Должно быть пусто (NotFound)

# Helm templates
helm template . | grep "{removed_resource}"
# → Должно быть пусто

# Make-цели
make {removed_target} 2>&1
# → Должно быть: make: *** No rule to make target '{removed_target}'

# Документация (мёртвые ссылки)
make docs-validate
```

### 5.2. Запустить тесты

```bash
# Unit тесты (должны проходить без удалённого кода)
cd telegram-bot && python -m pytest tests/ -v

# Lint
cd telegram-bot && python -m flake8 app/ tests/

# Bash lint
shellcheck scripts/**/*.sh

# YAML lint
yamllint config/ templates/

# Helm lint
helm lint .

# Validate Make targets
make validate-make-no-aliases
```

### 5.3. Запустить ADR верификацию

```bash
# Полная верификация
./scripts/verify-all-adr.sh

# Быстрая верификация (критические ADR)
./scripts/verify-all-adr.sh --quick

# Проверка прогресса реализации по чеклистам (ДВОЙНОЙ СТАТУС)
./scripts/verify-adr-checklist.sh

# Сгенерировать отчёт
./scripts/generate-adr-verification-report.sh
```

### 5.4. Целевые показатели

| Метрика | Требование |
|---|---|
| Pass rate | ≥ 95% |
| Hardcoded kubectl | 0 |
| Мёртвые импорты | 0 |
| Мёртвые Make-цели | 0 |
| Broken docs links | 0 |
| Не обновлённые ADR | 0 |

---

## Шаг 6: Обновление ADR index

После успешного удаления:

```bash
# Запустить index-update-prompt
cat docs/ai-agent-prompts/promt-index-update.md
# Контекст: Вариант A — После депрекации ADR NNN-{slug} / удаления функционала {X}.
# Действие: Обновить index.md — статус → Deprecated, переместить в deprecated/ раздел.
```

### 6.1. ADR Removal Normalization Gate (ОБЯЗАТЕЛЬНО после feature-remove)

После удаления/депрекации запусти обязательный шлюз нормализации:

```bash
# 1) Проверка дублей/пересечений после депрекации
./scripts/find-duplicate-adr.sh

# 2) Если после депрекации появились кандидаты на merge — запустить консолидацию
cat docs/ai-agent-prompts/promt-consolidation.md
# Контекст: После feature-remove для {slug}, появились пересечения ADR-{X}, ADR-{Y}

# 3) Пересчитать реальный прогресс реализации
./scripts/verify-adr-checklist.sh --format short

# 4) Перестроить очередь внедрения по Critical Path + Layer hierarchy
cat docs/ai-agent-prompts/promt-verification.md
# Контекст: После feature-remove, пересчитать planned/partial/full и обновить очередь
```

**Критерий прохождения gate:**
- Нет неразрешённых дублей/пересечений по затронутым topic slug
- Статусы planned/partial/full соответствуют фактическим чеклистам
- Mermaid-граф и очередь внедрения синхронизированы с новым состоянием ADR

---

## Шаг 7: Документация

### 7.1. Обязательные обновления

```bash
# Регенерация README.md (если изменились Make-цели)
make docs-readme

# Регенерация конфигурации (если изменились config/variables/)
make generate-dev  # или make generate-prod

# Rebuild docs
make docs-build
make docs-validate
```

### 7.2. Правила документирования удаления

- **ADR:** обновить статус на `Deprecated`, переместить файл в `deprecated/`
- **How-to:** удалить или обновить (убрать упоминания удалённого функционала)
- **Reference:** автоматически обновится через `make docs-update`
- **index.md:** обновить через `promt-index-update.md`

**ЗАПРЕЩЕНО создавать:**
- `PHASE_*.md`, `*_REMOVAL.md`, `*_CLEANUP.md`
- Директории: `deprecated-code/`, `archive/`

---

## Финальный чеклист

По завершении удаления проверить:

```markdown
## Feature Remove Checklist: [название удалённого функционала]

### Исследование и анализ
- [ ] Context7 запрошен для migration best practices по [технология]
- [ ] official_document прочитан (READ-ONLY, не изменён)
- [ ] Все зависимости найдены и проанализированы
- [ ] Матрица риска заполнена
- [ ] Стратегия удаления выбрана: Hard delete / Soft deprecation / Replace & Remove

### ADR
- [ ] ADR-решение принято (новый deprecation ADR / обновить статус / не нужен)
- [ ] ADR файл обновлён: статус → Deprecated
- [ ] Если создан новый ADR: docs/explanation/adr/ADR-NNN-deprecate-{slug}.md
- [ ] Ссылки на Context7-исследование и official_document в ADR ## Ссылки

### Удаление кода
- [ ] Тесты удалённого функционала убраны
- [ ] Python код удалён (handlers, services, utils)
- [ ] Конфигурация (pydantic-settings поля, env vars) очищена
- [ ] K8s ресурсы удалены ($KUBECTL_CMD delete, не kubectl)
- [ ] Helm templates удалены
- [ ] Database схема обновлена (init-saas-database.sql — канонический)
- [ ] Make-цели и bash скрипты удалены
- [ ] Нет alias targets (make validate-make-no-aliases)

### Верификация
- [ ] Нет мёртвых Python импортов
- [ ] Нет мёртвых Make-целей
- [ ] Unit тесты проходят
- [ ] Lint пройден (flake8 / shellcheck / yamllint)
- [ ] helm lint успешен
- [ ] ./scripts/verify-all-adr.sh → pass rate ≥ 95%
- [ ] ./scripts/verify-adr-checklist.sh → прогресс корректен

### Документация
- [ ] ADR статус решения обновлён на Deprecated
- [ ] ADR файл перемещён в deprecated/ (если hard deleted)
- [ ] docs/explanation/adr/index.md обновлён (через index-update-prompt)
- [ ] How-to документы обновлены (убраны ссылки на удалённый функционал)
- [ ] make docs-build / make docs-validate — успешно

### Финал
- [ ] PR description содержит: ADR Decision + список удалённых файлов/ресурсов
- [ ] ./scripts/verify-all-adr.sh: 100% pass rate (или объяснение отклонений)
- [ ] Breaking changes задокументированы (если есть)
- [ ] ADR Removal Normalization Gate выполнен (duplicates/merge/queue/index)
```

---

## Ресурсы

| Ресурс | Путь | Назначение |
|---|---|---|
| **ADR шаблон** | `docs/explanation/adr/ADR-template.md` | Структура нового deprecation ADR |
| **ADR индекс** | `docs/explanation/adr/index.md` | Список всех ADR |
| **Deprecated ADR** | `docs/explanation/adr/deprecated/` | Архив устаревших ADR |
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
| **Feature Add** | `docs/ai-agent-prompts/promt-feature-add.md` | Если удаление + замена |
| **official_document** | `docs/official_document/` | ⭐ Эталон терминов и migration guides (READ-ONLY) |

---

## Anti-Patterns (ЗАПРЕЩЕНО)

```
❌ kubectl delete без $KUBECTL_CMD  → ✅ $KUBECTL_CMD delete
❌ Удалять docs/official_document/ → ✅ READ-ONLY, только читать
❌ Удалять ADR файл без перемещения → ✅ mv в deprecated/ + обновить index.md
❌ Создавать PHASE_*.md или *_CLEANUP.md → ✅ Обновлять существующий ADR
❌ Удалять config/values*.yaml строки напрямую → ✅ Изменять config/variables/, затем make generate-dev
❌ Оставлять мёртвые импорты в Python → ✅ Убирать вместе с удалением кода
❌ Удалять Make-цель без проверки зависимостей → ✅ grep {target} makefiles/*.mk сначала
❌ Удалять PVC без backup → ✅ Всегда создавать backup перед удалением данных
❌ Hard delete без migration period (если prod) → ✅ Soft deprecation → migration → hard delete
❌ Alias Make targets после удаления → ✅ Полностью удалять цель с командами
```

---

## Связанные промпты

| Промпт | Когда использовать |
|--------|-------------------|
| `promt-verification.md` | После удаления — верификация ADR-совместимости |
| `promt-consolidation.md` | Для нормализации ADR после удаления и ADR Removal Gate |
| `promt-index-update.md` | После изменения статусов ADR — обновить индекс |
| `promt-feature-add.md` | При замене удалённого функционала новым |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|----------|
| 1.5 | 2026-03-06 | Добавлены секции Gate I: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`. |
| 1.4 | 2026-02-25 | Добавлена секция `## Связанные промпты` по каноническому скелету. |
| 1.3 | 2026-02-24 | Context7 gate, dependency analysis, ADR Deprecated status. |

---

**Prompt Version:** 1.5
**Date:** 2026-03-06
**For:** Claude, GPT-4, GitHub Copilot, или любой AI-агент
**Context7:** Использовать обязательно на Шаге 0 для migration best practices
**Change:** v1.4 добавлена секция `## Связанные промпты` по каноническому скелету
