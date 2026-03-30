---

dependencies:
- promt-verification
- promt-index-update
description: Оркестрация сложных multi-prompt workflows с зависимостями и параллелизацией
layer: Meta
name: promt-workflow-orchestration
status: active
tags:
- workflow
- orchestration
- pipeline
- automation
type: p9i
version: '1.2'
---

# AI Agent Prompt: Оркестрация workflow и цепочка задач

**Version:** 1.2
**Date:** 2026-03-18
**Purpose:** Оркестрация сложных multi-prompt workflows с зависимостями и параллелизацией

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Meta / Orchestration |
| **Время выполнения** | Варьируется (10–120 мин) |
| **Домен** | Workflow — multi-prompt orchestration |

**Пример запроса:**

> «Используя `promt-workflow-orchestration.md`, оркестрируй полный workflow
> для feature add: research → Context7 → ADR → implementation → verification.»

**Ожидаемый результат:**
- Определённый workflow с последовательностью промтов
- Зависимости между этапами
- Параллелизация где возможно
- Отчёт о выполнении workflow

---

## Когда использовать

- Для сложных multi-stage задач (feature add, refactoring, migration)
- Для выполнения MPV pipeline (ideation → finish)
- Для автоматизации repetitive workflows
- Для parallel execution независимых задач
- Для end-to-end testing и verification

---

## Mission Statement

Ты — AI-агент, специализирующийся на **оркестрации workflows** — управлении цепочками промтов с зависимостями.

Твоя задача:
1. **Определить workflow** — какие промты нужны и в какой последовательности
2. **Построить зависимости** — DAG (Directed Acyclic Graph) задач
3. **Параллелизовать** — определить независимые задачи для parallel execution
4. **Выполнить workflow** — запустить промты в правильном порядке
5. **Отследить прогресс** — мониторинг выполнения и failures

---

## Контракт синхронизации системы

Обязательные инварианты:
- Workflows всегда имеют DAG структуру (no cycles)
- Зависимости явно определены перед выполнением
- Failures прерывают workflow (или continue on error по конфигурации)
- Все промты в workflow существуют в registry
- Progress tracking через отчёты выполнения

---

## Шаг 0: Определение типа workflow

### 0.1. Встроенные workflows

```markdown
## Built-in Workflows

### 1. Feature Add Workflow

**Цель:** Добавить новый функционал в проект

**Промты:**
1. `promt-project-stack-dump.md` — анализ текущего состояния
2. `promt-context7-generation.md` — research best practices
3. `promt-feature-add.md` — ADR и реализация
4. `promt-verification.md` — верификация ADR и кода
5. `promt-index-update.md` — обновление index.md

**Зависимости:**
- 2 → 1 (нужно состояние проекта для Context7)
- 3 → 2 (нужно Context7 research для ADR)
- 4 → 3 (нужно ADR и код для верификации)
- 5 → 4 (нужно верификация для обновления index)

**Время:** 60–120 мин

### 2. Bug Fix Workflow

**Цель:** Исправить баг в коде

**Промты:**
1. `promt-bug-fix.md` — диагностика и фикс
2. `promt-verification.md` — проверка, что фикс не сломал ADR
3. (опционально) `promt-index-update.md` — если изменился прогресс ADR

**Зависимости:**
- 2 → 1 (нужно фикс для верификации)
- 3 → 2 (нужно верификация для обновления index)

**Время:** 30–90 мин

### 3. MPV Pipeline Workflow

**Цель:** Полный 7-stage pipeline от идеи до delivery

**Промты:**
1. `promt-ideation.md` — генерация идей
2. `promt-analysis.md` — анализ требований
3. `promt-design.md` — архитектурное проектирование
4. `promt-implementation.md` — реализация
5. `promt-testing.md` — тестирование
6. `promt-debugging.md` — самокоррекция
7. `promt-finish.md` — документация и delivery

**Зависимости:**
- Каждый этап зависит от предыдущего

**Время:** 180–240 мин

### 4. ADR Consolidation Workflow

**Цель:** Консолидация дублирующих ADR

**Промты:**
1. `promt-verification.md` — анализ текущего состояния
2. `promt-consolidation.md` — merge/deprecate/renumber
3. `promt-verification.md` — верификация консолидации
4. `promt-index-update.md` — обновление index.md

**Зависимости:**
- 2 → 1 (нужно состояние для консолидации)
- 3 → 2 (нужно консолидация для верификации)
- 4 → 3 (нужно верификация для обновления)

**Время:** 60–90 мин

### 5. Project Onboarding Workflow

**Цель:** Быстрый старт для новых проектов

**Промты:**
1. `promt-project-stack-dump.md` — анализ стека проекта
2. `promt-system-adapt.md` — автоматическая настройка
3. `promt-onboarding.md` — создание документации onboarding
4. `promt-index-update.md` — обновление index.md

**Зависимости:**
- 2 → 1 (нужно стек проекта для адаптации)
- 3 → 2 (нужно адаптация для onboarding)
- 4 → 3 (нужно onboarding для обновления)

**Время:** 30–60 мин
```

### 0.2. Custom Workflow Definition

```python
# Custom workflow definition
workflow = {
    "name": "Custom Feature with Security Review",
    "description": "Feature add with additional security audit",
    "stages": [
        {
            "name": "research",
            "prompt": "promt-project-stack-dump.md",
            "parallel": False
        },
        {
            "name": "context7",
            "prompt": "promt-context7-generation.md",
            "dependencies": ["research"],
            "parallel": False
        },
        {
            "name": "feature_add",
            "prompt": "promt-feature-add.md",
            "dependencies": ["context7"],
            "parallel": False
        },
        {
            "name": "security_audit",  # Additional stage
            "prompt": "promt-security-audit.md",
            "dependencies": ["feature_add"],
            "parallel": False
        },
        {
            "name": "verification",
            "prompt": "promt-verification.md",
            "dependencies": ["security_audit"],
            "parallel": False
        },
        {
            "name": "index_update",
            "prompt": "promt-index-update.md",
            "dependencies": ["verification"],
            "parallel": False
        }
    ],
    "on_failure": "stop",  # or "continue"
    "timeout": 7200  # seconds
}
```

---

## Шаг 1: Построение DAG зависимостей

### 1.1. Определить все этапы и зависимости

```python
# Build DAG
def build_dag(workflow_stages):
    """
    Build Directed Acyclic Graph from workflow stages.

    Args:
        workflow_stages: list of stage definitions

    Returns:
        Dictionary: {stage_name: [dependencies]}
    """
    dag = {}
    for stage in workflow_stages:
        name = stage["name"]
        deps = stage.get("dependencies", [])
        dag[name] = deps

    # Validate no cycles
    if has_cycles(dag):
        raise ValueError("Workflow has cycles")

    return dag

def has_cycles(dag):
    """Check if DAG has cycles using DFS."""
    visited = set()
    rec_stack = set()

    def dfs(node):
        if node in rec_stack:
            return True
        if node in visited:
            return False

        visited.add(node)
        rec_stack.add(node)

        for neighbor in dag.get(node, []):
            if dfs(neighbor):
                return True

        rec_stack.remove(node)
        return False

    for node in dag:
        if dfs(node):
            return True

    return False
```

### 1.2. Топологическая сортировка для выполнения

```python
def topological_sort(dag):
    """
    Perform topological sort to determine execution order.

    Args:
        dag: {stage_name: [dependencies]}

    Returns:
        List of stage names in execution order
    """
    in_degree = {node: 0 for node in dag}
    for node in dag:
        for dep in dag[node]:
            in_degree[node] += 1

    queue = [node for node in dag if in_degree[node] == 0]
    result = []

    while queue:
        node = queue.pop(0)
        result.append(node)

        for neighbor in dag.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(dag):
        raise ValueError("Cycle detected in DAG")

    return result
```

---

## Шаг 2: Определение параллелизации

### 2.1. Найти независимые задачи

```python
def find_parallel_tasks(dag):
    """
    Find tasks that can be executed in parallel.

    Args:
        dag: {stage_name: [dependencies]}

    Returns:
        List of lists (each list is a parallel batch)
    """
    execution_order = topological_sort(dag)
    parallel_batches = []

    while execution_order:
        # Find tasks with all dependencies completed
        ready = [
            task for task in execution_order
            if all(
                dep not in execution_order
                for dep in dag.get(task, [])
            )
        ]

        # Remove ready tasks from execution order
        for task in ready:
            execution_order.remove(task)

        parallel_batches.append(ready)

    return parallel_batches
```

### 2.2. Пример параллелизации

```markdown
## Parallel Execution Batches

### Feature Add Workflow (Sequential)

Все задачи зависят от предыдущих → без параллелизации:
```
Batch 1: research
Batch 2: context7
Batch 3: feature_add
Batch 4: verification
Batch 5: index_update
```

### Custom Workflow (Parallel)

Некоторые задачи независимы → параллельное выполнение:
```
Batch 1: research
Batch 2: context7
Batch 3: feature_add, security_review  # ← Parallel!
Batch 4: verification
Batch 5: index_update
```

**Время с параллелизацией:**
- Sequential: 60 мин
- Parallel: 50 мин (feature_add + security_review = 20 мин vs 30 мин)
```

---

## Шаг 3: Выполнение workflow

### 3.1. Запуск промтов в порядке

```python
async def execute_workflow(workflow, context=None):
    """
    Execute workflow stages in order with dependencies.

    Args:
        workflow: workflow definition dictionary
        context: context object to pass between stages

    Returns:
        dict with results, logs, and status
    """
    results = {}
    logs = []

    # Build DAG
    dag = build_dag(workflow["stages"])

    # Find parallel batches
    parallel_batches = find_parallel_tasks(dag)

    for i, batch in enumerate(parallel_batches):
        log_entry = {
            "batch": i + 1,
            "stages": batch,
            "parallel": len(batch) > 1
        }
        logs.append(log_entry)

        # Execute batch (parallel if len(batch) > 1)
        batch_results = await execute_batch(batch, workflow, context)
        results.update(batch_results)

        # Check for failures
        failures = [
            stage for stage, result in batch_results.items()
            if not result["success"]
        ]

        if failures and workflow.get("on_failure") == "stop":
            return {
                "status": "failed",
                "results": results,
                "logs": logs,
                "failed_stage": failures[0]
            }

    return {
        "status": "completed",
        "results": results,
        "logs": logs
    }

async def execute_batch(stages, workflow, context):
    """Execute a batch of stages (parallel if len > 1)."""
    if len(stages) == 1:
        # Sequential
        stage = stages[0]
        return {stage: await execute_stage(stage, workflow, context)}
    else:
        # Parallel
        tasks = [
            execute_stage(stage, workflow, context)
            for stage in stages
        ]
        results = await asyncio.gather(*tasks)
        return dict(zip(stages, results))

async def execute_stage(stage_name, workflow, context):
    """Execute a single stage (prompt)."""
    stage = next(
        s for s in workflow["stages"]
        if s["name"] == stage_name
    )

    try:
        # Get prompt
        prompt = get_prompt_by_name(stage["prompt"])

        # Execute prompt
        result = await execute_prompt(prompt, context)

        return {
            "success": True,
            "result": result,
            "stage": stage_name,
            "prompt": stage["prompt"],
            "duration": result.get("duration"),
            "output": result.get("output")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "stage": stage_name,
            "prompt": stage["prompt"]
        }
```

### 3.2. Пример выполнения

```bash
# Execute built-in workflow
mcp__p9i__run_prompt_chain \
  --idea "добавить OAuth аутентификацию через GitHub" \
  --stages ideation,analysis,design,implementation,testing,debugging,finish

# Execute custom workflow
mcp__p9i__run_prompt \
  --prompt promt-workflow-orchestration.md \
  --workflow "feature_add_with_security" \
  --context '{"feature": "OAuth GitHub"}'
```

---

## Шаг 4: Мониторинг и отчётность

### 4.1. Отслеживание прогресса

```python
def track_workflow_progress(execution_result):
    """
    Generate progress report from execution result.

    Args:
        execution_result: result from execute_workflow()

    Returns:
        dict with progress metrics
    """
    results = execution_result["results"]
    logs = execution_result["logs"]

    total_stages = len(results)
    successful = sum(
        1 for r in results.values()
        if r["success"]
    )
    failed = total_stages - successful

    total_duration = sum(
        r.get("duration", 0)
        for r in results.values()
        if r["success"]
    )

    return {
        "status": execution_result["status"],
        "total_stages": total_stages,
        "successful": successful,
        "failed": failed,
        "success_rate": f"{successful / total_stages * 100:.1f}%",
        "total_duration": total_duration,
        "parallel_batches": len([l for l in logs if l["parallel"]]),
        "logs": logs
    }
```

### 4.2. Отчёт о выполнении workflow

```markdown
# Workflow Execution Report
**Date:** 2026-03-18T12:00:00Z
**Workflow:** Feature Add with Security Review
**Status:** ✅ Completed

## Summary

| Metric | Value |
|--------|-------|
| **Total Stages** | 6 |
| **Successful** | 6 |
| **Failed** | 0 |
| **Success Rate** | 100% |
| **Total Duration** | 52 min |
| **Parallel Batches** | 1 |

## Execution Log

### Batch 1: Sequential

| Stage | Prompt | Duration | Status | Output |
|--------|---------|----------|--------|--------|
| research | promt-project-stack-dump.md | 5 min | ✅ | Stack analysis complete |
| context7 | promt-context7-generation.md | 8 min | ✅ | Best practices collected |
| feature_add | promt-feature-add.md | 15 min | ✅ | ADR-006 created, code implemented |
| security_audit | promt-security-audit.md | 12 min | ✅ | No security issues found |
| verification | promt-verification.md | 8 min | ✅ | ADR compliance 100% |
| index_update | promt-index-update.md | 4 min | ✅ | index.md updated |

### Batch 2: Parallel (N/A)

## Results

### ADR Created
- ADR-006-github-oauth-authentication.md

### Code Implemented
- `telegram-bot/app/auth/github_oauth.py` (new file)
- `telegram-bot/app/config.py` (updated with GitHub OAuth config)

### Verification Results
- ADR Compliance: 100%
- Code Quality: 100%
- Test Coverage: 72%

### Documentation
- index.md updated
- README.md updated

## Recommendations

- ✅ No issues found
- ✅ All stages completed successfully
- ✅ Workflow executed optimally (no delays)

## Next Steps

- [ ] Review ADR-006 with team
- [ ] Deploy to staging environment
- [ ] Monitor GitHub OAuth integration
```

---

## Шаг 5: Создание отчёта workflow

### 5.1. Структура отчёта

Сохранить в: `artifacts/workflows/workflow-report-{timestamp}.json`

```json
{
  "workflow_report": {
    "workflow_name": "Feature Add with Security Review",
    "executed_at": "2026-03-18T12:00:00Z",
    "status": "completed",
    "summary": {
      "total_stages": 6,
      "successful": 6,
      "failed": 0,
      "success_rate": "100%",
      "total_duration": 3120,
      "parallel_batches": 1
    },
    "execution_log": [
      {
        "batch": 1,
        "stages": [
          {
            "stage": "research",
            "prompt": "promt-project-stack-dump.md",
            "duration": 300,
            "status": "success",
            "output": "Stack analysis complete"
          }
          // ... more stages
        ],
        "parallel": false
      }
    ],
    "results": {
      "adr_created": ["ADR-006-github-oauth-authentication.md"],
      "code_implemented": [
        "telegram-bot/app/auth/github_oauth.py",
        "telegram-bot/app/config.py"
      ],
      "verification_results": {
        "adr_compliance": 100,
        "code_quality": 100,
        "test_coverage": 72
      }
    },
    "recommendations": [
      "No issues found",
      "All stages completed successfully",
      "Workflow executed optimally"
    ]
  }
}
```

---

## Финальный чеклист workflow

- [ ] Workflow определён (тип или custom)
- [ ] DAG построен (no cycles)
- [ ] Зависимости явно определены
- [ ] Параллелизация определена (если применимо)
- [ ] Workflow выполнен
- [ ] Прогресс отслежен
- [ ] Отчёт создан

---

## Связанные промпты

| Промпт | Когда использовать |
|--------|-------------------|
| `run_prompt_chain` | Для MPV pipeline (built-in) |
| `run_prompt` | Для single prompt execution |
| Все промты | Как stages в custom workflow |

---

## Метрики успеха workflow

| Метрика | Требование |
|---------|------------|
| DAG валиден | Нет циклов |
| Зависимости | Все явно определены |
| Success Rate | ≥ 95% |
| Failures | Обработаны (stop или continue) |
| Отчёт | Создан |

---

## Anti-patterns при оркестрации

| Anti-pattern | Правильный подход |
|--------------|------------------|
| Игнорировать зависимости | Всегда строить DAG |
| Не проверять циклы | Валидировать DAG перед выполнением |
| Не отслеживать failures | Логировать все failures |
| Не использовать параллелизацию | Оптимизировать parallel execution |
| Пропускать отчёты | Всегда создавать отчёт выполнения |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.2 | 2026-03-18 | Добавлена структура отчёта workflow |
| 1.1 | 2026-03-06 | Добавлена параллелизация execution |
| 1.0 | 2026-02-20 | Первая версия: basic workflow orchestration |

---

**Prompt Version:** 1.2
**Date:** 2026-03-18
