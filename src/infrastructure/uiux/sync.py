# src/infrastructure/uiux/sync.py
"""
Sync UI/UX data from remote sources.

Fetches and parses design resources from:
- ui-ux-pro-mcp (CSV files)
- Updates embedded.py with new data

Usage:
    python -m src.infrastructure.uiux.sync --category styles
    python -m src.infrastructure.uiux.sync --all
"""

import argparse
import asyncio
import csv
import json
import logging
import os
import sys
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Source URLs
UIUX_PRO_BASE = "https://raw.githubusercontent.com/redf0x1/ui-ux-pro-mcp/main/data"

SOURCES = {
    "styles": f"{UIUX_PRO_BASE}/styles.csv",
    "colors": f"{UIUX_PRO_BASE}/colors.csv",
    "typography": f"{UIUX_PRO_BASE}/typography.csv",
    "icons": f"{UIUX_PRO_BASE}/icons.csv",
    "ux_guidelines": f"{UIUX_PRO_BASE}/ux_guidelines.csv",
}


class UIUXSync:
    """Sync UI/UX data from remote sources."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path(__file__).parent / "data"
        self.http_client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.http_client:
            await self.http_client.aclose()

    async def fetch_csv(self, url: str) -> str:
        """Fetch CSV content from URL."""
        if not self.http_client:
            raise RuntimeError("Use async context manager")

        logger.info(f"Fetching: {url}")
        response = await self.http_client.get(url)
        response.raise_for_status()
        return response.text

    def parse_styles_csv(self, content: str) -> List[Dict[str, Any]]:
        """Parse styles.csv with rich UI style data."""
        reader = csv.DictReader(StringIO(content))
        results = []

        for row in reader:
            if not row.get("STT"):
                continue

            item = {
                "id": f"style-{row.get('STT', '')}",
                "name": row.get("Style Category", "").strip(),
                "description": f"{row.get('Type', '')} - Keywords: {row.get('Keywords', '')}",
                "data": {
                    "primary_colors": row.get("Primary Colors", "").strip(),
                    "secondary_colors": row.get("Secondary Colors", "").strip(),
                    "effects": row.get("Effects & Animation", "").strip(),
                    "best_for": row.get("Best For", "").strip(),
                    "do_not_use_for": row.get("Do Not Use For", "").strip(),
                    "css_code": row.get("CSS_Code", "").strip(),
                    "motion_config": row.get("Motion_Config", "").strip(),
                    "framework_compatibility": row.get("Framework Compatibility", "").strip(),
                    "performance": row.get("Performance", "").strip(),
                    "accessibility": row.get("Accessibility", "").strip(),
                    "mobile_friendly": row.get("Mobile-Friendly", "").strip(),
                },
                "tags": [k.strip() for k in row.get("Keywords", "").split(",") if k.strip()][:10],
            }
            results.append(item)

        logger.info(f"Parsed {len(results)} styles")
        return results

    def parse_colors_csv(self, content: str) -> List[Dict[str, Any]]:
        """Parse colors.csv with industry palettes."""
        reader = csv.DictReader(StringIO(content))
        results = []

        for row in reader:
            # Column names from actual CSV
            if not row.get("No"):
                continue

            # Extract hex colors from palette
            primary = row.get("Primary (Hex)", "").strip()
            secondary = row.get("Secondary (Hex)", "").strip()
            accent = row.get("CTA (Hex)", "").strip()

            item = {
                "id": f"color-{row.get('No', '')}",
                "name": row.get("Product Type", "").strip(),
                "description": f"{row.get('Keywords', '')} - {row.get('Notes', '')}",
                "data": {
                    "primary": primary,
                    "secondary": secondary,
                    "accent": accent,
                    "background": row.get("Background (Hex)", "").strip(),
                    "text": row.get("Text (Hex)", "").strip(),
                    "border": row.get("Border (Hex)", "").strip(),
                    "tailwind_config": row.get("Tailwind_Config", "").strip(),
                    "dark_mode": row.get("Dark_Mode_Colors", "").strip(),
                    "semantic_tokens": row.get("Semantic_Tokens", "").strip(),
                },
                "tags": [k.strip().lower() for k in row.get("Keywords", "").split(",") if k.strip()][:10],
            }
            results.append(item)

        logger.info(f"Parsed {len(results)} color palettes")
        return results

    def parse_typography_csv(self, content: str) -> List[Dict[str, Any]]:
        """Parse typography.csv with font pairings."""
        reader = csv.DictReader(StringIO(content))
        results = []

        for row in reader:
            if not row.get("STT"):
                continue

            item = {
                "id": f"typo-{row.get('STT', '')}",
                "name": f"{row.get('Heading Font', '').strip()} + {row.get('Body Font', '').strip()}",
                "description": f"{row.get('Use Case', '')} - {row.get('Personality', '')}",
                "data": {
                    "heading": row.get("Heading Font", "").strip(),
                    "body": row.get("Body Font", "").strip(),
                    "mono": row.get("Monospace Font", "").strip(),
                    "google_fonts": row.get("Google Fonts Link", "").strip(),
                    "personality": row.get("Personality", "").strip(),
                    "use_case": row.get("Use Case", "").strip(),
                },
                "tags": [
                    row.get("Classification", "").strip().lower(),
                    row.get("Personality", "").strip().lower(),
                ],
            }
            results.append(item)

        logger.info(f"Parsed {len(results)} typography pairings")
        return results

    def parse_icons_csv(self, content: str) -> List[Dict[str, Any]]:
        """Parse icons.csv with Lucide icons."""
        reader = csv.DictReader(StringIO(content))
        results = []

        for row in reader:
            if not row.get("STT"):
                continue

            item = {
                "id": f"icon-{row.get('STT', '')}",
                "name": row.get("Icon Name", "").strip(),
                "description": f"{row.get('Category', '')} - {row.get('Description', '')}",
                "data": {
                    "import": f"import {{ {row.get('Icon Name', '').strip()} }} from 'lucide-react'",
                    "component": f"<{row.get('Icon Name', '').strip()} />",
                    "category": row.get("Category", "").strip(),
                    "style": row.get("Style", "").strip(),
                },
                "tags": [
                    row.get("Category", "").strip().lower(),
                    row.get("Icon Name", "").strip().lower(),
                ],
            }
            results.append(item)

        logger.info(f"Parsed {len(results)} icons")
        return results

    def parse_ux_guidelines_csv(self, content: str) -> List[Dict[str, Any]]:
        """Parse ux_guidelines.csv."""
        reader = csv.DictReader(StringIO(content))
        results = []

        for row in reader:
            if not row.get("STT"):
                continue

            item = {
                "id": f"ux-{row.get('STT', '')}",
                "name": row.get("Guideline Category", "").strip(),
                "description": f"{row.get('Type', '')} - {row.get('Key Points', '')}",
                "data": {
                    "category": row.get("Guideline Category", "").strip(),
                    "type": row.get("Type", "").strip(),
                    "key_points": row.get("Key Points", "").strip(),
                    "best_practices": row.get("Best Practices", "").strip(),
                    "wcag_reference": row.get("WCAG Reference", "").strip(),
                },
                "tags": [
                    row.get("Guideline Category", "").strip().lower(),
                    row.get("Type", "").strip().lower(),
                ],
            }
            results.append(item)

        logger.info(f"Parsed {len(results)} UX guidelines")
        return results

    async def sync_category(self, category: str) -> List[Dict[str, Any]]:
        """Sync a single category from remote source."""
        if category not in SOURCES:
            raise ValueError(f"Unknown category: {category}. Available: {list(SOURCES.keys())}")

        url = SOURCES[category]
        content = await self.fetch_csv(url)

        # Parse based on category
        parser_method = f"parse_{category}_csv"
        if hasattr(self, parser_method):
            return getattr(self, parser_method)(content)
        else:
            logger.warning(f"No parser for {category}, using generic parsing")
            return self._parse_generic_csv(content, category)

    def _parse_generic_csv(self, content: str, category: str) -> List[Dict[str, Any]]:
        """Generic CSV parser fallback."""
        reader = csv.DictReader(StringIO(content))
        results = []
        for i, row in enumerate(reader):
            results.append({
                "id": f"{category}-{i}",
                "name": row.get("Name", row.get("Category", f"Item {i}")),
                "description": row.get("Description", ""),
                "data": dict(row),
                "tags": [],
            })
        return results

    async def sync_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Sync all categories."""
        results = {}
        for category in SOURCES:
            try:
                results[category] = await self.sync_category(category)
            except Exception as e:
                logger.error(f"Failed to sync {category}: {e}")
                results[category] = []
        return results

    def generate_embedded_py(self, data: Dict[str, List[Dict[str, Any]]]) -> str:
        """Generate embedded.py content from synced data."""
        lines = [
            "# src/infrastructure/uiux/data/embedded.py",
            '"""',
            "Embedded UI/UX design resources.",
            "",
            f"Auto-synced from ui-ux-pro-mcp ({len(data.get('styles', []))} styles, ",
                f"{len(data.get('colors', []))} colors, etc.)",
            '"""',
            "",
        ]

        for category, items in data.items():
            var_name = f"UIUX_{category.upper()}"
            lines.append(f"# {category.replace('_', ' ').title()} ({len(items)})")
            lines.append(f"{var_name} = [")

            for item in items:
                lines.append("    {")
                lines.append(f'        "id": "{item.get("id", "")}",')
                lines.append(f'        "name": """{item.get("name", "").replace("\"", "\"\"")}""",')
                desc = item.get("description", "").replace("\"", "\"").replace("\n", " ")
                lines.append(f'        "description": """{desc}""",')
                lines.append(f'        "data": {json.dumps(item.get("data", {}), ensure_ascii=False)},')
                lines.append(f'        "tags": {json.dumps(item.get("tags", []))},')
                lines.append("    },")

            lines.append("]")
            lines.append("")

        # Add final dict
        lines.append("UIUX_EMBEDDED_DATA = {")
        for category in data:
            var_name = f"UIUX_{category.upper()}"
            lines.append(f'    "{category}": {var_name},')
        lines.append("}")

        return "\n".join(lines)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Sync UI/UX data from remote sources")
    parser.add_argument(
        "--category", "-c",
        choices=["styles", "colors", "typography", "icons", "ux_guidelines", "all"],
        default="all",
        help="Category to sync"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file path (default: update embedded.py)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be synced without writing"
    )

    args = parser.parse_args()

    async with UIUXSync() as sync:
        if args.category == "all":
            data = await sync.sync_all()
        else:
            data = {args.category: await sync.sync_category(args.category)}

        # Generate Python code
        embedded_code = sync.generate_embedded_py(data)

        if args.dry_run:
            print("=== Dry Run - Would generate ===")
            print(embedded_code[:2000])
            print("...")
            return

        # Write to file
        output_path = args.output or Path(__file__).parent / "data" / "embedded.py"
        output_path.write_text(embedded_code)
        logger.info(f"Written to {output_path}")

        # Also save JSON backup
        json_path = output_path.with_suffix(".json")
        json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        logger.info(f"Backup saved to {json_path}")


if __name__ == "__main__":
    asyncio.run(main())