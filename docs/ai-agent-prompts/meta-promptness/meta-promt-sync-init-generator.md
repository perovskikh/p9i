# Мета-промпт: Генератор Sync & Init промптов для CodeShift

**Версия:** 1.0  **Дата:** 2026-03-06  **Тип:** Meta
**Purpose:** Генерирует три операционных промпта по новой самодокументирующейся структуре фабрики v3.0

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Meta (генератор) |
| **Время выполнения** | 20–40 мин |
| **Домен** | Инициализация агента + синхронизация документации |

**Пример запроса:**

> «Используя `meta-promt-sync-init-generator.md`, сгенерируй три промпта: `promt-agent-init.md`,
> `promt-project-rules-sync.md`, `promt-readme-sync.md` по новой самодокументирующейся структуре.»

**Ожидаемый результат:**
- Три готовых промпта с полной самодокументацией (`## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`)
- Три строки добавлены в индекс-таблицу `README.md`
- Quality gates A–J пройдены для каждого файла

---

## Когда использовать

- Нужно воссоздать `promt-agent-init.md` после удаления по причине несоответствия структуре
- Нужно воссоздать `promt-project-rules-sync.md` с самодокументацией
- Нужно воссоздать `promt-readme-sync.md` (новый scope: только индекс-таблица README, не 6 разных секций)
- После обновления фабрики `meta-promt-prompt-generation.md` и нужна полная пересборка

---

## Контракт синхронизации системы

> **Source of truth:** `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`
> **Фабрика промптов:** `docs/ai-agent-prompts/meta-promptness/meta-promt-prompt-generation.md` v3.0+
> Этот мета-промпт подчиняется source of truth. При конфликте — приоритет у meta-prompt.

**Обязательные инварианты:**
- ADR идентификация по **topic slug** (номера нестабильны)
- Каждый генерируемый промпт: **самодокументирован** (все характеристики внутри файла)
- `docs/official_document/` — READ-ONLY
- Anti-legacy: не создавать `PHASE_*.md`, `*_REPORT.md`, `*_SUMMARY.md`
- В README добавляется ровно одна строка на промпт (индекс-таблица, не 6 секций)

---

## Шаг 0: Проверка зависимостей

Перед генерацией убедиться:

```bash
# Проверить версию фабрики
head -5 docs/ai-agent-prompts/meta-promptness/meta-promt-prompt-generation.md
# Должно быть: **Версия:** 3.0 или выше

# Убедиться что файлы не существуют (или удалены)
ls docs/ai-agent-prompts/promt-agent-init.md 2>/dev/null && echo "EXISTS - удали перед регенерацией"
ls docs/ai-agent-prompts/promt-project-rules-sync.md 2>/dev/null && echo "EXISTS - удали перед регенерацией"
ls docs/ai-agent-prompts/promt-readme-sync.md 2>/dev/null && echo "EXISTS - удали перед регенерацией"
```

---

## Шаг 1: Context7 исследование (ОБЯЗАТЕЛЬНО)

Перед генерацией каждого промпта выполнить Context7-запрос для его домена:

| Библиотека | Context7 ID | Для промпта |
|---|---|---|
| MkDocs Material | `/squidfunk/mkdocs-material` | promt-readme-sync.md |
| Diátaxis | `/diataxis/diataxis` | promt-project-rules-sync.md |
| Claude prompt engineering | `/anthropics/prompt-eng-interactive-tutorial` | promt-agent-init.md |
| Aiogram 3.x | `/websites/aiogram_dev_en_v3_22_0` | promt-agent-init.md |

Запросить best practices:
1. Структура документации prompt-систем (самодокументация)
2. Паттерны инициализации AI-агентов
3. Стандарты синхронизации технической документации

---

## Шаг 2: Генерация `promt-agent-init.md`

**Назначение:** Обязательная инициализация AI-агента перед работой с CodeShift.

**Тип:** Meta | **Время:** 10–20 мин

### Спецификация содержимого

**`## Быстрый старт`:**
```
| Параметр | Значение |
| Тип | Meta |
| Время | 5–10 мин |
| Домен | Инициализация агента |

Пример запроса:
«Используя promt-agent-init.md, выполни обязательную инициализацию:
загрузи контекст проекта, проверь ADR, выбери промпт для задачи
и задекларируй инварианты.»

Ожидаемый результат:
- Агент подтвердил загрузку всех 6 контекстных файлов
- Pass rate ADR зафиксирован
- Промпт для задачи выбран из decision tree
- Инварианты задекларированы явно
```

**`## Когда использовать`:**
- В начале любой новой сессии работы с CodeShift
- Перед выполнением любого операционного промпта
- При смене задачи в рамках сессии
- После длительного перерыва в работе с проектом

**Шаги workflow (6 шагов):**

**Шаг 0: Загрузка контекста (ОБЯЗАТЕЛЬНЫЙ)**
Прочитать полностью:
1. `CLAUDE.md` — инструкции для Claude
2. `.github/copilot-instructions.md` — инструкции для Copilot
3. `docs/ai-agent-prompts/README.md` — навигация по промптам
4. `docs/explanation/adr/index.md` — canonical topic slugs
5. `docs/rules/project-rules.md` — стандарты разработки
6. `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md` — source of truth

**Шаг 1: Context7 (ОБЯЗАТЕЛЬНЫЙ)**
Запросить лучшие практики для технологий, задействованных в планируемой задаче.
Если задача неизвестна — использовать стек по умолчанию: aiogram + FastAPI + Kubernetes.

**Шаг 2: Диагностика ADR (ОБЯЗАТЕЛЬНЫЙ)**
```bash
./scripts/verify-all-adr.sh --quick
./scripts/verify-adr-checklist.sh
```
Зафиксировать: pass rate, список активных ADR.

**Шаг 3: Выбор промпта по decision tree**
Использовать decision tree из `README.md` раздел 3.
Выбрать ровно один промпт для текущей задачи.

**Шаг 4: Декларация инвариантов**
Явно перечислить 9 инвариантов (topic slug, canonical DB, K8s abstraction и т.д.).

**Шаг 5: Сообщение готовности**
```
Готов. Использую promt-X.md. Pass rate: Y%. Active ADR: Z.
Инварианты приняты: topic slug, READ-ONLY zones, Anti-legacy, Canonical DB, K8s abstraction.
```

**ADR Topic Registry (релевантные):**
- `prompt-system-improvement-strategy` (ADR-022)
- `documentation-generation` (ADR-011)
- `bash-formatting-standard` (ADR-012)
- `k8s-provider-abstraction` (ADR-010)
- `telegram-bot-saas-platform` (ADR-017)

**Anti-patterns:**
1. Начало работы без инициализации
2. Использование ADR-XXX номеров вместо topic slug
3. Изменение READ-ONLY зон
4. Создание legacy-файлов

**Связанные промпты:** (после `promt-agent-init.md`) → любой операционный промпт из decision tree

---

## Шаг 3: Генерация `promt-project-rules-sync.md`

**Назначение:** Аудит и исправление структурных, форматных и инвариантных ошибок в `docs/rules/project-rules.md`.

**Тип:** Infra | **Время:** 30–60 мин

### Спецификация содержимого

**`## Быстрый старт`:**
```
| Параметр | Значение |
| Тип | Infra |
| Время | 30–60 мин |
| Домен | Документация / project-rules.md |

Пример запроса:
«Используя promt-project-rules-sync.md, выполни аудит и исправление
docs/rules/project-rules.md: добавь раздел AI Instructions Sync Rules,
восстанови раздел Рабочие процессы, замени ADR-XXX на topic slugs.»

Ожидаемый результат:
- project-rules.md обновлён с разделом AI Instructions Sync Rules
- Все ADR-XXX заменены на canonical topic slugs
- Раздел «Рабочие процессы» восстановлен
- Файл компактен: дублирующиеся формулировки удалены
```

**`## Когда использовать`:**
- В `project-rules.md` обнаружены ADR-XXX номера (нарушение topic slug-first)
- Отсутствует раздел о правилах синхронизации AI-инструкций (Copilot + Claude)
- Раздел «Рабочие процессы» деградировал или исчез
- После обновления `copilot-instructions.md` или `CLAUDE.md` нужна синхронизация

**Шаги workflow (6 шагов):**

**Шаг 0: Input Validation**
1. Прочитать `docs/rules/project-rules.md`
2. Прочитать `docs/explanation/adr/index.md` для маппинга slug → номер
3. Прочитать `.github/copilot-instructions.md` и `CLAUDE.md`
4. Построить таблицу аудита: что присутствует / что отсутствует

**Шаг 1: Context7 (ОБЯЗАТЕЛЬНЫЙ)**
Запросить best practices по документированию AI instructions:
- MkDocs Material (структура документов)
- Diátaxis (категоризация документации)

**Шаг 2: Раздел AI Instructions Sync Rules**
Добавить раздел `## 📋 AI Instructions Sync Rules`:
- Общее правило: все AI-инструкции синхронны с ADR topic slugs
- GitHub Copilot: файл, назначение, ключевые разделы, правила обновления
- Claude (Claude Code): файл, назначение, ключевые разделы, правила обновления
- Workflow синхронизации (4 шага)

**Шаг 3: Восстановление раздела «Рабочие процессы»**
Подразделы: Git Flow, Деплой и идемпотентность, CI/CD Pipeline,
Ссылки на how-to руководства.

**Шаг 4: Замена ADR-XXX → topic slugs**
1. Найти все `ADR-[0-9]+` в файле
2. Заменить на canonical topic slug из `index.md`
3. Пути файлов ADR остаются без изменений

**Шаг 5: Верификация**
```bash
make docs-prompt-guard
make docs-check-mkdocs-nav
./scripts/check-topic-slug-first.sh docs/rules/project-rules.md
```

**ADR Topic Registry (релевантные):**
- `documentation-generation` (ADR-011)
- `bash-formatting-standard` (ADR-012)
- `prompt-system-improvement-strategy` (ADR-022)
- `infrastructure-consolidation-dry` (ADR-023)
- `telegram-bot-saas-platform` (ADR-017)

**Anti-patterns:**
1. Создание новых файлов вместо редактирования in-place
2. Нарушение Diátaxis классификации
3. Добавление ADR-XXX номеров вместо topic slugs
4. Раздувание за счёт дублирования одного правила в нескольких местах

**Связанные промпты:** → `promt-copilot-instructions-update.md` (после), → `promt-sync-optimization.md`

---

## Шаг 4: Генерация `promt-readme-sync.md`

**Назначение:** Обслуживание индекс-таблицы `docs/ai-agent-prompts/README.md`.

**Тип:** Infra | **Время:** 15–30 мин

> ⚠️ **НОВЫЙ SCOPE:** Этот промпт обслуживает только индекс-таблицу реестра промптов.
> Он НЕ синхронизирует 6 разных секций (это устаревший подход, приведший к разрозненности).
> Полная документация каждого промпта живёт ВНУТРИ файла промпта (секции Быстрый старт / Когда использовать / Журнал изменений).

### Спецификация содержимого

**`## Быстрый старт`:**
```
| Параметр | Значение |
| Тип | Infra |
| Время | 15–30 мин |
| Домен | README / навигация prompt-системы |

Пример запроса:
«Используя promt-readme-sync.md, проверь актуальность индекс-таблицы
в README.md: все файлы должны присутствовать, версии актуальны,
удалённые файлы убраны из таблицы.»

Ожидаемый результат:
- Индекс-таблица README актуальна: ровно N строк = N .md файлов
- Версии в таблице совпадают с заголовками файлов
- Нет строк для несуществующих файлов
- Нет .md файлов без строки в таблице
```

**`## Когда использовать`:**
- После создания нового промпта (проверить, что строка добавлена)
- После удаления промпта (проверить, что строка убрана)
- После обновления версии промпта (синхронизировать версию в таблице)
- Периодически (раз в неделю) для проверки актуальности реестра

**Шаги workflow (4 шага):**

**Шаг 0: Discovery**
1. Получить список файлов: `ls docs/ai-agent-prompts/*.md`
2. Получить список файлов в `meta-promptness/`: `ls docs/ai-agent-prompts/meta-promptness/*.md`
3. Прочитать индекс-таблицу из README.md (раздел `## Реестр промптов`)
4. Построить diff: какие файлы есть в папке но нет в таблице, и наоборот

**Шаг 1: Context7 (по необходимости)**
Если нужна реструктуризация README — запросить best practices по документации.

**Шаг 2: Синхронизация индекс-таблицы**
1. Для каждого .md файла без строки в таблице → добавить строку
2. Для каждой строки без файла → убрать строку
3. Для каждого файла с несовпадающей версией → обновить версию в таблице
4. Порядок строк: по типу (Meta → ADR → Code → Infra), внутри типа — по алфавиту

**Шаг 3: Верификация**
```bash
# Количество .md файлов (кроме README и versioning-policy)
ls docs/ai-agent-prompts/*.md | wc -l
ls docs/ai-agent-prompts/meta-promptness/*.md | wc -l

# Проверить отсутствие ADR-XXX в README
grep -n "ADR-[0-9]\{3\}" docs/ai-agent-prompts/README.md | head -5
# Должно быть пусто
```

**ADR Topic Registry (релевантные):**
- `prompt-system-improvement-strategy` (ADR-022)
- `documentation-generation` (ADR-011)

**Anti-patterns:**
1. Добавление подробных описаний в README вместо в файл промпта
2. Создание 6+ секций для каждого промпта в README (устаревший подход)
3. Обновление только версии, но не содержимого таблицы

**Связанные промпты:** → `promt-versioning-policy.md` (после), → `promt-sync-optimization.md`

---

## Шаг 5: Валидация всех трёх промптов

Для каждого из трёх сгенерированных промптов прогнать quality gates:

| Gate | Проверка |
|------|----------|
| A | Канонический скелет: Mission, Контракт, Project Context, Шаги, Чеклист, Связанные |
| B | Source of truth совместимость |
| C | Dual-status (N/A для Meta/Infra типов) |
| D | Topic slug-first: нет ADR-XXX |
| E | Anti-legacy: нет ссылок на `k8s/` как active source |
| F | Read-only: нет модификаций `docs/official_document/` |
| G | Context7: шаг присутствует в workflow |
| H | Нет дублирования с существующими промптами |
| **I** | **Самодокументация: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений` присутствуют** |
| **J** | **Только индекс-строка в README** |

---

## Шаг 6: Регистрация в README

Добавить три строки в индекс-таблицу `docs/ai-agent-prompts/README.md`:

```markdown
| [`promt-agent-init.md`](promt-agent-init.md) | Meta | 1.0 | Обязательная инициализация AI-агента перед работой с CodeShift |
| [`promt-project-rules-sync.md`](promt-project-rules-sync.md) | Infra | 1.0 | Аудит и исправление docs/rules/project-rules.md |
| [`promt-readme-sync.md`](promt-readme-sync.md) | Infra | 1.0 | Обслуживание индекс-таблицы README.md (реестр промптов) |
```

---

## Чеклист генерации

**Pre-generation:**
- [ ] Версия фабрики `meta-promt-prompt-generation.md` ≥ 3.0
- [ ] Три старых файла удалены или не существуют
- [ ] Context7 запросы выполнены для всех трёх доменов

**During generation:**
- [ ] `promt-agent-init.md` содержит 6-шаговый workflow инициализации
- [ ] `promt-project-rules-sync.md` содержит шаги для AI Sync Rules + Workflows + slugs
- [ ] `promt-readme-sync.md` обслуживает только индекс-таблицу (не 6 секций)
- [ ] Все три файла имеют `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`

**Post-generation:**
- [ ] Quality gates A–J пройдены для каждого файла
- [ ] Три строки добавлены в README индекс-таблицу
- [ ] Никакого другого содержимого не добавлено в README

---

## Anti-patterns

1. **Разбросанная документация** — не добавлять описания в README; всё в файле промпта
2. **6-секционный README** — устаревший подход, не воспроизводить
3. **Старая фабрика** — запускать только с фабрикой v3.0+
4. **Смешение scope** — `promt-readme-sync.md` синхронизирует только индекс, не весь README

---

## Связанные промпты

| Промпт | Когда использовать |
|--------|-------------------|
| `meta-promt-prompt-generation.md` v3.0+ | Фабрика для создания любых других промптов |
| `promt-sync-optimization.md` | После генерации — аудит синхронизации системы |
| `promt-quality-test.md` | QA-проверка выходов сгенерированных промптов |
| `promt-versioning-policy.md` | Политика версионирования при обновлении промптов |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.0 | 2026-03-06 | Создан для воссоздания 3 промптов по новой самодокументирующейся структуре фабрики v3.0 |

---

**Prompt Version:** 1.0
**Maintainer:** @perovskikh
**Date:** 2026-03-06
