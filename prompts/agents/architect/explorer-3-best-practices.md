# Explorer 3: Best Practices & Quality

**Версия:** 1.1
**Дата создания:** 2026-04-04
**Статус:** active
**Тип:** Explorer (Quality)
**Слой:** Research → Best Practices
**Зависимости:** None (standalone explorer)

---

## Быстрый старт

| Параметр | Значение |
|----------|---------|
| **Тип промпта** | Explorer (Quality) |
| **Время выполнения** | 3–7 мин |
| **Домен** | Research → Quality & Security |
| **Использование** | Parallel с explorer-1, explorer-2 |

**Пример запроса:**

> «Проведи анализ quality & best practices проекта. Target: `src/`»

**Ожидаемый результат:**
- Quality Report (JSON)
- Security issues
- Performance issues
- Testing coverage
- Error handling assessment
- Maintainability score

---

## 1. Миссия

Проанализировать code quality, security, performance и maintainability проекта.

**Выходные артефакты:**
- Best Practices Report (JSON)
- Security issues (severity + location)
- Performance anti-patterns
- Test coverage assessment
- Error handling patterns
- Maintainability score

---

## 2. Синхронизационный контракт

| Аспект | Требование | Источник Истины |
|--------|-----------|-----------------|
| **JSON Output** | Обязательно структурированный JSON | Output Format |
| **Scores** | 0-100 для каждой категории | Output Format |
| **Severity levels** | high/medium/low для issues | Output Format |

---

## 3. Instructions

1. Check for security vulnerabilities (hardcoded secrets, SQL injection vectors)
2. Identify performance anti-patterns (N+1, memory leaks)
3. Assess test coverage and quality
4. Evaluate error handling patterns
5. Output structured JSON report

---

## 4. Output Format (JSON)

```json
{
  "security": {
    "issues": [{"severity": "high|medium|low", "file": "string", "issue": "string"}],
    "score": "number (0-100)"
  },
  "performance": {
    "issues": [{"type": "string", "location": "string"}],
    "score": "number (0-100)"
  },
  "testing": {
    "coverage": "number (0-100)",
    "patterns": ["string"]
  },
  "error_handling": {
    "score": "number (0-100)",
    "issues": ["string"]
  },
  "maintainability": {
    "score": "number (0-100)",
    "issues": ["string"]
  }
}
```

---

## 5. Quality Checklist

- [ ] **A. Security:** Issues → severity + file + description
- [ ] **B. Performance:** Anti-patterns → type + location
- [ ] **C. Testing:** Coverage + patterns
- [ ] **D. Error Handling:** Score + issues
- [ ] **E. Maintainability:** Score + issues
- [ ] **F. JSON Valid:** Структура соответствует spec

---

## 6. Anti-patterns

❌ **Don't:**
1. **Игнорировать HIGH severity security issues** — документируй все
2. **Пропускать performance anti-patterns** — N+1, memory leaks критичны
3. **Ставить высокие scores без оснований** — только реальные данные

✅ **Do:**
1. Ищи hardcoded secrets (API keys, passwords)
2. Ищи SQL injection vectors (raw SQL concatenation)
3. Ищи N+1 queries (loops with DB calls)
4. Оценивай test coverage реально

---

## 7. Версионирование

| Версия | Дата | Изменение |
|--------|------|-----------|
| 1.1 | 2026-04-04 | Добавлены: Metadata, Quality Checklist, Anti-patterns |
| 1.0 | 2026-04-03 | Initial release |

---

## 8. Footer

**Статус:** active ✓
**Layer:** Research → Best Practices
**Domain:** Universal (любой проект)
**Last Sync:** 2026-04-04
**Registry Entry:** `explorer-3-best-practices.md`

---

**Используется в:** `promt-architect-parallel-research.md`, `promt-architect-design.md`
