#!/usr/bin/env python3
"""
Simple sync for UI/UX data without external dependencies.
Uses subprocess to call curl for fetching CSV files.

Usage:
    python3 sync_local.py --category colors
    python3 sync_local.py --all
"""

import argparse
import csv
import json
import logging
import subprocess
import sys
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Source URLs
BASE_URL = "https://raw.githubusercontent.com/redf0x1/ui-ux-pro-mcp/main/data"

SOURCES = {
    "styles": f"{BASE_URL}/styles.csv",
    "colors": f"{BASE_URL}/colors.csv",
    "typography": f"{BASE_URL}/typography.csv",
    "icons": f"{BASE_URL}/icons.csv",
    "ux_guidelines": f"{BASE_URL}/ux_guidelines.csv",
}


def fetch_csv(url: str) -> str:
    """Fetch CSV using curl."""
    result = subprocess.run(
        ["curl", "-s", url],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout


def parse_colors_csv(content: str) -> List[Dict[str, Any]]:
    """Parse colors.csv with industry palettes."""
    reader = csv.DictReader(StringIO(content))
    results = []

    for row in reader:
        if not row.get("No"):
            continue

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
            },
            "tags": [k.strip().lower() for k in row.get("Keywords", "").split(",") if k.strip()][:10],
        }
        results.append(item)

    logger.info(f"Parsed {len(results)} color palettes")
    return results


def parse_styles_csv(content: str) -> List[Dict[str, Any]]:
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
                "css_code": row.get("CSS_Code", "").strip()[:500],  # Limit size
                "motion_config": row.get("Motion_Config", "").strip(),
                "framework_compatibility": row.get("Framework Compatibility", "").strip(),
                "performance": row.get("Performance", "").strip(),
            },
            "tags": [k.strip() for k in row.get("Keywords", "").split(",") if k.strip()][:10],
        }
        results.append(item)

    logger.info(f"Parsed {len(results)} styles")
    return results


def generate_embedded(data: Dict[str, List[Dict[str, Any]]]) -> str:
    """Generate embedded.py content."""
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
        lines.append(f"# {category.replace('_', ' ').title()} ({len(items)}) - Auto-synced")
        lines.append(f"{var_name} = [")

        for item in items:
            lines.append("    {")
            lines.append(f'        "id": "{item.get("id", "")}",')
            name = item.get("name", "").replace('"', '\\"')
            lines.append(f'        "name": "{name}",')
            desc = item.get("description", "").replace('"', '\\"').replace('\n', ' ')
            lines.append(f'        "description": "{desc}",')
            # Data as repr for simplicity
            lines.append(f'        "data": {repr(item.get("data", {}))},')
            lines.append(f'        "tags": {repr(item.get("tags", []))},')
            lines.append("    },")

        lines.append("]")
        lines.append("")

    lines.append("UIUX_EMBEDDED_DATA = {")
    for category in data:
        var_name = f"UIUX_{category.upper()}"
        lines.append(f'    "{category}": {var_name},')
    lines.append("}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Sync UI/UX data from remote sources")
    parser.add_argument(
        "--category", "-c",
        choices=["styles", "colors", "typography", "icons", "ux_guidelines", "all"],
        default="all",
        help="Category to sync"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be synced without writing"
    )
    args = parser.parse_args()

    data = {}

    if args.category == "all":
        categories = ["styles", "colors"]
    else:
        categories = [args.category]

    for cat in categories:
        if cat not in SOURCES:
            logger.warning(f"Skipping unknown category: {cat}")
            continue

        logger.info(f"Fetching {cat}...")
        url = SOURCES[cat]
        content = fetch_csv(url)

        if cat == "colors":
            data[cat] = parse_colors_csv(content)
        elif cat == "styles":
            data[cat] = parse_styles_csv(content)
        else:
            logger.info(f"Parser not implemented for {cat}")
            data[cat] = []

    # Generate code
    embedded_code = generate_embedded(data)

    if args.dry_run:
        logger.info("\n=== Dry Run ===")
        logger.info(embedded_code[:3000])
        logger.info("...")
        return

    # Write to file
    output_path = Path(__file__).parent / "data" / "embedded.py"
    output_path.write_text(embedded_code)
    logger.info(f"Written to {output_path}")

    # Also save JSON
    json_path = output_path.with_suffix(".json")
    json_path.write_text(json.dumps(data, indent=2))
    logger.info(f"Backup saved to {json_path}")


if __name__ == "__main__":
    main()