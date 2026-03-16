# AI Agent Prompt: Автоматизированный экспорт Sync Report для CodeShift

**Version:** 1.2
**Date:** 2026-02-24
**Purpose:** Ввести единый сценарий генерации и экспорта Sync Report в Markdown/JSON с хранением в `artifacts/prompt-sync/` и ротацией артефактов

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Operational |
| **Время выполнения** | 15–30 мин |
| **Домен** | Reporting — экспорт Sync Report |

**Пример запроса:**

> «Используя `promt-sync-report-export.md`, сформируй machine-readable
> Sync Report (`.md` + `.json`) в `artifacts/prompt-sync/`.»

**Ожидаемый результат:**
- `artifacts/prompt-sync/SYNC-REPORT-YYYYMMDD.md` создан
- `artifacts/prompt-sync/SYNC-REPORT-YYYYMMDD.json` создан
- Ротация артефактов: хранить последние N отчётов

---

## Когда использовать

- После выполнения `promt-sync-optimization.md` — для сохранения отчёта
- При CI/CD интеграции — автоматический экспорт после каждого sync-аудита
- Для передачи Sync Report в другой инструмент (Jira, Notion, GitHub Issues)
- При архивировании исторических данных о состоянии prompt-системы

---

## Mission Statement

Ты — AI-агент стандартизации отчётности prompt-системы CodeShift.
Твоя задача — перевести ручной Sync Report в воспроизводимый и машиночитаемый процесс:
определить единый шаблон отчёта, реализовать экспорт одной командой,
и обеспечить накопление/агрегацию отчётов по датам без legacy-дубликатов.

Этот промпт не заменяет `promt-sync-optimization.md` (аудит синхронизации).
Он добавляет слой **экспорта результатов аудита** в стабильный формат Markdown/JSON
для последующего анализа и CI-артефактов.

---

## Контракт синхронизации системы

> **Source of truth:** `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`
> При конфликте формулировок приоритет у source of truth.

**Обязательные инварианты:**
- ADR идентифицируются по **topic slug**
- Для ADR-материалов учитывать dual-status: `## Статус решения` + `## Прогресс реализации` + `## Чеклист реализации`
- `docs/official_document/` — строго READ-ONLY
- Anti-legacy: не создавать `PHASE_*.md`, `*_SUMMARY.md`, `*_REPORT.md`, `reports/`, `plans/`
- Update in-place: без `*-v2.md`, `*-new.md`, `*-final.md`
- Артефакты отчётов сохраняются только в `artifacts/` (не в корне репозитория)
- Ручной формат отчёта без стандартизированного контракта не допускается
- Для фактического ADR-прогресса использовать `./scripts/verify-adr-checklist.sh --summary`

---

## Назначение

Этот промпт стандартизирует Sync Report Export Workflow:
- единый шаблон отчёта (`markdown` + `json`),
- единый entrypoint скрипта (`scripts/generate-prompt-sync-report.sh`),
- единая директория артефактов (`artifacts/prompt-sync/`),
- минимальная ретеншн-политика и базовая агрегация по датам.

## Входы

- Результаты guard-проверок prompt-системы:
  - `scripts/check-prompt-drift.sh`
  - `scripts/check-prompt-versions.sh`
  - `scripts/check-prompt-legacy-refs.sh`
- Версии source/meta/operational prompt-файлов
- Timestamp запуска и контекст ветки/коммита (если доступно)

## Выходы

- `artifacts/prompt-sync/prompt-sync-report-YYYYMMDD-HHMMSS.md`
- `artifacts/prompt-sync/prompt-sync-report-YYYYMMDD-HHMMSS.json`
- `artifacts/prompt-sync/prompt-sync-latest.md`
- `artifacts/prompt-sync/prompt-sync-latest.json`

## Ограничения / инварианты

- Скрипт экспорта должен быть идемпотентным и безопасным к повторному запуску
- Логи и отчёты не писать в корень репозитория
- Любые изменения — только in-place
- Не менять read-only зоны (`docs/official_document/`, `.roo/`)
- Не смешивать экспорт отчёта с логикой модификации prompt-файлов

## Workflow шаги

1. Discovery: собрать входные данные sync-аудита
2. Context7 Gate: подтвердить best practices для report schemas и CLI export workflows
3. Report Template Build: сформировать единый контракт Markdown/JSON
4. Script Implementation: реализовать/обновить `scripts/generate-prompt-sync-report.sh`
5. Artifact Export: сохранить timestamped + latest файлы в `artifacts/prompt-sync/`
6. Retention: применить ротацию старых артефактов
7. Validation: проверить формат, ссылки и воспроизводимость

## Проверки / acceptance criteria

- Одна команда генерирует оба формата отчёта (`.md` и `.json`)
- Структура отчёта стабильна между запусками
- `latest`-файлы обновляются атомарно и ссылаются на последний отчёт
- Ротация удаляет устаревшие артефакты по retention-политике
- Guard-проверки остаются совместимыми и не ломаются

## Связи с другими промптами

- До: `promt-sync-optimization.md` (формирует фактические sync findings)
- После: `promt-quality-test.md` (проверка качества экспортируемого отчёта),
  `promt-versioning-policy.md` (если изменён output contract)

---

## Project Context

### О проекте (prompt-sync export domain)

CodeShift использует guard-пайплайн для контроля prompt-системы, но результат часто
фиксируется вручную в ответе агента. Для CI и исторического анализа нужен унифицированный
машиночитаемый экспорт, который можно агрегировать по датам и сравнивать между прогонами.

### ADR Topic Registry (релевантные topics)

| Topic Slug | Роль в экспортном workflow |
|---|---|
| `documentation-generation` | Контракт форматов и регламент обновления документации |
| `telegram-bot-saas-platform` | Общие SaaS-ограничения и production-практики |
| `k8s-provider-abstraction` | Унифицированный подход к исполняемым скриптам в проекте |

---

## Шаг 0: Discovery и входной контракт

### 0.1. Зафиксировать входные команды

Минимальный входной набор:

```bash
./scripts/check-prompt-drift.sh
./scripts/check-prompt-versions.sh
./scripts/check-prompt-legacy-refs.sh
./scripts/verify-adr-checklist.sh --summary
```

### 0.2. Нормализовать входные статусы

Для каждой проверки сформировать нормализованную запись:
- `check_id`
- `status` (`PASS` / `FAIL`)
- `summary`
- `details` (опционально)

---

## Шаг 1: Context7 исследование (ОБЯЗАТЕЛЬНО)

Собери best practices для:
- machine-readable audit reports (Markdown + JSON dual-output)
- CLI script design (idempotent export commands)
- artifact retention/rotation policy

Применяй только практики, совместимые с anti-legacy и update in-place правилами CodeShift.

---

## Шаг 2: Шаблон Sync Report

### 2.1. Markdown-структура (обязательная)

```markdown
# Prompt Sync Report

## Metadata
- Generated at: <ISO8601>
- Report ID: <sync-YYYYMMDD-HHMMSS>
- Source of truth version: <version>

## Summary
- Total checks: N
- Passed: N
- Failed: N
- Overall status: PASS|FAIL

## Checks
| Check | Status | Summary |
|---|---|---|

## Drift Details
...

## Legacy Gate Details
...

## Version Registry Details
...

## Actions
- [ ] ...
```

### 2.2. JSON-структура (обязательная)

```json
{
  "report_id": "sync-YYYYMMDD-HHMMSS",
  "generated_at": "ISO8601",
  "overall_status": "PASS",
  "summary": {
    "total_checks": 3,
    "passed": 3,
    "failed": 0
  },
  "checks": [
    {
      "check_id": "prompt-drift",
      "status": "PASS",
      "summary": "NO DRIFT"
    }
  ],
  "actions": []
}
```

---

## Шаг 3: Контракт скрипта экспорта

### 3.1. Целевой артефакт

- Скрипт: `scripts/generate-prompt-sync-report.sh`
- Директория: `artifacts/prompt-sync/`

### 3.2. CLI-поведение (минимум)

```bash
./scripts/generate-prompt-sync-report.sh
./scripts/generate-prompt-sync-report.sh --output-dir artifacts/prompt-sync
./scripts/generate-prompt-sync-report.sh --retention-days 30
```

### 3.3. Обязательные требования

- `set -euo pipefail`
- Создание директории артефактов через `mkdir -p`
- Timestamped имена + обновление `latest` файлов
- Корректный exit code: `0` при success, `!=0` при критической ошибке
- Безопасная обработка отсутствующих входных данных (понятное сообщение + fallback)

---

## Шаг 4: Retention и агрегация

### 4.1. Retention policy

Минимальная политика:
- хранить отчёты за последние `N` дней (по умолчанию `30`)
- удалять файлы старше retention окна

### 4.2. Агрегация по датам

Поддерживать лёгкую агрегацию:
- сортировка отчётов по дате в имени файла
- `latest`-ссылки/копии для быстрого доступа
- возможность выборки `grep`/`jq` без дополнительного преобразования

---

## Шаг 5: Валидация

```bash
make docs-prompt-guard
./scripts/generate-prompt-sync-report.sh
ls -1 artifacts/prompt-sync/
```

Проверь:
- `.md` и `.json` созданы одновременно
- `latest` обновлён
- JSON валиден и пригоден для `jq`

---

## Чеклист Prompt Sync Report Export

### Pre-flight
- [ ] Определены входные проверки (`drift`, `legacy`, `versions`)
- [ ] Подтверждён единый output contract (md/json)
- [ ] Выбрана retention-политика

### Implementation
- [ ] Есть скрипт `scripts/generate-prompt-sync-report.sh`
- [ ] Скрипт создаёт `artifacts/prompt-sync/` при отсутствии
- [ ] Генерируются timestamped `.md` и `.json`
- [ ] Обновляются `prompt-sync-latest.md` и `prompt-sync-latest.json`

### Validation
- [ ] `make docs-prompt-guard` проходит
- [ ] JSON отчёт валиден
- [ ] Формат Markdown стабилен и содержит обязательные секции

### Final
- [ ] README реестр prompt-системы обновлён при необходимости
- [ ] Нет нарушений anti-legacy
- [ ] Нет артефактов вне `artifacts/`

---

## Anti-patterns

| Anti-pattern | Почему плохо | Правильный подход |
|---|---|---|
| Писать Sync Report вручную только в ответе агента | Нет воспроизводимости, нет истории | Генерировать стандартизированный md/json артефакт |
| Хранить отчёты в `reports/` или в корне | Нарушение anti-legacy и правил чистоты | Использовать только `artifacts/prompt-sync/` |
| Генерировать только Markdown без JSON | Сложная машинная обработка | Всегда экспортировать оба формата |
| Менять формат отчёта без versioning-проверки | Ломается downstream-обработка | Согласовывать через `promt-versioning-policy.md` |

---

## Ресурсы

| Ресурс | Путь | Назначение |
|---|---|---|
| **Sync artifacts** | `artifacts/prompt-sync/` | Repository for reports |
| **Версионирование** | `docs/ai-agent-prompts/promt-versioning-policy.md` | Version bump rules |
| **Качество** | `docs/ai-agent-prompts/promt-quality-test.md` | Оценка отчётов |
| **Workflow** | `docs/ai-agent-prompts/promt-workflow-orchestration.md` | Внедрение экспорта |
| **Правила проекта** | `.github/copilot-instructions.md` | Anti-legacy rules |
| **Официальная документация** | `docs/official_document/` | **READ-ONLY** эталон |
| **Meta-prompt** | `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md` | Source of truth |

---

## Связанные промпты

| Промпт | Когда использовать |
|---|---|
| `promt-sync-optimization.md` | Получить актуальные sync findings перед экспортом |
| `promt-quality-test.md` | Проверить качество структуры экспортного отчёта |
| `promt-versioning-policy.md` | Зафиксировать корректный version bump при изменении output contract |
| `promt-workflow-orchestration.md` | Встроить экспорт как шаг в governance workflow цепочку |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|----------|
| 1.2 | 2026-03-06 | Добавлены секции Gate I: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`. |
| 1.1 | 2026-02-24 | Dual format export (md + json), artifact rotation, CI integration. |
| 1.0 | 2026-02-23 | Первая версия: экспорт Sync Report в artifacts/. |

---

**Prompt Version:** 1.2
**Date:** 2026-03-06
**Maintainer:** @perovskikh
**Date:** 2026-02-24
