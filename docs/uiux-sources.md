# UI/UX Data Sources Research

## Executive Summary

Multi-source strategy for UI/UX design resources:
1. **ui-ux-pro-mcp** - Main source (styles, colors, icons)
2. **shadcn/ui** - Component library
3. **Claude Cookbooks** - AI/Claude integration patterns
4. **Context7** - Real-time documentation
5. **Primary Sources** - Official design systems

---

## 1. ui-ux-pro-mcp (Primary Source)

### Overview
- **URL**: https://github.com/redf0x1/ui-ux-pro-mcp
- **Data**: 1920+ curated design resources
- **Format**: CSV files in `data/`

### Files

| File | Size | Records | Fields |
|------|------|---------|--------|
| styles.csv | 28KB | ~20 | CSS_Code, Motion_Config, Animation_Variants |
| colors.csv | 187KB | ~121 | Industry palettes |
| typography.csv | 35KB | ~74 | Font pairings |
| icons.csv | 113KB | ~176 | Lucide icons |
| ux_guidelines.csv | 148KB | ~115 | WCAG, best practices |
| stacks/ | 72KB | ~696 | Framework guidelines |
| platforms/ | - | ~220 | iOS HIG, Android Material 3 |

### Key Fields in styles.csv
```
"CSS_Code" - готовый CSS
"Motion_Config" - JSON анимации
"Animation_Variants" - JSON variants
"Framework Compatibility" - Tailwind/Bootstrap/MUI rating
```

### Sync Strategy
```python
# Parser required - rich data
def parse_styles_csv(csv_content):
    return [{
        "id": f"style-{row['STT']}",
        "name": row['Style Category'],
        "data": {
            "css": row['CSS_Code'],
            "motion": row['Motion_Config'],
            "frameworks": row['Framework Compatibility'],
        }
    }]
```

---

## 2. shadcn/ui (Components)

### Overview
- **URL**: https://github.com/shadcn-ui/ui
- **Components**: 50+ React components
- **Docs**: https://ui.shadcn.com/docs/components

### Components List
```
Accordion, Alert, Alert Dialog, Aspect Ratio, Avatar, Badge,
Breadcrumb, Button, Button Group, Calendar, Card, Carousel,
Chart, Checkbox, Collapsible, Combobox, Command, Context Menu,
Data Table, Date Picker, Dialog, Direction, Drawer, Dropdown Menu,
Empty, Field, Hover Card, Input, Input Group, Input OTP, Item,
Kbd, Label, Menubar, Native Select, Navigation Menu, Pagination,
Popover, Progress, Radio Group, Resizable, Scroll Area, Select,
Separator, Sheet, Sidebar, Skeleton, Sonner, Spinner, Switch,
Table, Tabs, Textarea, Toast, Toggle, Toggle Group, Tooltip, Typography
```

### Sync Strategy
```python
# Fetch from GitHub API
def sync_shadcn_components():
    url = "https://api.github.com/repos/shadcn-ui/ui/contents/apps/www/src/components/ui"
    # Parse each component .tsx file
```

---

## 3. Claude Cookbooks (AI Patterns)

### Overview
- **URL**: https://github.com/anthropics/claude-cookbooks
- **Stars**: 35.8k
- **Focus**: Claude/AI integration patterns

### Relevant Sections

| Category | Path | Purpose |
|----------|------|---------|
| Tool Use | tool_use/ | Integration patterns |
| Coding | coding/ | Code generation |
| Agents | patterns/agents/ | Agent patterns |
| Multimodal | multimodal/ | Vision capabilities |

### Key Files
- `coding/frontend/` - Frontend patterns
- `tool_use/customer_service_agent/` - Agent patterns
- `capabilities/classification/` - Classification

### Sync Strategy
```python
# Clone and parse notebooks
def sync_cookbook_patterns():
    # Extract prompt patterns from .ipynb files
    # Convert to p9i prompts
```

---

## 4. Context7 (Documentation)

### Overview
- **Integration**: Already in p9i via `context7_lookup`
- **Data**: Real-time docs for 500+ libraries
- **Use Case**: Get latest framework docs

### Available Libraries
```
React, Vue, Angular, Svelte, Next.js, Nuxt,
Tailwind CSS, Bootstrap, Material UI, Chakra UI,
FastAPI, Django, Flask, Express, NestJS,
Python, TypeScript, Go, Rust, and 500+ more
```

### Usage in p9i
```python
await context7_lookup('react', 'component patterns')
await context7_lookup('tailwind', 'utility classes')
```

### Enhancement: Add to UI/UX
```python
# In promt-ui-generator context
context7_lookup(target_framework, f"{component} best practices")
```

---

## 5. Primary Sources (Official)

### Design Systems

| Source | URL | Data |
|--------|-----|------|
| Apple HIG | developer.apple.com/design/human-interface-guidelines | iOS/macOS |
| Material Design | material.io/design | Android |
| Fluent UI | fluent2.microsoft.design | Microsoft |
| Tailwind | tailwindcss.com | CSS utilities |

### Framework Docs

| Framework | Docs URL |
|----------|----------|
| React | react.dev |
| Vue | vuejs.org/guide |
| Next.js | nextjs.org/docs |
| Flutter | docs.flutter.dev |

---

## Architecture: Multi-Source Integration

```
┌─────────────────────────────────────────────────────────┐
│                    p9i UI/UX Engine                  │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Intent       │  │ Designer     │  │ Context7 │ │
│  │ Router      │  │ Agent        │  │ Lookup   │ │
│  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘ │
│         │                  │                 │        │
│         ▼                  ▼                 ▼        │
│  ┌─────────────────────────────────────────────────┐│
│  │           UI/UX Resource Aggregator            ││
│  │  ┌─────────────┐ ┌────────────┐ ┌──────────┐ ││
│  │  │ui-ux-pro   │ │shadcn     │ │Cookbooks │ ││
│  │  │(styles,    │ │(components│ │(patterns)│ ││
│  │  │ colors)    │ │)          │ │          │ ││
│  │  └─────────────┘ └────────────┘ └──────────┘ ││
│  └─────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Request: "Create a login form in React"
              │
              ▼
┌─────────────────────────────────────────────┐
│  1. p9i_siri detects "designer" agent     │
│  2. Designer loads promt-ui-generator     │
│  3. Gather context:                        │
│     - search_styles("modern login")        │
│     - search_colors("auth blue")           │
│     - context7_lookup('react', 'form')     │
│     - shadcn_components('form')           │
│  4. Generate code with all context        │
└─────────────────────────────────────────────┘
```

---

## Implementation Priority

### Phase 1: Current (Done)
- [x] ui-ux-pro-mcp embedded data
- [x] BM25 search
- [x] MCP tools

### Phase 2: Sync (Next)
- [ ] CSV parser for ui-ux-pro-mcp
- [ ] Auto-sync from GitHub (weekly)
- [ ] Incremental updates

### Phase 3: Integration
- [ ] Context7 lookup in prompts
- [ ] shadcn components list
- [ ] Claude cookbook patterns

### Phase 4: Automation
- [ ] GitHub Action for sync
- [ ] Version tracking
- [ ] Diff notifications

---

## Sync Script Design

```python
# src/infrastructure/uiux/sync.py

import httpx
import csv
from io import StringIO
from pathlib import Path

class UIUXSync:
    """Sync UI/UX data from multiple sources."""

    SOURCES = {
        "uiux_pro": {
            "base": "https://raw.githubusercontent.com/redf0x1/ui-ux-pro-mcp/main/data",
            "files": ["styles.csv", "colors.csv", "typography.csv"],
        },
        "shadcn": {
            "api": "https://api.github.com/repos/shadcn-ui/ui/contents",
        },
    }

    async def sync_all(self):
        """Sync all sources."""
        await self.sync_uiux_pro()
        await self.sync_shadcn()

    async def sync_uiux_pro(self):
        """Sync from ui-ux-pro-mcp."""
        for filename in ["styles.csv", "colors.csv"]:
            url = f"{self.SOURCES['uiux_pro']['base']}/{filename}"
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                # Parse and update embedded.py

    async def sync_shadcn(self):
        """Sync shadcn components."""
        # Fetch component list from GitHub
```

---

## Verification Commands

```bash
# Test sources
python -c "
import asyncio
from src.infrastructure.uiux import get_search

search = get_search()

# Test each category
print('Styles:', len(search.search_styles('minimalism')))
print('Colors:', len(search.search_colors('fintech')))
print('Typography:', len(search.search_typography('modern')))
print('Stack:', len(search.search_stack('react')))
"
```

---

## Summary

| Source | Type | Format | Update Frequency |
|--------|------|--------|-----------------|
| ui-ux-pro-mcp | Design resources | CSV | Monthly |
| shadcn/ui | Components | GitHub API | Weekly |
| Claude Cookbooks | Patterns | Notebooks | On-demand |
| Context7 | Documentation | API | Real-time |
| Apple/Google/Fluent | Design Systems | Official docs | Quarterly |

**Recommended**: Start with CSV sync from ui-ux-pro-mcp, then integrate Context7 into prompts.
