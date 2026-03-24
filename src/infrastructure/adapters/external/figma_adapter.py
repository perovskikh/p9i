# src/services/figma.py
"""
Figma API Integration Service

Provides integration with Figma REST API for:
- Reading file structure
- Extracting components
- Getting design tokens (colors, typography)
- Exporting nodes to images
"""

import os
import httpx
import logging
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)

FIGMA_API_BASE = "https://api.figma.com/v1"


class FigmaClient:
    """Figma API client."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("FIGMA_TOKEN")
        self.client = httpx.AsyncClient(
            headers={
                "X-Figma-Token": self.token
            } if self.token else {}
        )

    async def close(self):
        await self.client.aclose()

    async def get_file(self, file_key: str) -> Dict[str, Any]:
        """
        Get full file data from Figma.

        Args:
            file_key: Figma file key (from URL: figma.com/file/FILE_KEY/...)

        Returns:
            dict: File JSON structure
        """
        if not self.token:
            raise ValueError("FIGMA_TOKEN not set")

        response = await self.client.get(f"{FIGMA_API_BASE}/files/{file_key}")
        response.raise_for_status()
        return response.json()

    async def get_file_styles(self, file_key: str) -> Dict[str, Any]:
        """
        Get all styles (colors, typography, effects) from file.

        Args:
            file_key: Figma file key

        Returns:
            dict: Styles metadata
        """
        if not self.token:
            raise ValueError("FIGMA_TOKEN not set")

        # First get the file to find style IDs
        file_data = await self.get_file(file_key)

        styles = {
            "colors": [],
            "typography": [],
            "effects": []
        }

        # Extract styles from metadata
        meta = file_data.get("metadata", {})
        if "styles" in meta:
            for style in meta["styles"]:
                style_type = style.get("style_type", "")
                if style_type == "FILL":
                    styles["colors"].append({
                        "key": style.get("key"),
                        "name": style.get("name"),
                        "description": style.get("description", "")
                    })
                elif style_type == "TEXT":
                    styles["typography"].append({
                        "key": style.get("key"),
                        "name": style.get("name"),
                        "description": style.get("description", "")
                    })
                elif style_type == "EFFECT":
                    styles["effects"].append({
                        "key": style.get("key"),
                        "name": style.get("name"),
                        "description": style.get("description", "")
                    })

        # Also try to get styles from the file's styles property
        file_styles = file_data.get("styles", {})
        for style_key, style_val in file_styles.items():
            style_type = style_val.get("style_type", "")
            if style_type == "FILL":
                styles["colors"].append({
                    "key": style_key,
                    "name": style_val.get("name"),
                    "description": style_val.get("description", "")
                })
            elif style_type == "TEXT":
                styles["typography"].append({
                    "key": style_key,
                    "name": style_val.get("name"),
                    "description": style_val.get("description", "")
                })

        return styles

    async def get_file_components(self, file_key: str) -> Dict[str, Any]:
        """
        Get all components from file.

        Args:
            file_key: Figma file key

        Returns:
            dict: Components metadata
        """
        if not self.token:
            raise ValueError("FIGMA_TOKEN not set")

        file_data = await self.get_file(file_key)

        components = []
        meta = file_data.get("metadata", {})

        # Get components from metadata
        if "components" in meta:
            for comp in meta["components"]:
                components.append({
                    "key": comp.get("key"),
                    "name": comp.get("name"),
                    "description": comp.get("description", ""),
                    "componentSetId": comp.get("componentSetId", "")
                })

        # Also try from file's components property
        file_components = file_data.get("components", {})
        for comp_key, comp_val in file_components.items():
            components.append({
                "key": comp_key,
                "name": comp_val.get("name"),
                "description": comp_val.get("description", ""),
                "componentSetId": comp_val.get("componentSetId", "")
            })

        return {
            "components": components,
            "total": len(components)
        }

    async def get_node(self, file_key: str, node_ids: List[str]) -> Dict[str, Any]:
        """
        Get specific nodes from file.

        Args:
            file_key: Figma file key
            node_ids: List of node IDs to fetch

        Returns:
            dict: Node data
        """
        if not self.token:
            raise ValueError("FIGMA_TOKEN not set")

        ids = ",".join(node_ids)
        response = await self.client.get(
            f"{FIGMA_API_BASE}/files/{file_key}/nodes",
            params={"ids": ids}
        )
        response.raise_for_status()
        return response.json()

    async def export_images(
        self,
        file_key: str,
        node_ids: List[str],
        format: str = "png",
        scale: float = 2.0
    ) -> Dict[str, Any]:
        """
        Export nodes as images.

        Args:
            file_key: Figma file key
            node_ids: List of node IDs to export
            format: Output format (png, jpg, svg, pdf)
            scale: Scale factor (1, 2, 3, 4)

        Returns:
            dict: URLs of exported images
        """
        if not self.token:
            raise ValueError("FIGMA_TOKEN not set")

        ids = ",".join(node_ids)
        response = await self.client.get(
            f"{FIGMA_API_BASE}/images/{file_key}",
            params={
                "ids": ids,
                "format": format,
                "scale": scale
            }
        )
        response.raise_for_status()
        return response.json()

    async def get_color_styles(self, file_key: str) -> List[Dict[str, Any]]:
        """
        Get color styles as hex values.

        Args:
            file_key: Figma file key

        Returns:
            list: Color palette with hex values
        """
        if not self.token:
            raise ValueError("FIGMA_TOKEN not set")

        # Get file with all properties to find color values
        response = await self.client.get(
            f"{FIGMA_API_BASE}/files/{file_key}",
            params={"properties": "styles"}
        )
        response.raise_for_status()
        data = response.json()

        colors = []

        # Try to extract colors from the document
        doc = data.get("document", {})

        def extract_colors_from_node(node):
            """Recursively extract color styles from nodes."""
            fills = node.get("fills", [])
            for fill in fills:
                if fill.get("type") == "SOLID":
                    color = fill.get("color", {})
                    r = color.get("r", 0)
                    g = color.get("g", 0)
                    b = color.get("b", 0)
                    a = color.get("a", 1)

                    hex_color = "#{:02x}{:02x}{:02x}".format(
                        int(r * 255),
                        int(g * 255),
                        int(b * 255)
                    )

                    colors.append({
                        "hex": hex_color,
                        "rgba": f"rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, {a})",
                        "name": node.get("name", "unnamed")
                    })

            # Recurse into children
            for child in node.get("children", []):
                extract_colors_from_node(child)

        extract_colors_from_node(doc)

        # Deduplicate by hex
        seen = set()
        unique_colors = []
        for color in colors:
            if color["hex"] not in seen:
                seen.add(color["hex"])
                unique_colors.append(color)

        return unique_colors


# Global client instance
_figma_client: Optional[FigmaClient] = None


async def get_figma_client() -> FigmaClient:
    """Get or create Figma client."""
    global _figma_client
    if _figma_client is None:
        _figma_client = FigmaClient()
    return _figma_client


async def close_figma_client():
    """Close Figma client."""
    global _figma_client
    if _figma_client:
        await _figma_client.close()
        _figma_client = None
