# promt-system-adapt

## Назначение
Адаптирует ai-prompt-system под НОВЫЙ проект: автоматически определяет стек, подключает нужные MCP, настраивает маршрутизатор и генерирует недостающие промты.

## Категория
Universal

## Когда использовать
- "адаптируй систему под проект"
- "подключи ai-prompts к новому проекту"
- "настрой систему под {язык/фреймворк}"
- "init ai-promts"
- "инициализация ai-promts"
- "подключи систему к проекту"

## Входные данные
- `project_path` — путь к проекту (обязательно)
- `stack_hint` — подсказка по стеку (опционально)

---

## Алгоритм

### Шаг 1 — Распознавание проекта

Сканируем маркеры стека:

```python
fingerprint = adapt_to_project(path=project_path)
```

Что определяем:
- **Python** → pyproject.toml / requirements.txt / setup.py
- **JS/TS** → package.json / tsconfig.json
- **Go** → go.mod
- **Rust** → Cargo.toml
- **Java** → pom.xml / build.gradle
- **Ruby** → Gemfile
- **.NET** → *.csproj / *.sln
- **Multi** → несколько маркеров одновременно

Результат → `project_profile`:
```json
{
  "lang": "python",
  "frameworks": ["fastapi", "pydantic"],
  "test_runner": "pytest",
  "is_new": true,
  "has_ci": false
}
```

### Шаг 2 — Подбор внешних MCP через Context7

Для каждого фреймворка из `project_profile`:

```python
for lib in project_profile["frameworks"]:
    context7_lookup(library=lib, query="best practices patterns conventions")
```

Приоритет поиска:
1. **context7** → актуальная документация фреймворка
2. **get_available_mcp_tools** → какие MCP уже подключены
3. **save_project_memory** → кешируем найденное

### Шаг 3 — Аудит существующих промтов

```python
current_prompts = list_prompts()
```

Проверяем: какие промты есть, каких не хватает для данного стека.

**Матрица покрытия:**
- ✅ feature-add — есть
- ✅ bug-fix — есть
- ✅ quality-test — есть
- ❌ {lang}-specific — НУЖНО СОЗДАТЬ
- ❌ {framework}-api — НУЖНО СОЗДАТЬ

### Шаг 4 — Генерация недостающих промтов

Для каждого пробела в матрице:

```python
run_prompt("promt-prompt-creator", {
    "idea": f"промт для {lang}/{framework} специфики",
    "category": "",
    "context": context7_docs
})
```

Примеры авто-генерации:
- Go проект → создаёт `promt-go-conventions.md`
- Rust проект → создаёт `promt-rust-safety.md`
- Next.js → создаёт `promt-nextjs-app-router.md`

### Шаг 5 — Обновление маршрутизатора

Добавляет новые триггеры в `ai_prompts`:

```python
# Авто-добавляет в роутер:
new_routes = {
    f"{lang}, {framework}": f"promt-{lang}-conventions",
    f"{framework} api": f"promt-{framework}-api",
}
save_project_memory(key="custom_routes", value=new_routes)
```

### Шаг 6 — Сохранение профиля

```python
save_project_memory(key="project_fingerprint", value={
    "profile": project_profile,
    "mcp_sources": [...],  # использованные context7 libs
    "custom_prompts": [...],  # сгенерированные промты
    "routes_added": [...],  # новые маршруты
    "adapted_at": "timestamp"
})
```

### Шаг 7 — Отчёт адаптации

```
## System Adapt Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Проект: {name}
Стек: {lang} + {frameworks}
Новый: да / нет

MCP Sources:
  ✅ context7/{lib1} — {N} паттернов
  ✅ context7/{lib2} — {N} паттернов

Промты:
  📦 Использовано существующих: {N}
  ✨ Создано новых: {N}
    → promt-{name}.md
    → promt-{name}.md

Маршрутизатор:
  + {N} новых триггеров добавлено

Готово к использованию: "{task} use ai-prompts"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Выходной формат

1. **Project Profile** — JSON профиль стека
2. **Gap Analysis** — каких промтов не хватало
3. **New Prompts** — сгенерированные .md файлы
4. **Adapt Report** — итоговый отчёт

## Ограничения

- Не удаляет существующие промты
- Не ломает текущий маршрутизатор
- Новые промты добавляются, не заменяют базовые 30
- Кешируется в memory/ — работает между сессиями

## Тест

```
Подключи ai-prompts к новому Go проекту. use ai-prompts
```

или

```
Инициализация ai-promts для Python/FastAPI проекта. use ai-prompts
```
