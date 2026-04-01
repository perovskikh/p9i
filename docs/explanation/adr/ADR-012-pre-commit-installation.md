# ADR-012: Pre-commit Hook Installation Requirement

## Статус решения
**Accepted** | 2026-03-30

## Прогресс реализации
✅ Реализован

## Context

Репозиторий содержит `.pre-commit-config.yaml` с локальным хуком для валидации нумерации ADR файлов. Однако:

1. Пакет `pre-commit` не установлен в системе разработки
2. При каждом `git commit` Git пытается выполнить pre-commit hooks
3. Пользователи получают ошибку: `pre-commit not found. Did you forget to activate your virtualenv?`
4. Временное решение: `git commit --no-verify`

Это создаёт неудобство для всех разработчиков и нарушает CI/CD процессы.

## Decision

**Устанавливать `pre-commit` в систему как часть разработки.**

### Дополнительное требование

Хук ADR-валидации **должен проверять корректность формата** с учётом существующих файлов:

- ADR-001 ... ADR-011 ✅
- FINAL-REVIEW-COMPLETE.md ⚠️ (нарушает формат)
- IMPLEMENTATION_REPORT_2026_03_18.md ⚠️ (нарушает формат)

Эти файлы **не являются ADR** — они отчётные документы и должны быть перенесены в отдельную директорию `docs/reports/` для соблюдения формата ADR.

## Implementation

### Option 1: Установить pre-commit (Рекомендуется)

```bash
# Установка
pip install pre-commit

# Активация хуков
pre-commit install
```

Добавить в `.env.example` или `CONTRIBUTING.md`:
```
# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

**Pros**:
- Сохраняет валидацию ADR формата
- Автоматическая проверка при каждом коммите
- Единый стандарт для команды

**Cons**:
- Требует установки пакета
- Задержка при коммите (незначительная)

### Option 2: Заменить на shell-скрипт без pre-commit

Использовать `entry: bash` вместо `entry: python3` с простым скриптом:

```yaml
- id: adr-numbering
  name: ADR numbering validation
  entry: bash
  args: [-c, 'python3 -c "..."']
  language: system
```

**Pros**:
- Не требует pre-commit пакета
- Быстрая активация

**Cons**:
- Сложнее поддерживать
- Менее гибкий

## Decision

**Выбираем Option 1: Установка pre-commit как стандартная практика разработки.**

### Действия

1. Добавить в `pyproject.toml` или создать `.pre-commit-requirements.txt`:
   ```
   pre-commit>=3.0.0
   ```

2. Обновить `.pre-commit-config.yaml` с `fail: false` для неблокирующей проверки (опционально):

   ```yaml
   - id: adr-numbering
     ...
     fail: false  # Предупреждение, но не блокировка
   ```

3. Добавить в `CLAUDE.md` секцию "Development Setup":
   ```bash
   # Install pre-commit hooks (REQUIRED for this repo)
   pip install pre-commit
   pre-commit install
   ```

4. Перенести отчётные файлы в `docs/reports/`:
   - `docs/explanation/adr/FINAL-REVIEW-COMPLETE.md` → `docs/reports/FINAL-REVIEW-COMPLETE.md`
   - `docs/explanation/adr/IMPLEMENTATION_REPORT_2026_03_18.md` → `docs/reports/IMPLEMENTATION_REPORT_2026_03_18.md`

## Consequences

### Positive
- Устранение ошибки "pre-commit not found"
- Единый стандарт валидации ADR для всех разработчиков
- Улучшение качества коммитов

### Negative
- Необходимость установки pre-commit для новых разработчиков

## References

- [.pre-commit-config.yaml](./.pre-commit-config.yaml)
- [ADR-001-system-genesis.md](./ADR-001-system-genesis.md)