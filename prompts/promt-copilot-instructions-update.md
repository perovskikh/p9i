# AI Agent Prompt: Синхронизация copilot-instructions.md и project-rules.md с ADR и архитектурными инвариантами

**Version:** 2.1
**Date:** 2026-03-06
**Purpose:** Системное обновление инструкций AI-агента: ADR Topic Registry, архитектурные инварианты, стек, команды. Синхронизация `.github/copilot-instructions.md` и раздела в `docs/rules/project-rules.md`.

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Operational |
| **Время выполнения** | 30–60 мин |
| **Домен** | Copilot policy — синхронизация AI-инструкций |

**Пример запроса:**

> «Используя `promt-copilot-instructions-update.md`, синхронизируй
> `.github/copilot-instructions.md` и `docs/rules/project-rules.md`
> с текущими ADR topic slugs и инвариантами проекта.»

**Ожидаемый результат:**
- `.github/copilot-instructions.md` содержит актуальный ADR Topic Registry
- `docs/rules/project-rules.md` содержит раздел «AI Instructions Sync Rules»
- Topic slug-first соблюдён во всех документах
- Нет устаревших ADR-XXX номеров в тексте

---

## Когда использовать

- После добавления или переименования ADR (обновить topic registry)
- После изменения архитектурных инвариантов (стек, команды, паттерны)
- При плановой синхронизации (раз в спринт или после массовых изменений)
- Вместе с `promt-project-rules-sync.md` (они синхронизируют разные разделы)

> **Связка:** `promt-copilot-instructions-update.md` (ADR registry + инварианты)
> + `promt-project-rules-sync.md` (topic slugs + рабочие процессы).

---

## Mission Statement

Ты — AI-агент, отвечающий за актуальность и точность **двух файлов** в проекте CodeShift:
- `.github/copilot-instructions.md` — основные инструкции для AI-агентов
- `docs/rules/project-rules.md` — раздел о правилах синхронизации copilot-инструкций

Ты обновляешь эти файлы при появлении нового ADR, изменении стека, добавлении инвариантов или ключевых команд.
Каждое изменение строго прослеживаемо: ты указываешь триггер, раздел, до/после.

Этот промпт **НЕ** выполняет разработку фич, не создаёт ADR и не изменяет код — только файл инструкций и раздел в project-rules.

---

## Назначение

Обеспечить синхронизацию `.github/copilot-instructions.md` и раздела в `docs/rules/project-rules.md` с текущим состоянием проекта:
- **ADR Topic Registry** — таблица критичных ADR с topic slug + ключевым принципом
- **Architecture** — инфраструктурные инварианты (Ingress, K8s, Storage, SSL, GitOps)
- **Telegram Bot** — конфиг, DB, платежи, K8s, jobs
- **Key Commands** — `make`-цели и CLI
- **Conventions** — bash, YAML, Python, Make правила
- **Project Rules** — синхронизация раздела в `docs/rules/project-rules.md`, где фиксируются правила для copilot-инструкций (какие ADR-slug обязательны, какие инварианты должны быть отражены)

---

## Контракт синхронизации системы

> **Source of truth:** `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`
> При конфликте формулировок — приоритет у source of truth.

**Обязательные инварианты:**
- ADR идентифицируются только по **topic slug** (номера нестабильны, меняются при consolidation)
- `docs/official_document/` — READ-ONLY, никогда не изменять
- `.roo/` — READ-ONLY
- Anti-legacy: не создавать `PHASE_*.md`, `*_REPORT.md`, `*_SUMMARY.md`, директории `reports/`, `plans/`
- Deployment contour единственный: `Helm + config/manifests`; `k8s/` — legacy, фазируется out
- `$KUBECTL_CMD` из `scripts/helpers/k8s-exec.sh` — НИКОГДА не хардкодить `k3s kubectl`
- Canonical DB: `scripts/utils/init-saas-database.sql` (без Alembic)
- Dual-status ADR: `## Статус решения` + `## Прогресс реализации` + `## Чеклист реализации`
- Проверка фактического прогресса ADR: `./scripts/verify-adr-checklist.sh --topic <slug>`

---

## Project Context

### О проекте

**CodeShift** — multi-tenant SaaS платформа, развёртывающая VS Code (code-server) через Telegram Bot + YooKassa на Kubernetes.

**Стек:** Kubernetes (k3s/microk8s), Helm, Traefik, cert-manager, Python, aiogram 3.x, FastAPI, PostgreSQL, Redis, Longhorn/local-path, ArgoCD.

### ADR Topic Registry (релевантные для этого промпта)

> **КРИТИЧНО:** ADR идентифицируются по **topic slug**.
> Поиск: `find docs/explanation/adr -name "ADR-*-{slug}*.md" | head -1`

| Topic Slug | Связь с copilot-instructions.md |
|------------|----------------------------------|
| `path-based-routing` | Architecture → Ingress инвариант |
| `k8s-provider-abstraction` | Architecture → `$KUBECTL_CMD` инвариант |
| `storage-provider-selection` | Architecture → Storage инвариант |
| `telegram-bot-saas-platform` | Telegram Bot → pydantic-settings, PLAN_SPECS |
| `documentation-generation` | Conventions → reference docs AUTO-GENERATED |
| `helm-chart-structure-optimization` | Key Files → templates count |

---

## Входы

| Вход | Описание | Обязательность |
|------|----------|----------------|
| Триггер изменения | Новый ADR, изменение стека, новая команда, новый инвариант | Обязательно |
| `.github/copilot-instructions.md` | Текущее состояние файла | Обязательно |
| `docs/rules/project-rules.md` | Текущее состояние файла правил | Обязательно |
| ADR файл (если триггер = ADR) | `docs/explanation/adr/ADR-*-{slug}*.md` | При ADR-триггере |
| `docs/explanation/adr/index.md` | Список активных ADR | При обновлении Registry |
| `makefiles/` и `Makefile` | Актуальные make-цели | При обновлении команд |
| `telegram-bot/app/config.py` | Актуальные поля Settings | При обновлении Config |

---

## Выходы

| Выход | Описание |
|-------|---------|
| `.github/copilot-instructions.md` (обновлённый) | Файл синхронизирован с текущим состоянием проекта |
| `docs/rules/project-rules.md` (обновлённый) | Раздел о copilot-инструкциях синхронизирован |
| Commit message | Формат: `docs: update copilot-instructions — {причина}` |
| Трассировка изменений | Раздел → что изменено → почему (в этом ответе агента) |

---

## Ограничения / инварианты

1. **Два файла — два изменяемых артефакта.** Этот промпт работает с `.github/copilot-instructions.md` и `docs/rules/project-rules.md`.
2. **Никаких новых разделов без обоснования.** Структура файла стабильна; добавлять разделы только если появился принципиально новый домен.
3. **ADR Topic Registry** — только критичные ADR (влияют на каждый PR). Не добавлять полный список всех 21+ ADR.
4. **Ключевые принципы в таблице** — одна фраза (`Single domain, NO subdomains`). Не копировать ADR целиком.
5. **Key Commands** — только `make`-цели с широким применением. Не дублировать `make help`.
6. **Legal**: 422-ФЗ (НПД) — упоминание CPU/RAM/server запрещено в публичных текстах.
7. **Никогда не добавлять** раздел "History" или "Changelog" в `copilot-instructions.md`.
8. **Изменения в `project-rules.md` ограничены ТОЛЬКО разделом `## 📋 Copilot Instructions Sync Rules`**; остальные 22 раздела не трогать.

---

## Workflow шаги

### Шаг 0: Определить триггер и scope изменения

Ответь на вопросы:
- Что изменилось в проекте? (новый ADR / изменение стека / новая команда / новый инвариант)
- Какой раздел `copilot-instructions.md` затронут?
- Это добавление, изменение или удаление?

**Пример формата входа:**
> «Добавился новый ADR по теме `helm-secrets-management` с принципом "Используй Sealed Secrets". Нужно добавить в ADR Topic Registry.»

---

### Шаг 1: Context7 — проверка best practices (обязательно при изменении стека)

> Используй Context7 MCP: `resolve-library-id` → `get-library-docs`

| Библиотека | Context7 ID | Когда нужен |
|---|---|---|
| Helm | `/websites/helm_sh` | Если меняется K8s/Helm стек |
| Kubernetes | `/kubernetes/website` | Если меняется K8s topology |
| aiogram 3.x | `/websites/aiogram_dev_en_v3_22_0` | Если меняется bot framework |
| FastAPI | `/fastapi/fastapi` | Если меняется webhook стек |
| Traefik | `/websites/traefik_io` | Если меняется Ingress |

Если триггер — только добавление ADR в Registry, Context7 **опционален**.

---

### Шаг 2: Прочитать текущий файл

```bash
cat .github/copilot-instructions.md
```

Зафиксируй:
- Текущее содержимое затронутого раздела (до изменения)
- Точный синтаксис таблицы / bullet / code block в нужном разделе

---

### Шаг 3: Проверить источник изменения

**При ADR-триггере:**
```bash
# Найти ADR по topic slug
find docs/explanation/adr -name "ADR-*-{slug}*.md" | head -1

# Прочитать ключевые разделы
grep -A5 "## Статус решения\|## Принятое решение\|## Ключевые принципы" docs/explanation/adr/ADR-*-{slug}*.md
```

**При изменении стека / команд:**
```bash
# Актуальные make-цели
make help 2>/dev/null | grep -E "^\s+[a-z]" | head -30

# Актуальные поля config
grep "^    " telegram-bot/app/config.py | head -50
```

---

### Шаг 4: Применить изменение в copilot-instructions.md

Используй правило **хирургического редактирования**: меняй только минимально необходимое.

#### 4.1. Добавить ADR в Topic Registry

Шаблон строки:
```markdown
| Path-Based Routing | `ADR-*-path-based-routing*.md` | Single domain, NO subdomains |
```
Формат: `| {Название} | \`ADR-*-{slug}*.md\` | {ключевой принцип} |`

Добавляй **только критичные** ADR — те, которые влияют на ежедневные PR-решения.

#### 4.2. Обновить Architecture инвариант

Найди релевантный bullet/subsection. Замени **только изменившуюся часть**. Сохрани стиль (bold, backticks, link-формат).

#### 4.3. Обновить Key Commands

Добавь/измени строку в code block формата:
```
make <target>          # <описание>
```
Максимум 1 строка изменения на 1 команду.

#### 4.4. Обновить Key Files таблицу

```markdown
| Purpose | Path |
```
Добавь строку только если файл действительно критичен для навигации нового агента.

---

### Шаг 4.5: Обновить раздел в `project-rules.md`

1. Прочитать `docs/rules/project-rules.md`
2. Найти раздел `## 📋 Copilot Instructions Sync Rules` (или создать его, если отсутствует — после раздела «21. Версионирование», перед «22. Матрица тестирования окружений»)
3. Обновить/добавить абзац с правилами синхронизации copilot-instructions

**Пример содержимого раздела для `project-rules.md`:**

```markdown
## 📋 Copilot Instructions Sync Rules

> Правила синхронизации `.github/copilot-instructions.md` с архитектурными решениями.

- **ADR Topic Registry**: `copilot-instructions.md` ОБЯЗАН содержать таблицу критичных ADR topic slug
  (≤10 строк). При добавлении/удалении/переименовании ADR — обновить таблицу.
- **Архитектурные инварианты**: все инварианты из раздела «Архитектурные принципы» project-rules
  ДОЛЖНЫ быть отражены в copilot-instructions (Ingress, K8s abstraction, Storage, Deployment contour).
- **Триггер обновления**: любое изменение ADR, стека или инвариантов → запустить
  `promt-copilot-instructions-update.md`.
- **Формат commit**: `docs: update copilot-instructions — {причина}`.
- **Запрещено**: добавлять полный список всех ADR, хардкодить версии, создавать History/Changelog разделы.
```

---

### Шаг 5: Верификация применённого изменения

```bash
# Проверить синтаксис Markdown (таблицы не порваны)
grep -c "^|" .github/copilot-instructions.md

# Проверить slug консистентность (ADR Topic Registry)
grep "ADR-\*-" .github/copilot-instructions.md | while read line; do
  slug=$(echo "$line" | grep -oP 'ADR-\*-\K[^*]+')
  count=$(find docs/explanation/adr -name "ADR-*-${slug}*.md" 2>/dev/null | wc -l)
  echo "slug=$slug files=$count"
done
```

Проверь ручным взором:
- [ ] Таблица ADR Topic Registry выровнена (`|---|---|---|`)
- [ ] Новый принцип — одна фраза, без точки в конце
- [ ] Нет дублирующихся строк в таблицах
- [ ] Ссылки `docs/explanation/adr/` ведут на реальные файлы

---

### Шаг 6: Проверить смежные промпты на устаревание

После изменения copilot-instructions.md проверь, не нужно ли обновить frozen snapshot:

```bash
# Если менялся стек или инварианты — проверить drift в промптах
make docs-prompt-guard 2>/dev/null || cat scripts/check-prompt-drift.sh
```

Если в `promt-sync-optimization.md` есть frozen snapshot с устаревшими данными — вызови `promt-sync-optimization.md`.

---

### Шаг 7: Задокументировать изменение

Сформируй трассировку изменений в ответе агента:
```
ИЗМЕНЕНИЕ:
  Файл: .github/copilot-instructions.md
  Раздел: ADR Topic Registry
  Триггер: Утверждён ADR-XXX-{slug} (Принятый статус)
  До: [строк не было / было ...]
  После: | {slug} | ... | ... |
  Инвариант: ADR идентифицируется по topic slug

ИЗМЕНЕНИЕ:
  Файл: docs/rules/project-rules.md
  Раздел: 📋 Copilot Instructions Sync Rules
  Триггер: Синхронизация с copilot-instructions.md
  До: [раздела не было / было ...]
  После: [обновлённое содержимое раздела]
  Инвариант: Остальные 22 раздела не затронуты
```

---

## Проверки / acceptance criteria

| Критерий | Проверка |
|----------|---------|
| Изменён только релевантный раздел | `git diff .github/copilot-instructions.md` — delta минимальна |
| ADR slug корректен | `find docs/explanation/adr -name "ADR-*-{slug}*.md"` возвращает ≥1 файл |
| Таблицы не сломаны | Все строки начинаются с `|`, заголовок разделён `|---|` |
| Стиль сохранён | Bold/backtick/link форматирование соответствует соседним строкам |
| Дублей нет | Каждый topic slug в Registry встречается ровно 1 раз |
| Инварианты не нарушены | Нет упоминаний `k3s kubectl` напрямую, нет CPU/RAM данных |
| Anti-legacy | Не создано новых `.md` файлов (`PHASE_*`, `*_REPORT`, `reports/`) |
| Commit message | Формат `docs: update copilot-instructions — {причина}` |
| Prompt Guard | `make docs-prompt-guard` проходит без ошибок (если менялось) |
| `project-rules.md` раздел существует | `grep "Copilot Instructions Sync Rules" docs/rules/project-rules.md` |
| `project-rules.md` не сломан | Остальные 22 раздела не изменены |

---

## Чеклист обновления copilot-instructions.md

### Pre (перед началом)
- [ ] Триггер изменения чётко сформулирован
- [ ] Определён раздел файла, который будет затронут
- [ ] ADR файл прочитан (если триггер — ADR)
- [ ] `.github/copilot-instructions.md` прочитан полностью
- [ ] `docs/rules/project-rules.md` прочитан полностью

### Изменение
- [ ] Изменение хирургическое — только необходимый минимум
- [ ] ADR topic slug проверен через `find docs/explanation/adr -name "ADR-*-{slug}*.md"`
- [ ] Ключевой принцип — одна фраза, без точки
- [ ] Форматирование таблицы/bullet соответствует стилю соседних строк
- [ ] Нет дублей в таблицах
- [ ] Раздел в `project-rules.md` обновлён/создан
- [ ] Остальные разделы `project-rules.md` не затронуты
- [ ] Содержимое раздела согласовано с copilot-instructions.md

### Валидация
- [ ] `grep -c "^|" .github/copilot-instructions.md` — число строк таблиц не убыло
- [ ] Slug-консистентность проверена (все слаги ведут на реальные файлы)
- [ ] Инварианты: нет `k3s kubectl` напрямую, нет `k8s/` как активного contour
- [ ] `make docs-prompt-guard` прошёл (если был изменён frozen snapshot)

### Final
- [ ] Трассировка изменений задокументирована (раздел → до → после → причина)
- [ ] Commit message в формате `docs: update copilot-instructions — {причина}`
- [ ] Проверено: `docs/official_document/` не тронут
- [ ] Проверено: `.roo/` не тронут

---

## Anti-patterns

| Anti-pattern | Почему опасно | Правильный подход |
|---|---|---|
| Добавить весь список ADR в Topic Registry | Registry перегружается, теряет ценность как «критичные» | Только ADR, влияющие на ежедневные решения (≤10 строк) |
| Хардкодить версии (`aiogram==3.0.0`) | Устаревает, создаёт ложный источник истины | Ссылаться на `telegram-bot/requirements.txt` |
| Переписывать раздел целиком | Высокий риск потери нюансов, невозможно review | Хирургическое изменение: только дельта |
| Создать `COPILOT-INSTRUCTIONS-HISTORY.md` | Anti-legacy нарушение | История видна через `git log .github/copilot-instructions.md` |
| Добавить CPU/RAM/server данные | Нарушение 422-ФЗ (НПД) | Упоминать только архитектурные компоненты |
| Использовать номер ADR вместо slug | Номера меняются при consolidation | Всегда `ADR-*-{slug}*.md` pattern |
| Переписать весь `project-rules.md` | Потеря остальных 22 разделов | Изменять ТОЛЬКО раздел Copilot Instructions Sync Rules |

---

## Ресурсы

| Ресурс | Путь | Назначение |
|---|---|---|
| **Copilot instructions** | `.github/copilot-instructions.md` | Main config file |
| **Project rules** | `docs/rules/project-rules.md` | Sync section |
| **ADR-файлы** | `docs/explanation/adr/ADR-*.md` | Registry definitions |
| **Скрипт верификации** | `scripts/verify-all-adr.sh` | Validation |
| **Официальная документация** | `docs/official_document/` | **READ-ONLY** эталон |
| **Meta-prompt** | `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md` | Source of truth |

---

## Связи с другими промптами

| Промпт | Связь |
|--------|-------|
| `promt-verification.md` | Верификация ADR ↔ код после обновления Registry |
| `promt-index-update.md` | Обновить `docs/explanation/adr/index.md` при новом ADR |
| `promt-consolidation.md` | При объединении ADR — обновить slug в Registry |
| `promt-sync-optimization.md` | Если frozen snapshot устарел после изменений |
| `promt-feature-add.md` | Обновление copilot-instructions — часть workflow добавления фичи |

---

## Связанные промпты

| Промпт | Когда использовать |
|--------|-------------------|
| `promt-verification.md` | После добавления нового ADR в Registry — верифицировать реализацию |
| `promt-index-update.md` | При добавлении/архивации ADR — синхронизировать index.md |
| `promt-consolidation.md` | При обнаружении дублирующихся ADR-slug в Registry |
| `promt-sync-optimization.md` | Если изменения затронули frozen snapshot промптов |
| `promt-feature-add.md` | Обновление copilot-instructions входит в workflow добавления фичи |
| `promt-system-evolution.md` | При системных изменениях, затрагивающих project-rules |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 2.1 | 2026-03-06 | Добавлены секции Gate I: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`. |
| 2.0 | 2026-02-26 | Расширен scope: синхронизация `.github/copilot-instructions.md` + раздел `Copilot Instructions Sync Rules` в `docs/rules/project-rules.md`. |
| 1.0 | 2026-02-24 | Первая версия: обновление ADR Topic Registry в copilot-instructions. |

---

**Prompt Version:** 2.1
**Maintainer:** @perovskikh
**Date:** 2026-03-06
