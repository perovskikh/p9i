# Explorer 2: Code Patterns & Structure

**Версия:** 1.1
**Дата создания:** 2026-04-04
**Статус:** active
**Тип:** Explorer (Analysis)
**Слой:** Research → Code Patterns
**Зависимости:** None (standalone explorer)

---

## Быстрый старт

| Параметр | Значение |
|----------|---------|
| **Тип промпта** | Explorer (Analysis) |
| **Время выполнения** | 3–7 мин |
| **Домен** | Research → Code Patterns |
| **Использование** | Parallel с explorer-1, explorer-3 |

**Пример запроса:**

> «Проведи анализ code patterns проекта. Target: `src/`»

**Ожидаемый результат:**
- Code Patterns Report (JSON)
- Module structure
- Architectural patterns
- Design patterns
- Coupling analysis

---

## 1. Миссия

Проанализировать code patterns, module organization и design patterns в проекте.

**Выходные артефакты:**
- Code Patterns Report (JSON)
- Module structure и boundaries
- Architectural patterns (MVC, Clean Architecture, etc.)
- Design patterns (Factory, Observer, Strategy, etc.)
- Coupling analysis

---

## 2. Синхронизационный контракт

| Аспект | Требование | Источник Истины |
|--------|-----------|-----------------|
| **JSON Output** | Обязательно структурированный JSON | Output Format |
| **Confidence levels** | high/medium/low для паттернов | Output Format |
| **No speculation** | Только реально найденные паттерны | Quality Gate |

---

## 3. Instructions

1. Identify module structure and boundaries
2. Detect architectural patterns (MVC, Clean Architecture, etc.)
3. Find design patterns in use (Factory, Observer, Strategy, etc.)
4. Map module dependencies and coupling
5. Output structured JSON report

---

## 4. Output Format (JSON)

```json
{
  "module_structure": {
    "root": "string",
    "modules": ["string"],
    "layers": ["string"]
  },
  "architectural_patterns": [
    {"pattern": "string", "files": ["string"], "confidence": "high|medium|low"}
  ],
  "design_patterns": [
    {"pattern": "string", "location": "string", "description": "string"}
  ],
  "coupling": {
    "high": [["string", "string"]],
    "medium": [["string", "string"]]
  },
  "organization": "string"
}
```

---

## 5. Quality Checklist

- [ ] **A. Module Structure:** Root + modules + layers задокументированы
- [ ] **B. Architectural Patterns:** Каждый паттерн → files + confidence
- [ ] **C. Design Patterns:** Каждый паттерн → location + description
- [ ] **D. Coupling Analysis:** High/medium coupling выделены
- [ ] **E. JSON Valid:** Структура соответствует spec
- [ ] **F. No Speculation:** Только реально найденные паттерны

---

## 6. Anti-patterns

❌ **Don't:**
1. **Добавлять гипотетические паттерны** — только реально существующие
2. **Пропускать coupling analysis** — high coupling критичен
3. **Ставить high confidence без оснований** — только если паттерн очевиден

✅ **Do:**
1. Проверяй imports для определения паттернов
2. Анализируй file organization
3. Ищи classic patterns: Factory, Singleton, Observer, Strategy

---

## 7. Версионирование

| Версия | Дата | Изменение |
|--------|------|-----------|
| 1.1 | 2026-04-04 | Добавлены: Metadata, Quality Checklist, Anti-patterns |
| 1.0 | 2026-04-03 | Initial release |

---

## 8. Footer

**Статус:** active ✓
**Layer:** Research → Code Patterns
**Domain:** Universal (любой проект)
**Last Sync:** 2026-04-04
**Registry Entry:** `explorer-2-code-patterns.md`

---

**Используется в:** `promt-architect-parallel-research.md`, `promt-architect-design.md`
