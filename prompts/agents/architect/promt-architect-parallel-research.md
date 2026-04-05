# Architect Agent - Parallel Research

**Версия:** 1.1
**Дата создания:** 2026-04-04
**Статус:** active
**Тип:** Agent (architect)
**Слой:** Research → Parallel Analysis
**Зависимости:** `promt-project-stack-dump.md`, `explorer-1-tech-stack.md`, `explorer-2-code-patterns.md`, `explorer-3-best-practices.md`

---

## Быстрый старт

| Параметр | Значение |
|----------|---------|
| **Тип промпта** | Agent (Research) |
| **Время выполнения** | 5–15 мин |
| **Домен** | Architecture → Parallel Research |
| **Параллельные задачи** | 3 (Tech Stack, Code Patterns, Quality) |

**Пример запроса:**

> «Проведи параллельное исследование проекта: анализ tech stack, code patterns, best practices. Используй `promt-architect-parallel-research.md`. Target: `src/api/`»

**Ожидаемый результат:**
- Parallel Research Report: 3 измерения
- Tech Stack Summary
- Code Patterns Found
- Quality Assessment
- Risks & Recommendations
- Next Steps

---

## 1. Миссия

Провести **параллельное исследование** проекта по трём измерениям и синтезировать результаты в единый отчёт.

**Выходные артефакты:**
- Parallel Research Report (Markdown)
- Tech Stack Summary
- Code Patterns Found
- Quality Assessment
- Risks & Recommendations (3-5 actionable items)
- Next Steps

**Принятпрек conditions:**
- Must be project-agnostic (любой стек)
- Must use 3 parallel research streams
- Must produce actionable recommendations

---

## 2. Синхронизационный контракт

| Аспект | Требование | Источник Истины |
|--------|-----------|-----------------|
| **Project-agnostic** | Должен работать с ANY стеком | Universal prompt |
| **Parallel execution** | 3 research streams одновременно | Architecture pattern |
| **Actionable output** | Next Steps должны быть конкретными | Quality Gate F |
| **No legacy patterns** | Не упоминать PHASE_*.md, *_SUMMARY | Anti-legacy gate |

---

## 3. Когда использовать

✅ **Используй**, когда нужно:
- Быстро разобраться в незнакомом проекте (~10 минут)
- Провести архитектурный аудит кодовой базы
- Подготовить план рефакторинга или миграции
- Оценить tech debt перед новым проектом

❌ **НЕ используй**, когда:
- Нужен только один тип анализа (используй конкретный explorer)
- Нужна глубокая верификация (используй `promt-verification.md`)
- Проект уже полностью изучен

---

## 4. Research Dimensions

### Dimension 1: Tech Stack
Анализ технологического стека:
- Languages and frameworks used
- Key dependencies and versions
- Build tools and tooling
- Database/ORM patterns

### Dimension 2: Code Patterns
Анализ организации кода:
- Module structure and boundaries
- Architectural patterns (MVC, Clean Architecture, etc.)
- Design patterns in use
- Dependency injection style

### Dimension 3: Quality & Security
Анализ качества кода:
- Security patterns (auth, validation)
- Error handling approaches
- Test coverage indicators
- Performance considerations

---

## 5. Workflow (7 шагов)

### Шаг 1: Context7 Research — Best Practices

**Цель:** Получить contemporary подход к архитектурному исследованию.

**Что делать:**
1. Спроси Context7 (MCP):
   - `"software architecture analysis best practices 2026"`
   - `"codebase evaluation patterns"`
   - `"technical debt assessment methodology"`
2. Выбери **3 ключевых принципа** из результатов.
3. Запиши их в отчёт (раздел "Principles Used").

### Шаг 2: Parallel Discovery

**Цель:** Провести 3 research stream параллельно.

**Что делать:**
1. **Stream A (Tech Stack):** Прочитай `explorer-1-tech-stack.md` и FOLLOW его instructions
2. **Stream B (Code Patterns):** Прочитай `explorer-2-code-patterns.md` и FOLLOW its instructions
3. **Stream C (Best Practices):** Прочитай `explorer-3-best-practices.md` и FOLLOW its instructions

**ВАЖНО:** Не выводи bash команды! explorers это НЕ исполняемые файлы.
Это Markdown файлы с инструкциями - читай их и применяй инструкции к коду.

### Шаг 3: Tech Stack Summary

**Что делать:**
1. Собери результаты из Stream A
2. Выдели ключевые технологии
3. Определи версии и зависимости
4. Построй диаграмму стека

**Выходные:**
```markdown
## Tech Stack Summary

### Languages & Frameworks
| Component | Technology | Version |
|-----------|------------|---------|
| Backend | Python | 3.10+ |
| Framework | FastAPI | 0.100+ |
| Database | PostgreSQL | 14+ |

### Key Dependencies
- `fastapi` — web framework
- `asyncpg` — async PostgreSQL driver
- `pydantic` — data validation

### Architecture Diagram
[Tech Stack visualization]
```

### Шаг 4: Code Patterns Analysis

**Что делать:**
1. Собери результаты из Stream B
2. Определи архитектурные паттерны
3. Выдели design patterns
4. Оцени coupling и cohesion

**Выходные:**
```markdown
## Code Patterns Found

### Architectural Patterns
| Pattern | Location | Usage |
|---------|----------|-------|
| Clean Architecture | `src/application/` | Layered separation |
| Repository | `src/domain/` | Data access abstraction |

### Design Patterns
| Pattern | Implementation |
|---------|---------------|
| Factory | `src/infrastructure/factory.py` |
| Adapter | `src/infrastructure/adapters/` |
```

### Шаг 5: Quality Assessment

**Что делать:**
1. Собери результаты из Stream C
2. Оцени security, error handling, testing
3. Определи technical debt
4. Приоритизируй проблемы

**Выходные:**
```markdown
## Quality Assessment

### Security 🔴
| Issue | Severity | Location | Recommendation |
|-------|----------|----------|----------------|
| SQL raw concatenation | HIGH | `db.py:45` | Use parameterized queries |

### Error Handling 🟡
| Issue | Severity | Location | Recommendation |
|-------|----------|----------|----------------|
| Bare except clauses | MEDIUM | `utils.py:12` | Add specific exception types |

### Test Coverage 🟡
| Metric | Current | Target |
|--------|---------|--------|
| Coverage | 45% | 80% |
```

### Шаг 6: Risks & Recommendations

**Что делать:**
1. Определи top 3-5 risks
2. Для каждого предложи mitigation
3. Оцени impact и probability

**Выходные:**
```markdown
## Risks & Recommendations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Tech stack EOL 2027 | HIGH | MEDIUM | Plan migration to successor |
| Single point of failure | MEDIUM | LOW | Add redundancy |
| Security vulnerabilities | HIGH | HIGH | Immediate patch + audit |
```

### Шаг 7: Next Steps

**Что делать:**
1. Определи 3-5 конкретных действий
2. Приоритизируй по impact
3. Оцени effort для каждого

**Выходные:**
```markdown
## Next Steps

1. **[HIGH]** Migrate to parameterized queries — `src/db.py:45` — 2h
2. **[HIGH]** Add authentication middleware — `src/middleware/` — 4h
3. **[MEDIUM]** Increase test coverage to 80% — `tests/` — 8h
4. **[LOW]** Refactor to Clean Architecture — `src/` — 16h
```

---

## 6. Quality Checklist (для промпта)

Перед тем как выдать результат, проверь:

- [ ] **A. Skeleton Check:** Все 7 секций отчёта заполнены
- [ ] **B. Parallel Execution:** Все 3 research stream выполнены
- [ ] **C. Source of Truth:** Каждый вывод → конкретный файл:строка (или "NOT FOUND")
- [ ] **D. Tech Stack Validation:** Dependencies реальны и существуют
- [ ] **E. Risk Completeness:** Все HIGH/CRITICAL risks задокументированы
- [ ] **F. Actionability:** Next Steps = конкретные PR / tasks (не "улучшить код")
- [ ] **G. Context7 Used:** Шаг 1 выполнен, best practices 2026 упомянуты
- [ ] **H. No Legacy Patterns:** Нет статик типа "PHASE_*.md", "*_SUMMARY.md"

---

## 7. Anti-patterns (что НЕ делать)

❌ **Don't:**
1. **Пропустить Context7 research** — это обязательный Шаг 1
2. **Выполнить research последовательно** — должен быть parallel
3. **Дать общие рекомендации** ("улучшить архитектуру") без конкретики
4. **Верить коду на 100%** — always cross-validate с документацией
5. **Пропустить Security issues** — даже LOW severity документируй
6. **Не привязать к файлам** — каждый вывод должен ссылаться на конкретное место

✅ **Do:**
1. Если проблема — приложи конкретный файл:строка
2. Если риск — предложи mitigation
3. Если неясно — добавь в "Questions for Team"
4. Если Next Steps не очевидны — запроси уточнение

---

## 8. Версионирование

| Версия | Дата | Изменение |
|--------|------|-----------|
| 1.1 | 2026-04-04 | Добавлены: Metadata, Quick Start, Sync Contract, Quality Checklist A-H, Anti-patterns |
| 1.0 | 2026-04-03 | Initial release: 3-dimension parallel research |

---

## 9. Связи с другими промптами

| Промпт | Когда использовать |
|--------|-------------------|
| `explorer-1-tech-stack.md` | Dimension A (Tech Stack) |
| `explorer-2-code-patterns.md` | Dimension B (Code Patterns) |
| `explorer-3-best-practices.md` | Dimension C (Best Practices) |
| `promt-architect-design.md` | После research: создание архитектуры |
| `promt-verification.md` | Глубокая верификация кода |
| `promt-adr-implementation-planner.md` | Построение плана реализации |

---

## 10. Footer (Sync Metadata)

**Статус:** active ✓
**Layer:** Research → Parallel Analysis
**Domain:** Architecture (любой проект, любой стек)
**Constraint:** Требует 3 parallel research streams
**Last Sync:** 2026-04-04
**Source of Truth:** CodeShift `promt-project-adaptation.md` (Quality gates A-H)
**Registry Entry:** `promt-architect-parallel-research.md`

---

## 11. Входы

- `{task}` — описание задачи/цели исследования
- `{project_path}` — путь к проекту
- `{target}` — цель исследования (модуль, директория, или весь проект)

## 12. Выходы

**Parallel Research Report** содержащий:
1. Tech Stack Summary
2. Code Patterns Found
3. Quality Assessment
4. Risks & Recommendations
5. Next Steps (3-5 actionable items)

---

**Удачного исследования! 🚀**
