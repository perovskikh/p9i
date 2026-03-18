# AI Agent Prompt: Аудит и исправление project-rules.md для CodeShift

**Версия:** 1.1  **Дата:** 2026-03-06  **Тип:** Infra
**Purpose:** Аудит и исправление структурных, форматных и инвариантных ошибок в `docs/rules/project-rules.md` — topic slug compliance, раздел AI Instructions Sync Rules, раздел «Рабочие процессы».

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Infra |
| **Время выполнения** | 30–60 мин |
| **Домен** | Документация / project-rules.md |

**Пример запроса:**

> «Используя `promt-project-rules-sync.md`, выполни аудит и исправление
> `docs/rules/project-rules.md`: добавь раздел AI Instructions Sync Rules,
> восстанови раздел Рабочие процессы, замени ADR-XXX на topic slugs.»

**Ожидаемый результат:**
- `project-rules.md` обновлён с разделом `## AI Instructions Sync Rules`
- Все ADR-XXX заменены на canonical topic slugs
- Раздел «Рабочие процессы» восстановлен (если деградировал)
- Файл компактен: дублирующиеся формулировки удалены

---

## Когда использовать

- В `project-rules.md` обнаружены ADR-XXX номера (нарушение topic slug-first)
- Отсутствует или неполный раздел о правилах синхронизации AI-инструкций (Copilot + Claude)
- Раздел «Рабочие процессы» деградировал или исчез
- После обновления `copilot-instructions.md` или `CLAUDE.md` — нужна синхронизация
- После изменения инвариантов в ADR (topic slug изменился или добавился новый)
- Файл обрастает дублирующимися формулировками — нужна чистка

Этот промпт работает **только** с `docs/rules/project-rules.md`. Для синхронизации
`copilot-instructions.md` используй `promt-copilot-instructions-update.md`.

---

## Mission Statement

Ты — AI-агент, отвечающий за качество и актуальность `docs/rules/project-rules.md`.
Твоя задача — провести аудит файла по формальным критериям (topic slug-first, наличие
обязательных разделов, дублирование) и исправить найденные нарушения in-place.
Главная цель — чтобы файл был самодостаточным справочником стандартов разработки,
совместимым с AI-инструкциями CLAUDE.md и copilot-instructions.md.
Объём — столько, сколько нужно для точности и полноты, без воды.

---

## Контракт синхронизации системы

> **Source of truth:** `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`
> Этот промпт подчиняется source of truth. При конфликте — приоритет у meta-prompt.

**Обязательные инварианты:**
- ADR идентификация по **topic slug** (номера нестабильны)
- `docs/official_document/` — READ-ONLY
- Anti-legacy: не создавать `PHASE_*.md`, `*_REPORT.md`, `*_SUMMARY.md`
- Update in-place: не создавать `project-rules-v2.md`, `project-rules-new.md`
- Diátaxis: reference-документ — факты, правила, без туториалов

---


## Назначение

Аудит и исправление `docs/rules/project-rules.md`: замена ADR-XXX на topic slugs, добавление раздела AI Instructions Sync Rules, восстановление раздела «Рабочие процессы».

## Входы

- `docs/rules/project-rules.md` (текущее состояние)
- `.github/copilot-instructions.md` (ADR Topic Registry)
- Список активных ADR из `docs/explanation/adr/`

## Выходы

- Обновлённый `docs/rules/project-rules.md` с topic slugs и AI Sync Rules разделом
- Нет `ADR-XXX` номеров в тексте
- Раздел «Рабочие процессы» присутствует и актуален

## Ограничения / инварианты

См. `## Контракт синхронизации системы` выше. Topic slug-first — ключевой инвариант: номера ADR нестабильны и должны быть заменены на slugs.

## Workflow шаги

См. шаги `## Шаг 0`–`## Шаг 5` ниже: Input Validation → Context7 → AI Sync Rules → Рабочие процессы → Topic slugs → Верификация.

## Проверки / acceptance criteria

См. `## Чеклист синхронизации` ниже. Промпт завершён, когда: нет ADR-XXX в тексте, раздел AI Sync Rules присутствует, раздел «Рабочие процессы» восстановлен.

## Project Context

### О проекте

**CodeShift** — multi-tenant SaaS платформа, развёртывающая VS Code (code-server)
через Telegram Bot + YooKassa на Kubernetes.

**Стек:** Kubernetes (k3s/microk8s), Helm, Traefik, cert-manager, Python,
aiogram 3.x, FastAPI, PostgreSQL, Redis, Longhorn/local-path, ArgoCD.

### ADR Topic Registry (релевантные)

> **КРИТИЧНО:** ADR идентифицируются по **topic slug**.

| Topic Slug | Назначение |
|---|---|
| `documentation-generation` | Генерация и стандарты документации |
| `bash-formatting-standard` | Стандарты bash-скриптов |
| `prompt-system-improvement-strategy` | Стратегия prompt-системы |
| `infrastructure-consolidation-dry` | Консолидация инфраструктуры DRY |
| `telegram-bot-saas-platform` | Telegram Bot SaaS платформа |
| `k8s-provider-abstraction` | Абстракция K8s-провайдера |
| `path-based-routing` | Path-based routing (без subdomains) |

---

## Шаг 0: Input Validation

1. Прочитать `docs/rules/project-rules.md` полностью
2. Прочитать `docs/explanation/adr/index.md` — для маппинга slug → номер
3. Прочитать `.github/copilot-instructions.md` и `CLAUDE.md`
4. Построить таблицу аудита:

| Критерий | Статус | Детали |
|----------|--------|--------|
| ADR-XXX ссылки | ✅/❌ | количество нарушений |
| Раздел AI Instructions Sync Rules | ✅/❌ | присутствует/отсутствует |
| Раздел Рабочие процессы | ✅/❌ | полный/деградировал |
| Дублирующиеся формулировки | ✅/❌ | есть/нет |

5. Зафиксировать: «Аудит завершён. Найдено X нарушений. Приступаю к исправлению.»

---

## Шаг 1: Context7 исследование (ОБЯЗАТЕЛЬНО)

> Используй Context7 MCP: `resolve-library-id` → `get-library-docs`

| Библиотека | Context7 ID | Зачем |
|---|---|---|
| MkDocs Material | `/squidfunk/mkdocs-material` | Best practices структуры документов |

Запросить:
- Лучшие практики структурирования reference-документации (Diátaxis)
- Стандарты синхронизации технических инструкций AI-агентов

---

## Шаг 2: Раздел AI Instructions Sync Rules

Добавить или обновить раздел `## AI Instructions Sync Rules` в `project-rules.md`:

**Содержимое раздела:**
- Общее правило: все AI-инструкции синхронны с ADR topic slugs
- **GitHub Copilot:** файл `.github/copilot-instructions.md`, назначение,
  ключевые разделы (ADR Topic Registry, Architecture, Conventions), правила обновления
- **Claude (Claude Code):** файл `CLAUDE.md`, назначение,
  ключевые разделы (Architecture, Key Commands, Code Conventions), правила обновления
- **Workflow синхронизации (4 шага):**
  1. Изменился ADR → обновить topic slug в обоих файлах
  2. Изменился стек → обновить раздел Architecture в copilot-instructions
  3. Новые инварианты → добавить в оба файла и зафиксировать в ADR
  4. Проверка: `./scripts/check-topic-slug-first.sh .github/copilot-instructions.md`

---

## Шаг 3: Восстановление раздела «Рабочие процессы»

Если раздел отсутствует или деградировал — восстановить с подразделами:

- **Git Flow** — ветки (`feature/`, `fix/`, `docs/`), commit-формат, PR правила
- **Деплой и идемпотентность** — `kubectl apply` (не `create`), `--wait=false` паттерн
- **CI/CD Pipeline** — make-цели (`make test`, `make lint`, `make vet`), порядок запуска
- **Ссылки на how-to** — `docs/how-to/` для пошаговых руководств

---

## Шаг 4: Замена ADR-XXX → topic slugs

1. Найти все `ADR-[0-9]+` вхождения в файле:
   ```bash
   grep -n "ADR-[0-9]\{3\}" docs/rules/project-rules.md
   ```
2. Для каждого найденного номера — найти canonical topic slug в `docs/explanation/adr/index.md`
3. Заменить `ADR-XXX` на topic slug (формат: `` `topic-slug` ``)
4. Пути файлов ADR оставить без изменений

---

## Шаг 5: Верификация

```bash
# Проверить topic slug-first compliance
./scripts/check-topic-slug-first.sh docs/rules/project-rules.md

# Проверить навигацию MkDocs
make docs-check-mkdocs-nav

# Общая проверка prompt-системы
make docs-prompt-guard
```

---

## Чеклист синхронизации

**Pre:**
- [ ] `project-rules.md` прочитан полностью
- [ ] `index.md` прочитан — маппинг slug → номер готов
- [ ] `copilot-instructions.md` и `CLAUDE.md` прочитаны
- [ ] Таблица аудита построена

**During:**
- [ ] Context7 запрос выполнен
- [ ] Раздел AI Instructions Sync Rules добавлен/обновлён
- [ ] Раздел «Рабочие процессы» присутствует и полный
- [ ] Все ADR-XXX заменены на topic slugs
- [ ] Пути к файлам ADR не изменены
- [ ] Дублирующиеся формулировки удалены

**Post:**
- [ ] `check-topic-slug-first.sh` — 0 нарушений
- [ ] `make docs-prompt-guard` — PASS
- [ ] `make docs-check-mkdocs-nav` — PASS
- [ ] Файл изменён in-place (не создан дубль)

---

## Anti-patterns

1. **Создание нового файла** вместо редактирования in-place (`project-rules-v2.md`)
2. **Нарушение Diátaxis** — добавление туториалов в reference-документ
3. **Добавление ADR-XXX номеров** вместо topic slugs при правках
4. **Раздувание за счёт дублирования** — одно правило в трёх местах
5. **Изменение `docs/official_document/`** — READ-ONLY

---

## Связи с другими промптами

| Промпт | Когда использовать |
|--------|-------------------|
| `promt-copilot-instructions-update.md` | После — синхронизировать `copilot-instructions.md` |
| `promt-sync-optimization.md` | Аудит синхронизации всей prompt-системы |
| `promt-documentation-refactoring-standards-2026.md` | Если нужен глубокий Diátaxis аудит |
| `promt-agent-init.md` | До — инициализация агента |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.1 | 2026-03-06 | Убраны жёсткие ограничения на строки (≤280); критерий объёма заменён на «без дублирования, по необходимости»; таблица аудита и чеклист обновлены |
| 1.0 | 2026-03-06 | Создан по `meta-promt-sync-init-generator.md` v1.0 |

---

**Prompt Version:** 1.1
**Maintainer:** @perovskikh
**Date:** 2026-03-06
