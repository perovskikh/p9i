# src/infrastructure/uiux/resources.py
"""
UI/UX Resource models and enums.

Provides data structures for 1920+ design resources.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class UIUXCategory(str, Enum):
    """UI/UX resource categories."""
    STYLES = "styles"
    COLORS = "colors"
    TYPOGRAPHY = "typography"
    ICONS = "icons"
    CHARTS = "charts"
    UX_GUIDELINES = "ux_guidelines"
    LANDING = "landing"
    PRODUCTS = "products"
    PROMPTS = "prompts"
    STACK = "stack"


class FrameworkStack(str, Enum):
    """Supported framework stacks."""
    REACT = "react"
    VUE = "vue"
    NEXTJS = "nextjs"
    NUXTJS = "nuxtjs"
    FLUTTER = "flutter"
    REACT_NATIVE = "react-native"
    SWIFTUI = "swiftui"
    JETPACK_COMPOSE = "jetpack-compose"
    HTML_TAILWIND = "html-tailwind"
    SHADCN = "shadcn"
    SVELTE = "svelte"
    NUXT_UI = "nuxt-ui"


@dataclass
class UIUXResource:
    """UI/UX design resource."""
    id: str
    category: UIUXCategory
    name: str
    description: str
    data: Dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "category": self.category.value,
            "name": self.name,
            "description": self.description,
            "data": self.data,
            "score": self.score,
            "tags": self.tags,
        }


@dataclass
class DesignStyle(UIUXResource):
    """UI design style (Glassmorphism, Minimalism, etc.)."""
    def __init__(self, id: str, name: str, description: str, **kwargs):
        super().__init__(
            id=id,
            category=UIUXCategory.STYLES,
            name=name,
            description=description,
            **kwargs
        )


@dataclass
class ColorPalette(UIUXResource):
    """Color palette for industry/use case."""
    def __init__(self, id: str, name: str, description: str, **kwargs):
        super().__init__(
            id=id,
            category=UIUXCategory.COLORS,
            name=name,
            description=description,
            **kwargs
        )


@dataclass
class TypographyPair(UIUXResource):
    """Font pairing with configs."""
    def __init__(self, id: str, name: str, description: str, **kwargs):
        super().__init__(
            id=id,
            category=UIUXCategory.TYPOGRAPHY,
            name=name,
            description=description,
            **kwargs
        )


@dataclass
class IconSet(UIUXResource):
    """Icon set with imports."""
    def __init__(self, id: str, name: str, description: str, **kwargs):
        super().__init__(
            id=id,
            category=UIUXCategory.ICONS,
            name=name,
            description=description,
            **kwargs
        )


@dataclass
class UXGuideline(UIUXResource):
    """UX best practice or guideline."""
    def __init__(self, id: str, name: str, description: str, **kwargs):
        super().__init__(
            id=id,
            category=UIUXCategory.UX_GUIDELINES,
            name=name,
            description=description,
            **kwargs
        )


@dataclass
class FrameworkGuideline(UIUXResource):
    """Framework-specific guideline."""
    def __init__(self, id: str, name: str, framework: FrameworkStack, description: str, **kwargs):
        super().__init__(
            id=id,
            category=UIUXCategory.STACK,
            name=name,
            description=description,
            **kwargs
        )
        self.framework = framework
