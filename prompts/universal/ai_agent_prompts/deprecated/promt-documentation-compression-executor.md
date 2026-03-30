---

dependencies:
- promt-verification
- promt-index-update
description: Компрессия документации при сохранении качества и структурирование для
  оптимизации
layer: Meta
name: promt-documentation-quality-compression
status: active
tags:
- documentation
- quality
- compression
type: p9i
version: '1.1'
---

# AI Agent Prompt: Компрессия и качество документации

**Version:** 1.1
**Date:** 2026-03-18
**Purpose:** Компрессия документации при сохранении качества и структурирование для оптимизации

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Meta / Documentation |
| **Время выполнения** | 15–30 мин |
| **Домен** | Documentation — compression & quality |

**Пример запроса:**

> «Используя `promt-documentation-quality-compression.md`, выполни компрессию документации:
> удали избыточную информацию, структурируй, сохрани качество.»

**Ожидаемый результат:**
- Компрессированная документация без потери качества
- Оптимизированная структура для быстрого поиска
- Отчёт о компрессии (ratio, сохранённый контент)

---

## Когда использовать

- После создания большого количества документации
- Перед деплоем документации (оптимизация размера)
- Periodic compression — ежемесячная оптимизация
- После рефакторинга — удалить дублирующую документацию

---

## Mission Statement

Ты — AI-агент, специализирующийся на **компрессии документации** — оптимизации размера без потери качества.

Твоя задача:
1. **Анализировать документацию** — найти избыточность, дубликаты
2. **Компрессировать контент** — удалить лишнее, объединить похожее
3. **Структурировать** — оптимизировать навигацию и поиск
4. **Сохранить качество** — вся ключевая информация сохранена
5. **Отчитать** — что было сжато и сохранено

---

## Контракт синхронизации системы

Обязательные инварианты:
- Вся ключевая информация сохранена
- Нет потери смысла контента
- Структура оптимизирована для поиска
- Ссылки на документацию актуальны
- Отчёт о компрессии создан

---

## Шаг 0: Анализ документации

### 0.1. Получить список всех файлов документации

```bash
# Найти все файлы документации
find docs/ -name "*.md" | sort

# Получить размер каждого файла
find docs/ -name "*.md" -exec du -h {} \; | sort -hr

# Получить общее количество файлов и размер
find docs/ -name "*.md" | wc -l
du -sh docs/
```

### 0.2. Найти дублирующую документацию

```bash
# Найти файлы с похожими названиями
find docs/ -name "*.md" | sed 's|.*/||' | sort | uniq -d

# Найти файлы с похожим контентом (>80% совпадение)
# (требует специализированный скрипт для сравнения контента)
```

---

## Шаг 1: Определение избыточности

### 1.1. Типы избыточности

```markdown
## Redundancy Types

### 1. Content Duplication

**Пример:** Один и тот же контент в нескольких файлах

```markdown
# File 1: docs/how-to/setup.md
## Installation
pip install p9i

# File 2: docs/how-to/installation.md
## Installation
pip install p9i
```

**Решение:** Merge или удалить один файл

### 2. Structural Redundancy

**Пример:** Избыточные уровни вложенности

```markdown
## Section 1
### Subsection 1.1
#### Sub-subsection 1.1.1
```

**Решение:** Flatten structure

### 3. Verbal Redundancy

**Пример:** Повторение одной и той же фразы

```markdown
To install, install the package. To install, follow these steps...
```

**Решение:** Rewrite concisely

### 4. Metadata Redundancy

**Пример:** Избыточные заголовки и description

```markdown
# AI Prompt System

## Overview
The AI Prompt System is a system for managing AI prompts.

## Description
This system manages AI prompts through their lifecycle.
```

**Решение:** Merge Overview + Description

### 5. Code Block Redundancy

**Пример:** Один и тот же код в нескольких файлах

```bash
# File 1
export PYTHONPATH="${PYTHONPATH}:/app"

# File 2
export PYTHONPATH="${PYTHONPATH}:/app"
```

**Решение:** Extract to common snippet file
```

### 1.2. Анализ избыточности

```bash
# Найти дублирующие заголовки
grep -h "^## " docs/**/*.md | sort | uniq -d

# Найти повторяющиеся фразы (>50 повторений)
grep -h "To" docs/**/*.md | sort | uniq -c | sort -rn | head -20

# Найти избыточные code blocks (по хэшу)
grep -h "^\`\`\`bash" docs/**/*.md | wc -l
```

---

## Шаг 2: Компрессия контента

### 2.1. Merge дублирующих файлов

```bash
# Если два файла с похожим контентом — merge
# File 1: docs/how-to/setup.md
# File 2: docs/how-to/installation.md

# Merge в один файл
cat > docs/how-to/setup.md << 'EOF'
# Installation & Setup

## Prerequisites
- Python 3.10+
- pip or poetry

## Installation

### Using pip
```bash
pip install p9i
```

### Using poetry
```bash
poetry add p9i
```

## Setup

### Environment Variables
```bash
export AI_PROMPT_SYSTEM_CONFIG=/path/to/config.yaml
```

### Verify Installation
```bash
p9i --version
```
EOF

# Удалить старый файл
rm docs/how-to/installation.md
```

### 2.2. Flatten структура

```markdown
# Было (избыточная вложенность)

## 1. Getting Started
### 1.1. Installation
#### 1.1.1. Prerequisites

# Стало (оптимальная структура)

## Getting Started

### Installation

#### Prerequisites
```

### 2.3. Удалить избыточные фразы

```markdown
# Было (verbal redundancy)

To install the AI Prompt System, you need to install the package.
To install the package, follow these steps: first, install the dependencies;
second, install the package; third, verify the installation.

# Стало (concise)

Install the AI Prompt System by following these steps:
1. Install dependencies
2. Install the package
3. Verify installation
```

### 2.4. Extract общие code blocks

```bash
# Создать файл для общих snippets
mkdir -p docs/snippets

# Извлечь общий код
cat > docs/snippets/common-env-vars.sh << 'EOF'
# Common Environment Variables
export PYTHONPATH="${PYTHONPATH}:/app"
export AI_PROMPT_SYSTEM_CONFIG="${AI_PROMPT_SYSTEM_CONFIG:-/app/config.yaml}"
export AI_PROMPT_SYSTEM_LOG_LEVEL="${AI_PROMPT_SYSTEM_LOG_LEVEL:-INFO}"
EOF

# Заменить дубликаты ссылками на snippet
find docs/ -name "*.md" -exec sed -i \
  's/export PYTHONPATH=".*"/See [Common Environment Variables](..\/snippets\/common-env-vars.md)/g' {} \;
```

---

## Шаг 3: Структурирование документации

### 3.1. Оптимизация навигации

```markdown
## Optimized Documentation Structure

```
docs/
├── README.md                  # Quick start
├── getting-started/           # Getting started guides
│   ├── installation.md       # Installation (merged from setup+installation)
│   ├── quick-start.md        # Quick start tutorial
│   └── first-project.md      # Create first project
├── how-to/                   # Task-based guides
│   ├── create-prompt.md      # Create new prompt
│   ├── run-prompt.md        # Run a prompt
│   └── manage-memory.md      # Manage project memory
├── reference/               # API reference (AUTO-GENERATED)
│   ├── mcp-tools.md        # MCP tools
│   ├── prompts.md          # Available prompts
│   └── configuration.md   # Configuration options
├── explanation/            # Conceptual explanations
│   ├── adr/               # Architecture Decision Records
│   │   ├── index.md      # ADR index
│   │   └── ADR-*.md     # Individual ADRs
│   └── architecture.md    # System architecture
├── snippets/               # Code snippets (extracted)
│   ├── common-env-vars.md  # Common environment variables
│   └── python-examples.md # Python examples
└── official_document/      # Official documentation (READ-ONLY)
    ├── code-server/
    ├── k3s/
    └── ...
```

### 3.2. Оптимизация поиска

```markdown
## Search Optimization

### Keywords

Добавить keywords в начале каждого файла для быстрого поиска:

```markdown
---
keywords: [installation, setup, getting-started, quick-start]
---

# Installation & Setup
...
```

### Cross-references

Добавить cross-references между связанными документами:

```markdown
See [Installation](../getting-started/installation.md) for setup instructions.
See [MCP Tools](../reference/mcp-tools.md) for available tools.
See [ADR-002](../explanation/adr/ADR-002-tiered-prompt-architecture.md) for tier architecture.
```
```

---

## Шаг 4: Верификация качества

### 4.1. Проверить потерянную информацию

```bash
# Проверить, что все заголовки есть в новом файле (после merge)
grep "^## " docs/how-to/setup.md
# Должны быть заголовки из обоих старых файлов

# Проверить, что все code blocks есть
grep "^\`\`\`" docs/how-to/setup.md | wc -l
# Должно быть ≥ суммы code blocks из старых файлов
```

### 4.2. Проверить ссылки

```bash
# Проверить, что все ссылки работают
find docs/ -name "*.md" -exec grep -oE '\[.*\]\(([^)]+)\)' {} \; | \
  while read link; do
    url=$(echo "$link" | sed 's/.*(\([^)]*\)).*/\1/')
    if [[ ! "$url" =~ ^https?:// ]]; then
      # Local link - check file exists
      if [ ! -f "docs/${url#../}" ]; then
        echo "Broken link: $url"
      fi
    fi
  done
```

### 4.3. Проверить размер до и после

```bash
# Размер до compression
size_before=$(du -s docs/ | cut -f1)

# Размер после compression
size_after=$(du -s docs/ | cut -f1)

# Compression ratio
ratio=$(echo "scale=2; ($size_before - $size_after) * 100 / $size_before" | bc)
echo "Compression: ${ratio}% (reduced from ${size_before}KB to ${size_after}KB)"
```

---

## Шаг 5: Создание отчёта компрессии

### 5.1. Структура отчёта

Сохранить в: `artifacts/compression/documentation-compression-{timestamp}.md`

```markdown
# Documentation Compression Report
**Date:** 2026-03-18T18:00:00Z

## Summary

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **Total Files** | 50 | 42 | -8 (-16%) |
| **Total Size** | 2.5 MB | 2.0 MB | -0.5 MB (-20%) |
| **Avg File Size** | 50 KB | 48 KB | -2 KB (-4%) |
| **Duplicate Files** | 8 | 0 | -8 (-100%) |

## Compression Actions

### Files Merged (8)

| Source Files | Target File | Reason |
|-------------|--------------|--------|
| docs/how-to/setup.md + docs/how-to/installation.md | docs/how-to/setup.md | Content duplication (95%) |
| docs/how-to/usage.md + docs/how-to/run-prompts.md | docs/how-to/run-prompt.md | Content overlap (80%) |
| docs/reference/tools.md + docs/reference/mcp-tools.md | docs/reference/mcp-tools.md | Content duplication (90%) |
| ... | ... | ... |

### Code Blocks Extracted (15)

| Common Code | Snippet File | References |
|-------------|--------------|------------|
| Environment variables | docs/snippets/common-env-vars.sh | 8 files |
| Python examples | docs/snippets/python-examples.md | 5 files |
| Bash scripts | docs/snippets/bash-examples.sh | 3 files |

### Structure Flattened (5)

| File | Changes |
|------|---------|
| docs/explanation/architecture.md | Removed 2 excessive nesting levels |
| docs/how-to/create-prompt.md | Simplified section headers |
| ... | ... |

## Quality Verification

- ✅ All key information preserved
- ✅ No broken links
- ✅ All code blocks present
- ✅ Search optimized (keywords added)
- ✅ Cross-references added

## Recommendations

- ✅ Compression successful (20% size reduction)
- ✅ No quality loss
- ✅ Search improved (keywords + cross-references)
- ⏳ Consider adding full-text search (e.g., Algolia)
- ⏳ Schedule next compression (monthly)

## Next Steps

- [ ] Review compressed documentation
- [ ] Update documentation generation scripts
- [ ] Test search functionality
- [ ] Deploy to production
```

---

## Финальный чеклист компрессии

- [ ] Все файлы документации проанализированы
- [ ] Дубликаты найдены
- [ ] Избыточность определена
- [ ] Дублирующие файлы объединены
- [ ] Структура упрощена (flatten)
- [ ] Избыточные фразы удалены
- [ ] Общие code blocks извлечены
- [ ] Структура оптимизирована
- [ ] Keywords добавлены
- [ ] Cross-references добавлены
- [ ] Качество проверено (информация сохранена)
- [ ] Ссылки проверены (no broken links)
- [ ] Размер измерен (до/после)
- [ ] Отчёт создан

---

## Связанные промпты

| Промпт | Когда использовать |
|--------|-------------------|
| `promt-index-update.md` | После — обновить index.md |
| `promt-readme-sync.md` | После — синхронизировать README.md |
| `promt-sync-report-export.md` | После — экспортировать отчёт компрессии |

---

## Метрики успеха компрессии

| Метрика | Требование |
|---------|------------|
| Информация сохранена | 100% ключевой информации |
| Размер уменьшен | ≥ 10% reduction |
| Broken links | 0 |
| Поиск улучшен | Keywords + cross-references |

---

## Anti-patterns при компрессии

| Anti-pattern | Правильный подход |
|--------------|------------------|
| Удалять контент без проверки | Всегда проверять, что информация сохранена |
| Компрессировать reference docs | Reference docs AUTO-GENERATED — не редактировать |
| Забывать обновлять ссылки | Всегда обновлять ссылки после merge |
| Удалять code blocks | Extract в snippets, не удалять |
| Компрессировать official_document/ | official_document/ READ-ONLY — не трогать |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.1 | 2026-03-18 | Добавлена структура отчёта компрессии |
| 1.0 | 2026-02-20 | Первая версия: basic documentation compression |

---

**Prompt Version:** 1.1
**Date:** 2026-03-18
**Location:** deprecated/ (moved to ai_agent_prompts/)
