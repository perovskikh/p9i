---
name: promt-agent-init
version: "1.0"
type: CodeShift
layer: Discovery
status: active
tags: [initialization, agent, meta]
---

# AI Agent Prompt: Обязательная инициализация AI-агента для CodeShift

**Версия:** 1.0  **Дата:** 2026-03-06  **Тип:** Meta
**Purpose:** Обязательная инициализация AI-агента перед работой с CodeShift — загрузка контекста, диагностика ADR, выбор промпта по decision tree, декларация инвариантов.

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Meta |
| **Время выполнения** | 5–10 мин |
| **Домен** | Инициализация агента |

**Пример запроса:**

> «Используя `promt-agent-init.md`, выполни обязательную инициализацию:
> загрузи контекст проекта, проверь состояние ADR, выбери промпт для задачи
> и задекларируй инварианты.»

**Ожидаемый результат:**
- Агент подтвердил загрузку всех 6 контекстных файлов
- Pass rate ADR зафиксирован (из `verify-all-adr.sh --quick`)
- Промпт для задачи выбран из decision tree
- Инварианты задекларированы явно в ответе агента

---

## Когда использовать

- В начале любой новой сессии работы с CodeShift
- Перед выполнением любого операционного промпта
- При смене задачи в рамках сессии
- После длительного перерыва в работе с проектом
- При первом знакомстве нового AI-агента с проектом

Этот промпт **НЕ выполняет** рабочие задачи — только инициализирует агента и выбирает нужный операционный промпт.

---

## Mission Statement

Ты — AI-агент, выполняющий обязательную инициализацию перед работой с проектом CodeShift.
Твоя задача — загрузить все необходимые контекстные файлы, зафиксировать текущее состояние ADR,
выбрать подходящий операционный промпт из decision tree и явно задекларировать архитектурные инварианты.
Без выполнения этой инициализации работа с проектом не начинается — это гарантирует консистентность
решений с принятыми Architecture Decision Records.

---

## Контракт синхронизации системы

> **Source of truth:** `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`
> Этот промпт подчиняется source of truth. При конфликте — приоритет у meta-prompt.

**Обязательные инварианты:**
- ADR идентификация по **topic slug** (номера нестабильны)
- Dual-status: `## Статус решения` + `## Прогресс реализации`
- `docs/official_document/` — READ-ONLY
- `.roo/` — READ-ONLY
- Anti-legacy: не создавать `PHASE_*.md`, `*_REPORT.md`, `*_SUMMARY.md`
- `$KUBECTL_CMD` из `scripts/helpers/k8s-exec.sh` — никогда не хардкодить
- Canonical DB: `scripts/utils/init-saas-database.sql` (без Alembic)
- Deployment contour: только `Helm + config/manifests`; `k8s/` — legacy
- Legal: 422-ФЗ (НПД) — без CPU/RAM/server в публичных текстах

---


## Назначение

Обязательная инициализация AI-агента перед работой с CodeShift: загрузка контекста, диагностика ADR, выбор промпта по decision tree, декларация инвариантов.

## Входы

- Файлы контекста проекта: `CLAUDE.md`, `.github/copilot-instructions.md`, `docs/rules/project-rules.md`
- Результаты `./scripts/verify-all-adr.sh --quick`
- Описание задачи от пользователя

## Выходы

- Подтверждение загрузки 6 контекстных файлов
- ADR pass rate (из скрипта верификации)
- Выбранный промпт из decision tree
- Задекларированные инварианты в ответе агента

## Ограничения / инварианты

См. `## Контракт синхронизации системы` выше. Ключевые: topic slug-first, dual-status ADR, READ-ONLY `docs/official_document/`, Anti-Legacy, Canonical DB.

## Workflow шаги

См. шаги `## Шаг 0`–`## Шаг 5` ниже: Загрузка контекста → Context7 → Диагностика ADR → Выбор промпта → Декларация инвариантов → Сообщение готовности.

## Проверки / acceptance criteria

См. `## Чеклист инициализации` ниже. Промпт считается завершённым, когда: все 6 файлов загружены, ADR pass rate зафиксирован, промпт выбран, инварианты задекларированы.

## Project Context

### О проекте

**CodeShift** — multi-tenant SaaS платформа, развёртывающая VS Code (code-server)
в браузере через Telegram Bot с YooKassa на Kubernetes.

**Стек:** Kubernetes (k3s/microk8s), Helm, Traefik, cert-manager, Python,
aiogram 3.x, FastAPI, PostgreSQL, Redis, Longhorn/local-path, ArgoCD.

### ADR Topic Registry (релевантные)

> **КРИТИЧНО:** ADR идентифицируются по **topic slug**.
> Поиск: `find docs/explanation/adr -name "ADR-*-{slug}*.md" | head -1`

| Topic Slug | Назначение |
|---|---|
| `prompt-system-improvement-strategy` | Стратегия улучшения prompt-системы |
| `documentation-generation` | Генерация и стандарты документации |
| `bash-formatting-standard` | Стандарты bash-скриптов |
| `k8s-provider-abstraction` | Абстракция K8s-провайдера |
| `telegram-bot-saas-platform` | Telegram Bot SaaS платформа |
| `path-based-routing` | Path-based routing (без subdomains) |

---

## Шаг 0: Загрузка контекста (ОБЯЗАТЕЛЬНЫЙ)

Прочитать полностью следующие файлы:

1. `CLAUDE.md` — инструкции для Claude Code
2. `.github/copilot-instructions.md` — инструкции для GitHub Copilot
3. `docs/ai-agent-prompts/README.md` — навигация по промптам и decision tree
4. `docs/explanation/adr/index.md` — canonical topic slugs и граф зависимостей
5. `docs/rules/project-rules.md` — стандарты разработки и инварианты
6. `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md` — source of truth

Подтвердить загрузку явно: «Контекст загружен: [перечислить 6 файлов с датами последнего изменения]».

---

## Шаг 1: Context7 исследование (ОБЯЗАТЕЛЬНО)

> Используй Context7 MCP: `resolve-library-id` → `get-library-docs`

Запросить best practices для технологий, задействованных в планируемой задаче.
Если задача неизвестна — использовать стек по умолчанию:

| Библиотека | Context7 ID |
|---|---|
| aiogram 3.x | `/websites/aiogram_dev_en_v3_22_0` |
| FastAPI | `/fastapi/fastapi` |
| Kubernetes | `/kubernetes/website` |
| Helm | `/websites/helm_sh` |

Зафиксировать, какие практики релевантны для текущей сессии.

---

## Шаг 2: Диагностика ADR (ОБЯЗАТЕЛЬНЫЙ)

```bash
# Быстрая диагностика состояния ADR
./scripts/verify-all-adr.sh --quick
./scripts/verify-adr-checklist.sh
```

Зафиксировать:
- Pass rate (формат: `X/Y checks passed`)
- Список активных ADR (topic slugs)
- Текущие блокеры и незакрытые GAP'ы (если есть)

---

## Шаг 3: Выбор промпта по decision tree

Использовать decision tree из `docs/ai-agent-prompts/README.md` (раздел 3).
Выбрать **ровно один** промпт для текущей задачи.

Критерии выбора:
- Изменения в правилах prompt-системы → `meta-promt-adr-system-generator.md`
- Новый промпт / обновление → `meta-promt-prompt-generation.md`
- Верификация ADR↔код → `promt-verification.md`
- Новый функционал → `promt-feature-add.md`
- Исправление бага → `promt-bug-fix.md`
- Рефакторинг → `promt-refactoring.md`
- CI/CD → `promt-ci-cd-pipeline.md`
- Security аудит → `promt-security-audit.md`
- База данных → `promt-db-baseline-governance.md`
- Синхронизация AI-инструкций → `promt-copilot-instructions-update.md`

Подтвердить выбор: «Использую `promt-X.md` для задачи: [описание]».

---

## Шаг 4: Декларация инвариантов

Явно перечислить следующие инварианты в ответе:

1. **Topic slug-first** — ADR идентифицируются только по topic slug
2. **READ-ONLY зоны** — `docs/official_document/`, `.roo/` не изменяются
3. **Anti-legacy** — не создавать `PHASE_*.md`, `*_REPORT.md`, `*_SUMMARY.md`
4. **Canonical DB** — только `scripts/utils/init-saas-database.sql`
5. **K8s abstraction** — `$KUBECTL_CMD` из `scripts/helpers/k8s-exec.sh`
6. **Deployment contour** — только Helm; `k8s/` legacy
7. **Dual-status ADR** — `## Статус решения` + `## Прогресс реализации`
8. **Ingress** — Traefik, path-based routing, без subdomains
9. **Legal** — 422-ФЗ (НПД), без CPU/RAM в публичных текстах

---

## Шаг 5: Сообщение готовности

Завершить инициализацию явным сообщением в формате:

```
Инициализация завершена.
Использую: promt-X.md
ADR pass rate: Y/Z
Активных ADR: N (topic slugs: ...)
Инварианты приняты: topic slug, READ-ONLY, Anti-legacy, Canonical DB,
K8s abstraction, Deployment contour, Dual-status, Ingress, Legal.
Готов к работе.
```

---

## Чеклист инициализации

**Pre (до начала работы):**
- [ ] 6 контекстных файлов прочитаны полностью
- [ ] Даты последних изменений ключевых файлов зафиксированы
- [ ] Context7 запрос выполнен (или обоснован пропуск)

**During (в процессе):**
- [ ] ADR диагностика запущена и pass rate зафиксирован
- [ ] Список активных ADR по topic slugs сформирован
- [ ] Промпт для задачи выбран по decision tree
- [ ] Выбор промпта обоснован

**Post (завершение инициализации):**
- [ ] 9 инвариантов задекларированы явно
- [ ] Сообщение готовности отправлено в стандартном формате
- [ ] Агент подтвердил готовность к выполнению задачи

---

## Anti-patterns

1. **Начало работы без инициализации** — нарушает консистентность с ADR и инвариантами
2. **Использование ADR-XXX номеров** вместо topic slug — номера нестабильны
3. **Изменение READ-ONLY зон** (`docs/official_document/`, `.roo/`)
4. **Не создавать legacy-файлы** (`PHASE_*.md`, `*_REPORT.md`, `*_SUMMARY.md`)
5. **Пропуск Context7 шага** без явного обоснования

---

## Связи с другими промптами

| Промпт | Когда использовать |
|--------|-------------------|
| `meta-promt-adr-system-generator.md` | После инициализации — если нужно изменить правила системы |
| `promt-verification.md` | Если задача — верификация ADR↔код |
| `promt-sync-optimization.md` | Аудит синхронизации prompt-системы |
| `promt-onboarding.md` | Онбординг нового разработчика |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.0 | 2026-03-06 | Создан по `meta-promt-sync-init-generator.md` v1.0 — новая самодокументирующаяся структура с gates I и J |

---

**Prompt Version:** 1.0
**Maintainer:** @perovskikh
**Date:** 2026-03-06
