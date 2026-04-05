# Explorer 1: Tech Stack Analysis

**Версия:** 1.1
**Дата создания:** 2026-04-04
**Статус:** active
**Тип:** Explorer (Research)
**Слой:** Research → Tech Stack Analysis
**Зависимости:** None (standalone explorer)

---

## Быстрый старт

| Параметр | Значение |
|----------|---------|
| **Тип промпта** | Explorer (Analysis) |
| **Время выполнения** | 2–5 мин |
| **Домен** | Research → Tech Stack |
| **Использование** | Parallel с explorer-2, explorer-3 |

**Пример запроса:**

> «Проведи анализ tech stack проекта. Target: `src/`»

**Ожидаемый результат:**
- Tech Stack Report (JSON)
- Languages detected
- Frameworks identified
- Dependencies mapped
- Tooling documented

---

## 1. Миссия

Проанализировать технологический стек проекта: языки, фреймворки, зависимости и tooling.

**Выходные артефакты:**
- Tech Stack Report (JSON)
- Languages with file counts
- Frameworks с purpose
- Dependencies (critical)
- Tooling (build, test, lint)

---

## 2. Синхронизационный контракт

| Аспект | Требование | Источник Истины |
|--------|-----------|-----------------|
| **JSON Output** | Обязательно структурированный JSON | Output Format |
| **File counts** | Для каждого языка/фреймворка | Output Format |
| **No speculation** | Только реально найденные | Quality Gate |

---

## 3. Instructions

1. Identify primary language(s) from file extensions and package managers
2. Detect frameworks via dependencies and patterns
3. Map tooling: build systems, linters, test runners
4. Document version constraints if found
5. Output structured JSON report

---

## 4. Output Format (JSON)

```json
{
  "languages": [
    {"name": "string", "files": "number", "extensions": ["string"]}
  ],
  "frameworks": [
    {"name": "string", "purpose": "string", "files": "number"}
  ],
  "dependencies": {
    "total": "number",
    "critical": ["string"]
  },
  "tooling": {
    "build": ["string"],
    "test": ["string"],
    "lint": ["string"]
  },
  "env_files": ["string"]
}
```

---

## 5. Quality Checklist

- [ ] **A. Languages Found:** Каждый язык → file count + extensions
- [ ] **B. Frameworks Identified:** Каждый фреймворк → purpose
- [ ] **C. Dependencies:** critical dependencies выделены
- [ ] **D. Tooling:** build, test, lint системы задокументированы
- [ ] **E. JSON Valid:** Структура соответствует spec
- [ ] **F. No Speculation:** Только реально найденные технологии

---

## 6. Anti-patterns

❌ **Don't:**
1. **Добавлять не найденные технологии** — только реально существующие
2. **Пропускать tooling** — build, test, lint важны
3. **Давать неполный JSON** — все поля обязательны

✅ **Do:**
1. Проверяй package managers (requirements.txt, package.json, go.mod)
2. Проверяй imports для определения фреймворков
3. Считай файлы по расширениям

---

## 7. Версионирование

| Версия | Дата | Изменение |
|--------|------|-----------|
| 1.1 | 2026-04-04 | Добавлены: Metadata, Quality Checklist, Anti-patterns |
| 1.0 | 2026-04-03 | Initial release |

---

## 8. Footer

**Статус:** active ✓
**Layer:** Research → Tech Stack
**Domain:** Universal (любой проект)
**Last Sync:** 2026-04-04
**Registry Entry:** `explorer-1-tech-stack.md`

---

**Используется в:** `promt-architect-parallel-research.md`, `promt-architect-design.md`
