---

dependencies:
- promt-verification
- promt-index-update
description: Экспорт отчётов синхронизации в различные форматы для документации и
  обмена
layer: Meta
name: promt-sync-report-export
status: active
tags:
- sync
- export
- report
- documentation
type: p9i
version: '1.2'
---

# AI Agent Prompt: Экспорт отчётов синхронизации

**Version:** 1.2
**Date:** 2026-03-18
**Purpose:** Экспорт отчётов синхронизации в различные форматы для документации и обмена

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Meta / Export |
| **Время выполнения** | 5–15 мин |
| **Домен** | Documentation — report export |

**Пример запроса:**

> «Используя `promt-sync-report-export.md`, экспортируй отчёты синхронизации
> в Markdown, JSON и PDF форматы для team review.»

**Ожидаемый результат:**
- Отчёты экспортированы в заданные форматы
- Отчёты сохранены в artifacts/reports/
- Отчёты готовы для sharing

---

## Когда использовать

- После выполнения workflow — экспорт результатов
- После консолидации ADR — экспорт отчёта консолидации
- После верификации — экспорт отчёта верификации
- Periodic export — еженедельный отчёт о состоянии системы
- Pre-meeting — подготовка материалов для review

---

## Mission Statement

Ты — AI-агент, специализирующийся на **экспорте отчётов** — преобразовании результатов синхронизации в различные форматы.

Твоя задача:
1. **Собрать все отчёты** — найти отчёты в artifacts/
2. **Конвертировать форматы** — Markdown → JSON/PDF/HTML
3. **Структурировать данные** — единая структура для всех отчётов
4. **Сохранить отчёты** — в artifacts/reports/ с timestamp
5. **Генерировать summary** — общий отчёт по всем экспортам

---

## Контракт синхронизации системы

Обязательные инварианты:
- Все отчёты сохраняются с timestamp
- Форматы совместимы (содержимое идентично)
- Структура JSON отчётов предсказуема
- Отчёты всегда в artifacts/reports/
- Metadata (автор, дата, version) присутствует

---

## Шаг 1: Сбор отчётов

### 1.1. Найти все отчёты в artifacts/

```bash
# Найти все отчёты
find artifacts/ -name "*report*.md" -o -name "*report*.json"

# Найти отчёты по типу
find artifacts/ -name "*verification*report*"
find artifacts/ -name "*consolidation*report*"
find artifacts/ -name "*sync*report*"
find artifacts/ -name "*workflow*report*"
```

### 1.2. Классифицировать отчёты

```markdown
## Report Types

| Тип | Шаблон | Пример |
|-----|---------|---------|
| **Verification** | *verification*report* | verification-report-2026-03-18T12:00:00Z.md |
| **Consolidation** | *consolidation*report* | consolidation-report-2026-03-18T13:00:00Z.md |
| **Sync** | *sync*report* | index-update-report-2026-03-18T14:00:00Z.md |
| **Migration** | *migration*report* | adr-migration-report-2026-03-18T15:00:00Z.md |
| **Planning** | *plan*report* | adr-implementation-plan-2026-03-18T16:00:00Z.md |
| **Workflow** | *workflow*report* | workflow-report-2026-03-18T17:00:00Z.md |
```

---

## Шаг 2: Конвертация форматов

### 2.1. Markdown → JSON

```python
import json
import re
from datetime import datetime
from pathlib import Path

def md_to_json(md_file):
    """
    Convert Markdown report to JSON format.

    Args:
        md_file: Path to Markdown file

    Returns:
        dict with structured JSON
    """
    with open(md_file, 'r') as f:
        content = f.read()

    # Parse metadata (first 20 lines)
    metadata = {}
    for line in content.split('\n')[:20]:
        if '**Date:**' in line:
            metadata['date'] = line.split('**Date:**')[1].strip()
        elif '**Status:**' in line:
            metadata['status'] = line.split('**Status:**')[1].strip()
        elif '**Scope:**' in line:
            metadata['scope'] = line.split('**Scope:**')[1].strip()

    # Parse sections
    sections = {}
    current_section = None
    current_content = []

    for line in content.split('\n'):
        if line.startswith('## '):
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()

            # Start new section
            current_section = line[3:].strip()
            current_content = []
        else:
            current_content.append(line)

    # Save last section
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()

    # Parse tables
    tables = {}
    table_pattern = r'\| (.+?) \|\n\|[-]+\|[\s\S]*?(?=\n\n|\Z)'
    for match in re.finditer(table_pattern, content):
        # Extract table header and rows
        lines = match.group(0).split('\n')
        header = [cell.strip() for cell in lines[0].split('|')[1:-1]]
        rows = []
        for line in lines[2:]:  # Skip separator line
            if line.strip().startswith('|'):
                row = [cell.strip() for cell in line.split('|')[1:-1]]
                rows.append(row)
        tables[header[0]] = {
            'header': header,
            'rows': rows
        }

    # Parse checklists
    checklists = {}
    checklist_pattern = r'- \[([ x])\] (.+)'
    for match in re.finditer(checklist_pattern, content):
        checked = match.group(1) == 'x'
        item = match.group(2).strip()
        # Group by section (simplified)
        section = current_section or 'general'
        if section not in checklists:
            checklists[section] = []
        checklists[section].append({
            'item': item,
            'checked': checked
        })

    return {
        'metadata': metadata,
        'content': content,
        'sections': sections,
        'tables': tables,
        'checklists': checklists,
        'file_path': str(md_file),
        'exported_at': datetime.now().isoformat()
    }

# Usage
md_file = Path('artifacts/verification/verification-report-2026-03-18.md')
json_report = md_to_json(md_file)

# Save JSON
json_file = md_file.with_suffix('.json')
with open(json_file, 'w') as f:
    json.dump(json_report, f, indent=2)
```

### 2.2. Markdown → HTML

```python
import markdown
from jinja2 import Template

def md_to_html(md_file):
    """
    Convert Markdown report to HTML format.

    Args:
        md_file: Path to Markdown file

    Returns:
        HTML string
    """
    with open(md_file, 'r') as f:
        content = f.read()

    # Convert Markdown to HTML
    html_content = markdown.markdown(
        content,
        extensions=['tables', 'fenced_code']
    )

    # Wrap in HTML template
    template = Template('''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3 {
            margin-top: 2em;
            margin-bottom: 1em;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f5f5f5;
        }
        code {
            background-color: #f5f5f5;
            padding: 2px 5px;
            border-radius: 3px;
        }
        pre {
            background-color: #f5f5f5;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    {{ content }}
</body>
</html>
    ''')

    title = md_file.stem
    html = template.render(title=title, content=html_content)

    return html

# Usage
md_file = Path('artifacts/verification/verification-report-2026-03-18.md')
html = md_to_html(md_file)

# Save HTML
html_file = md_file.with_suffix('.html')
with open(html_file, 'w') as f:
    f.write(html)
```

### 2.3. Markdown → PDF (через pandoc)

```bash
# Install pandoc
sudo apt-get install pandoc

# Convert MD to PDF
pandoc artifacts/verification/verification-report-2026-03-18.md \
  -o artifacts/verification/verification-report-2026-03-18.pdf \
  --pdf-engine=xelatex \
  -V geometry:margin=1in \
  -V colorlinks=true \
  -V linkcolor=blue
```

---

## Шаг 3: Структурирование данных

### 3.1. Единая структура для всех отчётов

```json
{
  "report": {
    "metadata": {
      "report_id": "verification-2026-03-18T12:00:00Z",
      "report_type": "verification",
      "title": "ADR Verification Report",
      "created_at": "2026-03-18T12:00:00Z",
      "author": "AI Agent (Verification Prompt)",
      "version": "3.4"
    },
    "summary": {
      "status": "completed",
      "total_adrs": 15,
      "critical_adrs": 5,
      "average_implementation": "67.3%",
      "adr_compliance": "94.2%",
      "code_quality": "87.5%",
      "production_ready": true
    },
    "content": {
      "raw": "...",  // Full Markdown content
      "sections": {
        "Summary": "...",
        "ADR Details": "...",
        "Code Quality": "..."
      }
    },
    "data": {
      "tables": {
        "ADR Verification": {
          "header": ["#", "Topic Slug", "Status", "Progress"],
          "rows": [...]
        }
      },
      "checklists": {
        "Verification Checklist": [
          {"item": "ADR structure verified", "checked": true},
          ...
        ]
      }
    },
    "exports": {
      "markdown": "artifacts/reports/verification-2026-03-18.md",
      "json": "artifacts/reports/verification-2026-03-18.json",
      "html": "artifacts/reports/verification-2026-03-18.html",
      "pdf": "artifacts/reports/verification-2026-03-18.pdf"
    }
  }
}
```

### 3.2. Индекс всех отчётов

```json
{
  "reports_index": {
    "updated_at": "2026-03-18T18:00:00Z",
    "total_reports": 6,
    "reports": [
      {
        "report_id": "verification-2026-03-18T12:00:00Z",
        "report_type": "verification",
        "title": "ADR Verification Report",
        "created_at": "2026-03-18T12:00:00Z",
        "files": {
          "markdown": "artifacts/reports/verification-2026-03-18.md",
          "json": "artifacts/reports/verification-2026-03-18.json",
          "html": "artifacts/reports/verification-2026-03-18.html",
          "pdf": "artifacts/reports/verification-2026-03-18.pdf"
        },
        "summary": {
          "status": "completed",
          "adr_compliance": "94.2%"
        }
      },
      // ... more reports
    ]
  }
}
```

---

## Шаг 4: Сохранение отчётов

### 4.1. Структура директории

```bash
# Create reports directory structure
mkdir -p artifacts/reports/{verification,consolidation,sync,migration,planning,workflow}

# Copy reports to structured directories
cp artifacts/verification/*report*.md artifacts/reports/verification/
cp artifacts/consolidation/*report*.md artifacts/reports/consolidation/
cp artifacts/sync/*report*.md artifacts/reports/sync/
```

### 4.2. Сохранение с timestamp

```bash
# Save report with timestamp
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
report_file="artifacts/reports/verification/verification-report-${timestamp}.md"

# Copy report
cp artifacts/verification/verification-report.md "$report_file"

# Generate all formats
python3 scripts/md_to_json.py "$report_file"
python3 scripts/md_to_html.py "$report_file"
pandoc "$report_file" -o "${report_file%.md}.pdf"
```

---

## Шаг 5: Генерация summary отчёта

### 5.1. Общий отчёт по всем экспортам

```markdown
# Reports Export Summary
**Date:** 2026-03-18T18:00:00Z
**Total Reports Exported:** 6

## Export Summary

| Type | Count | Formats |
|-------|--------|---------|
| **Verification** | 2 | MD, JSON, HTML, PDF |
| **Consolidation** | 1 | MD, JSON, HTML |
| **Sync** | 2 | MD, JSON |
| **Migration** | 1 | MD, JSON, HTML, PDF |

## Reports List

### Verification Reports

| Report ID | Date | Status | Files |
|-----------|------|--------|-------|
| verification-2026-03-18T12:00:00Z | 2026-03-18 | ✅ Completed | MD, JSON, HTML, PDF |
| verification-2026-03-17T09:00:00Z | 2026-03-17 | ✅ Completed | MD, JSON |

### Consolidation Reports

| Report ID | Date | Status | Files |
|-----------|------|--------|-------|
| consolidation-2026-03-18T13:00:00Z | 2026-03-18 | ✅ Completed | MD, JSON, HTML |

### Sync Reports

| Report ID | Date | Status | Files |
|-----------|------|--------|-------|
| index-update-2026-03-18T14:00:00Z | 2026-03-18 | ✅ Completed | MD, JSON |
| readme-sync-2026-03-18T15:00:00Z | 2026-03-18 | ✅ Completed | MD, JSON |

### Migration Reports

| Report ID | Date | Status | Files |
|-----------|------|--------|-------|
| adr-migration-2026-03-18T16:00:00Z | 2026-03-18 | ✅ Completed | MD, JSON, HTML, PDF |

## Statistics

| Metric | Value |
|--------|-------|
| **Total Reports** | 6 |
| **Total Files** | 18 (MD: 6, JSON: 6, HTML: 3, PDF: 3) |
| **Total Size** | 2.5 MB |
| **Export Duration** | 15 min |

## File Locations

All reports are saved in:
- `artifacts/reports/verification/`
- `artifacts/reports/consolidation/`
- `artifacts/reports/sync/`
- `artifacts/reports/migration/`
- `artifacts/reports/planning/`
- `artifacts/reports/workflow/`

Reports index: `artifacts/reports/reports-index.json`

## Next Steps

- [ ] Review verification reports with team
- [ ] Share PDF reports with stakeholders
- [ ] Archive older reports (keep last 30 days)
- [ ] Schedule next export (weekly)
```

---

## Шаг 6: Создание отчёта экспорта

### 6.1. Структура отчёта экспорта

Сохранить в: `artifacts/reports/export-summary-{timestamp}.md`

```markdown
# Export Summary
**Date:** 2026-03-18T18:00:00Z

## Export Details

- **Source:** artifacts/
- **Destination:** artifacts/reports/
- **Formats:** Markdown, JSON, HTML, PDF
- **Reports Exported:** 6
- **Files Created:** 18
- **Duration:** 15 min

## Formats Generated

| Format | Count | Total Size |
|---------|--------|------------|
| Markdown (.md) | 6 | 1.2 MB |
| JSON (.json) | 6 | 0.8 MB |
| HTML (.html) | 3 | 0.3 MB |
| PDF (.pdf) | 3 | 0.2 MB |

## Verification

- ✅ All files created successfully
- ✅ All formats valid
- ✅ JSON structure correct
- ✅ HTML renders correctly
- ✅ PDF renders correctly

## Files

### Verification Reports
- artifacts/reports/verification/verification-report-2026-03-18T12:00:00Z.md
- artifacts/reports/verification/verification-report-2026-03-18T12:00:00Z.json
- artifacts/reports/verification/verification-report-2026-03-18T12:00:00Z.html
- artifacts/reports/verification/verification-report-2026-03-18T12:00:00Z.pdf

// ... more files

## Recommendations

- ✅ Export completed successfully
- ✅ All reports ready for sharing
- ✅ Archive older reports (>30 days)
```

---

## Финальный чеклист экспорта

- [ ] Все отчёты найдены в artifacts/
- [ ] Отчёты классифицированы по типу
- [ ] Markdown → JSON конвертация выполнена
- [ ] Markdown → HTML конвертация выполнена
- [ ] Markdown → PDF конвертация выполнена
- [ ] Структура данных унифицирована
- [ ] Отчёты сохранены в artifacts/reports/
- [ ] Timestamp добавлен к именам файлов
- [ ] Индекс отчётов создан
- [ ] Summary отчёт создан
- [ ] Все форматы валидированы

---

## Связанные промпты

| Промпт | Когда использовать |
|--------|-------------------|
| `promt-verification.md` | После — экспорт отчёта верификации |
| `promt-consolidation.md` | После — экспорт отчёта консолидации |
| `promt-index-update.md` | После — экспорт отчёта sync |
| `promt-workflow-orchestration.md` | После — экспорт отчёта workflow |

---

## Метрики успеха экспорта

| Метрика | Требование |
|---------|------------|
| Все отчёты экспортированы | Да |
| Все форматы созданы | MD, JSON, HTML, PDF (как минимум MD+JSON) |
| Структура данных унифицирована | Да |
| Timestamp в именах | Да |
| Валидность форматов | Да |

---

## Anti-patterns при экспорте

| Anti-pattern | Правильный подход |
|--------------|------------------|
| Экспортировать только MD | Генерировать все форматы (MD+JSON как минимум) |
| Не сохранять timestamp | Всегда добавлять timestamp к имени файла |
| Не структурировать данные | Использовать единую структуру JSON |
| Не проверять валидность | Валидировать все форматы |
| Хаотичное расположение файлов | Структурировать по типу отчётов |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.2 | 2026-03-18 | Добавлена структура отчёта экспорта |
| 1.1 | 2026-03-06 | Добавлена поддержка PDF (через pandoc) |
| 1.0 | 2026-02-20 | Первая версия: basic MD→JSON export |

---

**Prompt Version:** 1.2
**Date:** 2026-03-18
