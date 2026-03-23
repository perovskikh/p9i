# src/infrastructure/uiux/__init__.py
"""
UI/UX Design Resources Module.

Provides 1920+ curated design resources for UI/UX generation:
- Styles (Glassmorphism, Minimalism, etc.)
- Colors (Industry palettes)
- Typography (Font pairings)
- Icons (Lucide)
- UX Guidelines (WCAG, best practices)
- Framework Guidelines (React, Vue, Flutter, etc.)

Usage:
    from src.infrastructure.uiux import register_uiux_tools

    # In server.py:
    register_uiux_tools(mcp)
"""

from .resources import (
    UIUXCategory,
    FrameworkStack,
    UIUXResource,
    DesignStyle,
    ColorPalette,
    TypographyPair,
    IconSet,
    UXGuideline,
    FrameworkGuideline,
)

from .loader import UIUXLoader, get_loader
from .search import BM25Search, get_search
from .tools import register_uiux_tools

__all__ = [
    # Resources
    "UIUXCategory",
    "FrameworkStack",
    "UIUXResource",
    "DesignStyle",
    "ColorPalette",
    "TypographyPair",
    "IconSet",
    "UXGuideline",
    "FrameworkGuideline",
    # Loading
    "UIUXLoader",
    "get_loader",
    # Search
    "BM25Search",
    "get_search",
    # Tools
    "register_uiux_tools",
]
