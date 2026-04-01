# Agent Interaction After ADR-15: Explorer Integration

> **Status:** Planned (Post ADR-15 Implementation)
> **Related:** ADR-015, ADR-007

---

## Overview

ADR-15 introduces the **Explorer Agent** — a deep code analysis capability that becomes a **shared knowledge base** for all other agents. This document describes how agents will interact after ADR-15 is implemented.

---

## All p9i Agents

| Агент | Фокус | Триггеры |
|-------|-------|----------|
| `p9i` | **Unified router** | Всё (заменяет ai_prompts + p9i_nl) |
| `architect` | Architecture, ADRs | архитектура, спроектируй, adr |
| `developer` | Code generation | реализуй, добавь, создай |
| `reviewer` | Code review, security | проверь, ревью, аудит |
| `designer` | UI/UX | дизайн, интерфейс, ui |
| `devops` | CI/CD, K8s, Docker | deploy, ci-cd, docker |
| `migration` | System migration | миграция, переход |
| **`explorer`** | **Deep code analysis** | **как работает, trace, dependencies** |

---

## Architecture Interaction

```
                         ┌─────────────────────┐
                         │   p9i (ROUTER)      │
                         │  маршрутизирует     │
                         └──────────┬──────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
            ▼                       ▼                       ▼
    ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
    │   architect  │       │   reviewer    │       │  explorer     │
    └───────┬───────┘       └───────┬───────┘       └───────┬───────┘
            │                       │                       │
            │                       │                       │
            │◄──────────────────────┴───────────────────────►│
            │           ЗАПРОСЫ К EXPLORER                   │
            │
            │
    ┌───────┴───────┐       ┌───────┴───────┐       ┌───────────────┐
    │  developer    │       │   designer    │       │    devops     │
    └───────────────┘       └───────────────┘       └───────────────┘
```

---

## Explorer Agent Capabilities

Explorer provides all agents with:

| Capability | Description |
|------------|-------------|
| **Execution Path Tracing** | Trace data flow from entry points to storage |
| **Dependency Graph** | Visual representation of module relationships |
| **Impact Analysis** | Predict what will break if code changes |
| **Semantic Search** | Find code by intent, not just keywords |
| **Cross-File Analysis** | Track data transformations between modules |
| **Security Scanner** | Taint analysis, vulnerability detection |

---

## Agent-by-Agent Integration

### 1. architect + explorer

```
architect: "спроектируй микросервис для платежей"
    │
    ├─► explorer: "покажи существующую архитектуру"
    │   └── Returns: dependency graph, domain boundaries
    │
    ├─► explorer: "есть ли похожие сервисы?"
    │   └── Returns: similar patterns in codebase
    │
    └─► architect: "вот blueprint на основе существующей структуры"
```

**What architect gets:**
- Context about existing architecture BEFORE designing
- Sees where similar patterns already exist
- Avoids duplicating existing solutions

### 2. reviewer + explorer

```
reviewer: "проверь код на баги"
    │
    ├─► explorer: "найди все связи модуля"
    │   └── Returns: dependency graph
    │
    ├─► explorer: "trace data flow от user input"
    │   └── Returns: execution path с vulnerabilities
    │
    └─► reviewer: "нашёл 3 проблемы + impact analysis"
```

**What reviewer gets:**
- "X-ray vision" — sees beyond the code being reviewed
- Traces data to find subtle bugs
- Predicts what else might break

### 3. developer + explorer

```
developer: "добавь новую функцию"
    │
    ├─► explorer: "где находится нужный модуль?"
    │   └── Returns: file locations, existing patterns
    │
    ├─► explorer: "какие функции уже делают похожее?"
    │   └── Returns: similar functions
    │
    └─► developer: "понял структуру, реализую здесь"
```

**What developer gets:**
- Exact location for new code
- Understanding of existing patterns to follow
- Confidence that changes won't break hidden dependencies

### 4. designer + explorer

```
designer: "сделай дизайн кнопки"
    │
    ├─► explorer: "какие компоненты используют эту кнопку?"
    │   └── Returns: affected components
    │
    └─► designer: "вот дизайн с учётом зависимостей"
```

**What designer gets:**
- Understanding of component dependencies
- Context for design decisions

### 5. devops + explorer

```
devops: "подготовь deploy"
    │
    ├─► explorer: "какие сервисы зависят от изменяемого?"
    │   └── Returns: dependency list
    │
    ├─► explorer: "нужны ли миграции?"
    │   └── Returns: schema changes, backward compatibility
    │
    └─► devops: "вот порядок deploy + rollback план"
```

**What devops gets:**
- Deployment order based on dependencies
- Early warning about potential issues

### 6. migration + explorer

```
migration: "мигрируй на новую БД"
    │
    ├─► explorer: "какие модули используют старую БД?"
    │   └── Returns: all touchpoints
    │
    ├─► explorer: "какие запросы нужно изменить?"
    │   └── Returns: query patterns
    │
    └─► migration: "вот план миграции с минимальным downtime"
```

**What migration gets:**
- Complete list of modules to change
- Understanding of query patterns to update

---

## Comparison: Before vs After ADR-15

| Агент | БЕЗ explorer | С explorer |
|-------|--------------|-------------|
| **architect** | "Я спроектировал абстрактно" | "Я вижу ВСЮ структуру и проектирую на её основе" |
| **reviewer** | "Я прочитал файлы" | "Я трассировал данные и нашёл проблемы" |
| **developer** | "Я добавил где думал правильно" | "Я точно знаю где и как добавить" |
| **designer** | "Я сделал красиво" | "Я вижу как компонент встраивается" |
| **devops** | "Я деплою по порядку" | "Я вижу зависимости и риски" |
| **migration** | "Я мигрирую везде" | "Я мигрирую точечно с минимальным impact" |

---

## Example: Full Workflow

### Scenario: "Реализуй фичу авторизации"

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: architect задает вопрос explorer                        │
├─────────────────────────────────────────────────────────────────┤
│ architect: "покажи структуру существующего auth"                │
│ explorer → Returns:                                            │
│   - dependency graph: middleware → auth_service → token_store  │
│   - entry points: /login, /logout, /refresh                    │
│   - data flow: request → validator → JWT → Redis              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: architect проектирует новую архитектуру                 │
├─────────────────────────────────────────────────────────────────┤
│ architect: "добавлю refresh token rotation в auth_service"       │
│             "новый endpoint /refresh-analytics"                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: developer реализует код                                 │
├─────────────────────────────────────────────────────────────────┤
│ developer: "реализовал новый endpoint"                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: reviewer проверяет с помощью explorer                   │
├─────────────────────────────────────────────────────────────────┤
│ reviewer: "проверь изменения"                                   │
│   ├─► explorer: "проанализируй impact изменений"                │
│   │   └── Returns: affected files, tests, endpoints            │
│   │                                                         │
│   ├─► explorer: "trace data flow от нового endpoint"           │
│   │   └── Returns: execution path + vulnerabilities           │
│   │                                                         │
│ reviewer: "нашёл 1 potential vulnerability в token refresh"     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Summary

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   explorer = "мозг" который ЗНАЕТ структуру codebase        │
│                                                             │
│   Все агенты ЗАПРАШИВАЮТ информацию у explorer             │
│   и используют её для своих задач                          │
│                                                             │
│   p9i (router) → направляет запрос нужному агенту           │
│                                                             │
└─────────────────────────────────────────────────────────────┘

До ADR-15:
  Агенты работают независимо
  Каждый "видит" только свой контекст
  Решения принимаются с неполной информацией

После ADR-15:
  explorer = shared knowledge base о структуре кода
  Все агенты "умнеют" за счёт понимания whole system
  Решения принимаются на основе полной картины
```

---

## Related Documents

- [ADR-015: Code Explorer Agent](./adr/ADR-015-code-explorer-agent.md)
- [ADR-007: Multi-Agent Orchestrator](../explanation/adr/ADR-007-multi-agent-orchestrator.md)
- [MPV Specification](./MPV.md)
