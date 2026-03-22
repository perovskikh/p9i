# AI Prompt System — MVP 2026

> Универсальный MCP-сервис управления AI-промтами.
> Полный конвейер любого проекта: от идеи до production.
> Доступ через HTTPS.

---

## Содержание

1. [Что мы строим](#что-мы-строим)
2. [Проблема которую решаем](#проблема-которую-решаем)
3. [Архитектура промтов](#архитектура-промтов)
4. [Полный конвейер проекта](#полный-конвейер-проекта)
5. [Наша уникальность](#наша-уникальность)
6. [MCP доступ через HTTPS](#mcp-доступ-через-https)
7. [Тренды 2026](#тренды-2026)
8. [Роадмап](#роадмап)
9. [Как не потерять уникальность](#как-не-потерять-уникальность)
10. [Конкуренты](#конкуренты)
11. [Технический стек](#технический-стек)
12. [Метрики успеха](#метрики-успеха)

---

## Что мы строим

**AI Prompt System** — это не просто набор промтов.
Это **управляемая MCP-архитектура** с полным конвейером жизненного цикла любого проекта:
от первой идеи до production-реализации.

Система работает как **умный конвейер**:
пишешь на естественном языке что нужно сделать — система определяет
на каком этапе находится задача, выбирает нужный промт,
подключает актуальную документацию через внешние MCP и выполняет.

Подключение через HTTPS:

```
https://mcp.p9i.dev/mcp
```

```
"нужна новая фича авторизации"  →  Pipeline  →  IDEATION → ... → FINISH
"упал деплой в k8s"             →  Router    →  k8s-pack  →  promt-k8s-pod-debug
"обнови README"                 →  Router    →  core      →  promt-readme-sync
```

---

## Проблема которую решаем

### Проблема 1 — Нет стандартного конвейера для AI-задач

Сейчас AI помогает с отдельными задачами — написать функцию, исправить баг.
Но нет системы которая ведёт задачу **через все этапы**: от идеи до кода,
от кода до документации, от документации до CI/CD.

Каждый раз разработчик сам собирает цепочку из разных промтов вручную.

### Проблема 2 — Токены стоят денег

Полный MCP-стек потребляет до 72% контекстного окна
только на описания инструментов.

```
❌ Обычный MCP — грузит всё сразу:
████████████████████████  72% — метаданные всех инструментов
█████                     18% — твой запрос
████                      10% — место для ответа

✅ Наш Lazy Loading — грузит только нужное:
██                         8% — один нужный пак
████████████████████      60% — твой запрос
████████████████          32% — место для ответа
```

Экономия: **−64% токенов** за счёт загрузки только нужного пака.

### Проблема 3 — Нет стандарта для промт-паков

Нет формата, нет зависимостей, нет реестра, нет версионирования.
Промты везде — просто папки с файлами. Как JS до npm.

### Проблема 4 — Сложный UX

```
❌ Было:
run_prompt("promt-k8s-deploy-rollout", {
    "cluster": "prod", "namespace": "default"
})

✅ Стало:
"задеплой в k8s"   use p9i
```

---

## Архитектура промтов

Все промты разделены на три уровня. Каждый уровень отвечает за свою зону ответственности.

---

### TIER 0 — CORE BASELINE
> `readonly` · `immutable` · работают в любом проекте без установки

Базовые операции с кодом. Нельзя удалить, нельзя изменить.
Как UNIX-утилиты: маленький набор, стабильный, вечный.

| Промт | Назначение | Этап конвейера |
|-------|-----------|----------------|
| `promt-feature-add` | Добавление новой фичи | IMPLEMENTATION |
| `promt-bug-fix` | Исправление бага | DEBUGGING |
| `promt-refactoring` | Рефакторинг кода | IMPLEMENTATION |
| `promt-security-audit` | Аудит безопасности | VERIFICATION |
| `promt-quality-test` | Проверка качества | TESTING |

**Правило:** core остаётся замороженным. Новые промты — только в паки или universal.

---

### TIER 1 — UNIVERSAL META
> Мета-промты управления системой и полным конвейером проекта

Разделены на три группы:

#### 1.1 Source of Truth (Конституция системы)

| Промт | Назначение |
|-------|-----------|
| `promt-adr-system-generator` | **Source of Truth** — конституция всей системы, ADR-архитектура |
| `promt-project-rules-sync` | Синхронизация правил проекта с ADR |
| `promt-versioning-policy` | Политика версионирования |

#### 1.2 Фабрика промтов (Meta-generation)

| Промт | Назначение |
|-------|-----------|
| `promt-prompt-creator` | Создание новых промтов под любую задачу |
| `promt-codeshift-refactor` | Рефакторинг кода с автодетектом стека |
| `promt-context7-generation` | Генерация кода с актуальной документацией |

#### 1.3 Адаптация и память проекта

| Промт | Назначение |
|-------|-----------|
| `promt-project-adaptation` | Адаптация системы под конкретный проект |
| `promt-project-stack-dump` | Полный дамп стека технологий проекта |
| `promt-system-adapt` | Автоопределение стека и подстройка промтов |
| `promt-mvp-baseline-generator-universal` | Генерация MVP для любого стека |

#### 1.4 Документация и синхронизация

| Промт | Назначение |
|-------|-----------|
| `promt-readme-sync` | Обновление README |
| `promt-documentation-refactoring-standards-2026` | Рефакторинг документации по стандартам 2026 |
| `promt-consolidation` | Консолидация изменений в единый документ |
| `promt-index-update` | Обновление индексов и реестров |

#### 1.5 Верификация и контроль качества

| Промт | Назначение |
|-------|-----------|
| `promt-verification` | Финальная верификация соответствия ADR и кода |
| `promt-adr-implementation-planner` | Планирование реализации из ADR |
| `promt-baseline-lock` | Заморозка baseline и защита core |

---

### TIER 2 — PLUGIN PACKS
> Подключаемые независимые домены. Устанавливаются через HTTPS API.

#### Структура пака

```json
{
  "name": "k8s-pack",
  "version": "1.0.0",
  "tier": 2,
  "mcp_requires": ["kubectl-mcp", "helm-mcp"],
  "prompts": [
    "promt-k8s-deploy-rollout",
    "promt-k8s-pod-debug",
    "promt-k8s-helm-upgrade"
  ],
  "triggers": {
    "деплой, rollout, k8s, kubernetes, helm": "promt-k8s-deploy-rollout",
    "дебаг, crashloop, oom, pending, pod":    "promt-k8s-pod-debug"
  }
}
```

#### Доступные паки

| Пак | Промты | MCP-зависимости |
|-----|--------|-----------------|
| `k8s-pack` | deploy-rollout, pod-debug, helm-upgrade | kubectl-mcp, helm-mcp |
| `gamedev-pack` | roblox-map, unity-scene, godot-script | roblox-mcp, unity-mcp |
| `data-pack` | sql-migration, etl-pipeline, dbt-model | db-mcp |
| `ci-cd-pack` | promt-ci-cd-pipeline, promt-db-baseline-governance | github-mcp |
| `[your-pack]` | любые промты | любые MCP |

#### Приоритет загрузки

```
packs/{project}/  →  universal/  →  core/
```

---

## Полный конвейер проекта

Главная ценность системы — **7-этапный конвейер** превращения любой идеи
в production-реализацию. Каждый этап обслуживается своим промтом.

```
ИДЕЯ
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│  ЭТАП 1: IDEATION                                       │
│  promt-ideation                                         │
│  Генерация идей, оценка, приоритизация                  │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  ЭТАП 2: ANALYSIS                                       │
│  promt-analysis                                         │
│  Анализ требований, рисков, зависимостей                │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  ЭТАП 3: DESIGN                                         │
│  promt-design + promt-adr-implementation-planner        │
│  Архитектура, ADR, проектирование                       │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  ЭТАП 4: IMPLEMENTATION                                 │
│  promt-feature-add / promt-refactoring                  │
│  promt-context7-generation (актуальная docs)            │
│  Генерация кода с документацией из context7             │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  ЭТАП 5: TESTING                                        │
│  promt-quality-test                                     │
│  Тесты, Quality Gates A-H, валидация                    │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  ЭТАП 6: DEBUGGING / VERIFICATION                       │
│  promt-bug-fix + promt-verification                     │
│  promt-security-audit                                   │
│  Self-correction, соответствие ADR                      │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  ЭТАП 7: FINISH & DELIVERY                              │
│  promt-consolidation + promt-readme-sync                │
│  promt-index-update + promt-project-rules-sync          │
│  Документация, обновление индексов, delivery            │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
                    PRODUCTION ✅
```

### Запуск полного конвейера

```
run_prompt_chain("добавь авторизацию через JWT", [
    "ideation",
    "analysis",
    "design",
    "implementation",
    "testing",
    "verification",
    "finish"
])
```

Или просто:

```
"нужна авторизация через JWT"   use p9i
```

Роутер сам определит что это новая фича → запустит конвейер с нужного этапа.

### ADR Pipeline (архитектурные решения)

Отдельный конвейер для управления архитектурными решениями:

```
ADR ИДЕЯ
    │
    ▼
promt-adr-system-generator     ← Source of Truth, конституция
    │
    ▼
promt-adr-implementation-planner ← Планирование реализации
    │
    ▼
promt-feature-add / promt-refactoring ← Реализация
    │
    ▼
promt-verification             ← Соответствие ADR и кода
    │
    ▼
promt-consolidation            ← Консолидация изменений
    │
    ▼
promt-index-update             ← Обновление индексов
    │
    ▼
ADR ЗАКРЫТ ✅
```

### Распределение промтов по этапам

| Этап | Промты | Тир |
|------|--------|-----|
| **IDEATION** | promt-ideation, promt-mvp-baseline-generator-universal | UNIVERSAL |
| **ANALYSIS** | promt-analysis, promt-project-stack-dump, promt-project-adaptation | UNIVERSAL |
| **DESIGN** | promt-design, promt-adr-system-generator, promt-adr-implementation-planner | UNIVERSAL |
| **IMPLEMENTATION** | promt-feature-add, promt-refactoring, promt-context7-generation | CORE + UNIVERSAL |
| **TESTING** | promt-quality-test, promt-ci-cd-pipeline | CORE + PACK |
| **DEBUGGING** | promt-bug-fix, promt-security-audit | CORE |
| **VERIFICATION** | promt-verification, promt-project-rules-sync | UNIVERSAL |
| **FINISH** | promt-consolidation, promt-readme-sync, promt-index-update | UNIVERSAL |
| **DOMAIN** | k8s-pack, gamedev-pack, data-pack, ci-cd-pack | TIER 2 PACKS |

---

## Наша уникальность

### 1. Полный конвейер — нигде нет

Конкуренты дают инструменты. Мы даём **конвейер**.
От идеи до production в одной системе, с памятью проекта, с ADR.

### 2. Plugin Packs с `pack.json`

Стандартизированный формат пака — нигде в мире такого нет.
Подключил пак — получил промты + MCP-зависимости + триггеры в роутере.

### 3. Source of Truth — ADR как конституция

`promt-adr-system-generator` — это конституция проекта.
Вся система верифицирует что код соответствует архитектурным решениям.
Это то чего нет ни у одного конкурента.

### 4. NL Router

Пишешь на естественном языке — система сама определяет:
новая фича или баг, какой этап конвейера запустить, какой пак нужен.

### 5. Lazy Loading — −64% токенов

Загружается только нужный пак. Остальные 30+ промтов
не существуют в контексте во время выполнения.

### 6. Hybrid Storage + Memory

```
Redis       ←  горячие промты, кэш роутера, сессии
PostgreSQL  ←  версии, ADR история, аудит, проекты
Memory      ←  save_project_memory / get_project_memory
```

Система помнит проект между сессиями. Знает стек, соглашения, историю решений.

---

## MCP доступ через HTTPS

### Подключение через Claude Code

```bash
claude mcp add \
  --scope user \
  --header "AI_PROMPTS_API_KEY: your-api-key" \
  --transport http \
  p9i https://mcp.p9i.dev/mcp
```

### Подключение через конфиг

```json
{
  "mcpServers": {
    "p9i": {
      "type": "http",
      "url": "https://mcp.p9i.dev/mcp",
      "headers": {
        "AI_PROMPTS_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Доступные MCP-инструменты

| Инструмент | Назначение |
|-----------|-----------|
| `ai_prompts` | Универсальный роутер на естественном языке |
| `run_prompt` | Запустить конкретный промт |
| `run_prompt_chain` | Запустить полный конвейер: ideation → finish |
| `list_prompts` | Список всех промтов и паков |
| `install_pack` | Установить пак по имени |
| `get_project_memory` | Получить память проекта |
| `save_project_memory` | Сохранить память проекта |
| `adapt_to_project` | Автоопределение стека и адаптация |
| `context7_lookup` | Получить актуальную документацию |
| `clean_context` | Очистка контекста при превышении токенов |
| `get_available_mcp_tools` | Список доступных инструментов |

### Использование

```
"нужна фича JWT авторизации"      use p9i  →  полный конвейер
"задеплой в k8s"                  use p9i  →  k8s-pack
"создай карту Roblox"             use p9i  →  gamedev-pack
"проведи рефакторинг src/api/"    use p9i  →  codeshift-refactor
"обнови README"                   use p9i  →  readme-sync
"верифицируй соответствие ADR"    use p9i  →  verification
```

---

## Тренды 2026

| Тренд | Как используем |
|-------|----------------|
| **Context window war** | Lazy Loading −64% токенов |
| **Multi-agent pipelines** | 7-этапный конвейер ideation→finish |
| **ADR as code** | promt-adr-system-generator — Source of Truth |
| **Domain specialization** | Plugin Pack для каждого домена |
| **Prompt as code** | Версионирование, тесты, CI в PostgreSQL |
| **MCP как стандарт** | MCP-native, FastMCP 3.x |
| **HTTPS-first MCP** | HTTPS/SSE без локальной установки |

---

## Роадмап

### Q1 2026 — Core Stable + Pipeline
- [ ] Заморозить core: 5 промтов, спецификация финальная
- [ ] Стабилизировать `pack.json` v1
- [ ] Полный 7-этапный конвейер в production
- [ ] ADR Pipeline: adr-generator → planner → verification
- [ ] HTTPS MCP эндпоинт в production
- [ ] Core покрыт тестами на 100%

### Q2 2026 — Pack Ecosystem
- [ ] Pack Registry API через HTTPS
- [ ] Официальные паки: k8s, gamedev, data, ci-cd
- [ ] NL Router v2 — LLM-based, accuracy > 90%
- [ ] Multi-tenant: приватные паки по API-ключу
- [ ] GitHub Actions: автотесты промтов при коммите
- [ ] Quality Gates A-H автоматизированы

### Q3 2026 — Community
- [ ] Публичный реестр паков
- [ ] 10+ паков от сообщества
- [ ] Pack versioning: semver + rollback
- [ ] VS Code extension
- [ ] Метрики: какие паки, этапы, токен-расход

### Q4 2026 — Scale
- [ ] 25+ паков в реестре
- [ ] Enterprise: приватные паки, SSO, SLA
- [ ] GitHub App: автовыбор пака по репозиторию
- [ ] Multi-LLM: Claude, GPT-4o, Gemini, Llama

### 2027 — Platform
- [ ] Де-факто стандарт pack.json в MCP-экосистеме
- [ ] 100+ публичных паков
- [ ] Pack marketplace с монетизацией авторов

---

## Как не потерять уникальность

### Правила которые нельзя нарушать

```
PIPELINE first    — конвейер это главная ценность, не промты по отдельности
CORE frozen       — максимум 7 промтов в core, остальное в паки
ADR as truth      — adr-system-generator это конституция, не трогать
NL Router alive   — главная точка входа, не прятать за сложным API
pack.json stable  — заморозить спецификацию до Q3, совместимость навсегда
Lazy Loading on   — не отключать, это главное техническое преимущество
```

### Защитный ров

```
Q1  →  Стабильный конвейер + HTTPS
        "Это работает от идеи до production"

Q2  →  pack.json как стандарт
        "Все паки используют этот формат"

Q3  →  Публичный реестр
        "Нельзя скопировать — нужно копировать экосистему"

Q4  →  Комьюнити паков
        "Сеть самоподдерживается"

2027 → Network effect
        "Стандарт де-факто"
```

### Чего не делать

- Не дробить конвейер — он должен работать как единое целое
- Не добавлять промты в core — только в паки или universal
- Не ломать обратную совместимость pack.json — никогда
- Не копировать LangChain — они монолит, мы конвейер с экосистемой
- Не делать GUI первым — сначала HTTPS API и конвейер

---

## Конкуренты

| Система | Сильные стороны | Чего нет |
|---------|-----------------|----------|
| **MCP Prompts (нативный)** | Промты как примитив MCP | Нет конвейера, нет тиров, нет паков |
| **LangChain** | Цепочки, широкая экосистема | Монолит, нет NL роутинга, нет ADR |
| **Perplexity Agent API** | Один эндпоинт | Закрытый, нет паков, нет конвейера |
| **Cursor / Copilot** | AI в редакторе | Нет конвейера, нет ADR, нет паков |
| **Sweep AI** | Автоматизация PR | Только код, нет полного цикла |

Прямых конкурентов с полным конвейером + pack.json + NL Router + ADR нет.

---

## Технический стек

| Компонент | Выбор | Причина |
|-----------|-------|---------|
| MCP Server | FastMCP 3.x | 70% MCP-серверов, стандарт |
| Transport | HTTPS / SSE | Без локальной установки |
| Database | PostgreSQL 14+ | ADR версионирование, аудит |
| Cache | Redis 7+ | Горячие промты, кэш роутера |
| Validation | Pydantic v2+ | pack.json валидация |
| Python | 3.11+ | |

### LLM провайдеры

| Провайдер | Переменная | Модель | Статус |
|-----------|-----------|--------|--------|
| Z.ai | `ZAI_API_KEY` | GLM-4.7 | ✅ Default |
| MiniMax | `MINIMAX_API_KEY` | MiniMax-M2.7 | ✅ |
| OpenRouter | `OPENROUTER_API_KEY` | hunter-alpha | ✅ Free fallback |

### Внешние MCP

| MCP | Пак | Назначение |
|-----|-----|-----------|
| `context7` | universal | Актуальная документация |
| `kubectl-mcp` | k8s-pack | Kubernetes |
| `helm-mcp` | k8s-pack | Helm чарты |
| `roblox-mcp` | gamedev-pack | Roblox Studio |
| `[любой MCP]` | [любой пак] | Через `mcp_requires` |

---

## Метрики успеха

### Q1 2026
- Полный конвейер ideation→finish работает end-to-end
- Core frozen: 0 новых промтов после заморозки
- HTTPS uptime > 99%
- NL Router accuracy > 85%

### Q2 2026
- 4 официальных пака в production
- 50+ активных подключений через HTTPS
- Токен-расход −50% vs нативный MCP
- ADR Pipeline работает в 3+ реальных проектах

### Q3 2026
- 10+ паков в публичном реестре
- 200+ активных пользователей
- 3+ пака от внешних авторов

### Q4 2026
- 25+ паков (10 от комьюнити)
- 1000+ активных пользователей
- Первый enterprise клиент

---

## Быстрый старт

```bash
# 1. Подключить через Claude Code
claude mcp add \
  --scope user \
  --header "AI_PROMPTS_API_KEY: your-api-key" \
  --transport http \
  p9i https://mcp.p9i.dev/mcp

# 2. Установить паки для своего стека
install_pack("k8s-pack")
install_pack("ci-cd-pack")

# 3. Адаптировать под проект
"проанализируй мой проект и адаптируй систему"   use p9i

# 4. Работать — полный конвейер запускается одной фразой
"нужна фича JWT авторизации"     use p9i
"задеплой в k8s"                 use p9i
"верифицируй соответствие ADR"   use p9i
```

---

*Версия: 0.5.0*
*Статус: Active Development*
*Последнее обновление: March 2026*