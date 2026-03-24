# UI/UX Data Sync Strategy

## Source: ui-ux-pro-mcp

### Data Files (CSV format)

| File | Size | Records | Description |
|------|------|---------|-------------|
| styles.csv | 28KB | ~20 | UI styles with CSS/Motion configs |
| colors.csv | 187KB | ~121 | Color palettes |
| typography.csv | 35KB | ~74 | Font pairings |
| icons.csv | 113KB | ~176 | Lucide icons |
| ux-guidelines.csv | 148KB | ~115 | UX best practices |
| stacks/ | 72KB | ~696 | Framework guidelines |
| platforms/ | - | ~220 | iOS HIG, Android Material 3 |

### CSV Structure Example (styles.csv)

```
"STT","Style Category","Type","Keywords","Primary Colors","Secondary Colors",
"Effects & Animation","Best For","Do Not Use For","Light Mode ✓","Dark Mode ✓",
"Performance","Accessibility","Mobile-Friendly","Conversion-Focused",
"Framework Compatibility","Era/Origin","Complexity","CSS_Code","Motion_Config",
"Animation_Variants"
```

### Rich Fields
- CSS_Code: готовый CSS
- Motion_Config: JSON для анимаций
- Animation_Variants: JSON variants

## Current embedded.py Structure

### Simplified for p9i
- id, name, description
- data (dict с ключами)
- tags (list)

## Sync Strategy

### Option 1: CSV Parser Script

```python
# src/infrastructure/uiux/sync.py
import csv
import httpx
import os

async def sync_from_github():
    """Sync data from ui-ux-pro-mcp"""
    base_url = "https://raw.githubusercontent.com/redf0x1/ui-ux-pro-mcp/main/data"

    files = {
        "styles": "styles.csv",
        "colors": "colors.csv",
        # ...
    }

    for category, filename in files.items():
        url = f"{base_url}/{filename}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            # Parse CSV and convert to embedded.py format
```

### Option 2: Git Submodule

```bash
git submodule add https://github.com/redf0x1/ui-ux-pro-mcp.git third_party/ui-ux-pro-mcp
```

### Option 3: Incremental Update Script

```python
# Update only new/changed items by ID
def update_category(category: str, new_items: List[dict]):
    current = load_category(category)
    current_ids = {item["id"] for item in current}

    for item in new_items:
        if item["id"] not in current_ids:
            current.append(item)

    save_category(category, current)
```

## Recommended: CSV Parser

Create `src/infrastructure/uiux/sync.py`:

```python
import csv
import json
from io import StringIO
from typing import Dict, List, Any

def parse_styles_csv(csv_content: str) -> List[Dict[str, Any]]:
    """Parse styles.csv with rich data."""
    reader = csv.DictReader(StringIO(csv_content))
    results = []

    for row in reader:
        # Extract key fields
        item = {
            "id": f"style-{row['STT']}",
            "name": row['Style Category'],
            "description": f"{row['Type']} - Keywords: {row['Keywords']}",
            "data": {
                "primary_colors": row['Primary Colors'],
                "secondary_colors": row['Secondary Colors'],
                "effects": row['Effects & Animation'],
                "best_for": row['Best For'],
                "do_not_use_for": row['Do Not Use For'],
                "css_code": row.get('CSS_Code', ''),
                "motion_config": row.get('Motion_Config', ''),
            },
            "tags": row['Keywords'].split(', ')[:5],
        }
        results.append(item)

    return results
```

## Update Commands

### Manual Sync
```bash
# Download latest CSV
curl -s https://raw.githubusercontent.com/redf0x1/ui-ux-pro-mcp/main/data/styles.csv > data/styles_new.csv

# Run parser
python -m src.infrastructure.uiux.sync --category styles
```

### CI/CD Sync (GitHub Action)
```yaml
# .github/workflows/sync-uiux.yml
name: Sync UI/UX Data
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Sync data
        run: python -m src.infrastructure.uiux.sync
      - name: Commit changes
        run: |
          git config --local user.email "ci@github.com"
          git config --local user.name "CI"
          git add src/infrastructure/uiux/data/
          git commit -m "chore: sync UI/UX data" || echo "No changes"
```

## Fields to Extract

### Styles (CSS, Tailwind, Motion)
- CSS_Code → data.css
- Framework Compatibility → data.frameworks
- Motion_Config → data.animation

### Colors
- Primary Colors → data.primary
- Secondary Colors → data.secondary

### Stack Guidelines
- Already structured per framework

## Conclusion

Best approach: Create sync.py that:
1. Downloads CSV from GitHub
2. Parses to simplified p9i format
3. Updates embedded.py or database

For MVP: Keep embedded.py, update manually monthly.
