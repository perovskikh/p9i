# src/infrastructure/uiux/context.py
"""
UI/UX Context Builder

Builds context for UI/UX generation by:
1. Detecting UI/UX intent in user requests
2. Searching relevant design resources
3. Integrating Context7 documentation
"""

import logging
import re
from typing import Dict, Any, Optional, List

from .search import get_search

logger = logging.getLogger(__name__)

# Keywords that trigger UI/UX context
UIUX_KEYWORDS = [
    # English
    "ui", "ux", "design", "button", "card", "component", "form", "input",
    "color", "palette", "typography", "font", "icon", "layout", "responsive",
    "accessibility", "a11y", "style", "theme", "dark mode", "light mode",
    "glassmorphism", "minimalism", "neumorphism", "brutalism",
    # Russian
    "дизайн", "интерфейс", "компонент", "кнопка", "карточка", "форма",
    "цвет", "палитра", "шрифт", "иконка", "верстка", "стиль", "тема",
]

# Framework detection patterns
FRAMEWORK_PATTERNS = {
    "react": [r"react", r"jsx", r"tsx", r"next\.?js", r"next\.?js"],
    "vue": [r"vue", r"nuxt"],
    "flutter": [r"flutter", r"dart"],
    "svelte": [r"svelte"],
    "angular": [r"angular"],
    "tailwind": [r"tailwind", r"tw"],
    "bootstrap": [r"bootstrap"],
    "mui": [r"material", r"mui"],
}


class UIUXContextBuilder:
    """Builds UI/UX context for prompt execution."""

    def __init__(self):
        self.search = get_search()

    def detect_uiux_intent(self, task: str) -> bool:
        """Check if task contains UI/UX related content."""
        task_lower = task.lower()
        return any(kw in task_lower for kw in UIUX_KEYWORDS)

    def detect_framework(self, task: str) -> Optional[str]:
        """Detect the target framework from task."""
        task_lower = task.lower()
        for framework, patterns in FRAMEWORK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, task_lower):
                    return framework
        return None

    def extract_design_terms(self, task: str) -> List[str]:
        """Extract design-related terms from task."""
        terms = []
        task_lower = task.lower()

        # Style-related terms
        styles = ["glassmorphism", "minimalism", "neumorphism", "brutalism",
                  "flat", "material", "skeuomorphic", "bento"]
        for s in styles:
            if s in task_lower:
                terms.append(s)

        # Color-related terms
        colors = ["dark mode", "dark", "light", "pastel", "neon", "gradient"]
        for c in colors:
            if c in task_lower:
                terms.append(c)

        # Component-related
        components = ["button", "card", "form", "input", "modal", "dropdown",
                      "navbar", "sidebar", "table", "chart"]
        for comp in components:
            if comp in task_lower:
                terms.append(comp)

        return terms

    async def build_context(self, task: str) -> Dict[str, Any]:
        """
        Build UI/UX context from task.

        Returns dict with design resources and metadata.
        """
        if not self.detect_uiux_intent(task):
            return {"enabled": False}

        context = {
            "enabled": True,
            "framework": self.detect_framework(task),
            "design_terms": self.extract_design_terms(task),
        }

        # Search for relevant resources
        try:
            # Search styles
            styles = self.search.search_styles(task, max_results=3)
            context["styles"] = [s.to_dict() for s in styles]

            # Search colors
            colors = self.search.search_colors(task, max_results=3)
            context["colors"] = [c.to_dict() for c in colors]

            # Search typography
            typography = self.search.search_typography(task, max_results=2)
            context["typography"] = [t.to_dict() for t in typography]

            # Search icons
            icons = self.search.search_icons(task, max_results=5)
            context["icons"] = [i.to_dict() for i in icons]

            # If framework detected, get stack guidelines + Context7 docs
            if context["framework"]:
                stack = self.search.search_stack(
                    task,
                    framework=context["framework"],
                    max_results=2
                )
                context["stack"] = [s.to_dict() for s in stack]

                # Query Context7 for framework docs
                context["context7_docs"] = await self._query_context7(
                    context["framework"],
                    task
                )

            logger.info(f"UI/UX context built: {len(styles)} styles, {len(colors)} colors")

        except Exception as e:
            logger.error(f"Error building UI/UX context: {e}")
            context["error"] = str(e)

        return context

    async def _query_context7(self, framework: str, task: str) -> Optional[Dict[str, Any]]:
        """Query Context7 for framework documentation."""
        try:
            # Import Context7 lookup from server
            from src.api.server import context7_lookup, _context7_query_docs

            # Map framework to Context7 library
            library_map = {
                "react": "react",
                "vue": "vue",
                "next": "next.js",
                "tailwind": "tailwindcss",
                "bootstrap": "bootstrap",
                "mui": "material-ui",
                "svelte": "svelte",
                "angular": "angular",
            }

            library = library_map.get(framework.lower())
            if not library:
                return None

            # Determine query based on task
            query = "component patterns best practices"
            if "button" in task.lower():
                query = "button component patterns"
            elif "form" in task.lower():
                query = "form validation patterns"
            elif "card" in task.lower():
                query = "card component patterns"
            elif "modal" in task.lower() or "dialog" in task.lower():
                query = "modal dialog patterns"

            # Get library ID
            lookup_result = context7_lookup(library, query)
            library_id = lookup_result.get("context7_id")

            if library_id:
                # Query docs
                docs_result = await _context7_query_docs(library_id, query)
                return {
                    "library": library,
                    "library_id": library_id,
                    "query": query,
                    "result": docs_result
                }

        except Exception as e:
            logger.warning(f"Context7 query failed: {e}")

        return None

    def format_for_prompt(self, context: Dict[str, Any]) -> str:
        """Format context as a string for prompt injection."""
        if not context.get("enabled"):
            return ""

        lines = ["\n## UI/UX Design Context\n"]

        # Framework
        if context.get("framework"):
            lines.append(f"**Framework**: {context['framework'].upper()}")

        # Context7 Documentation
        if context.get("context7_docs"):
            docs = context["context7_docs"]
            result = docs.get("result", {})
            if result.get("status") == "success":
                content = result.get("content", "")
                if content:
                    lines.append(f"\n### {docs.get('library', '').upper()} Docs")
                    # Truncate to first 500 chars
                    lines.append(content[:500])

        # Colors
        if context.get("colors"):
            lines.append("\n### Color Palette")
            for color in context["colors"][:2]:
                data = color.get("data", {})
                lines.append(f"- **{color['name']}**: {data.get('primary', 'N/A')}")

        # Styles
        if context.get("styles"):
            lines.append("\n### Design Styles")
            for style in context["styles"][:2]:
                lines.append(f"- **{style['name']}**: {style.get('description', '')[:100]}")

        # Typography
        if context.get("typography"):
            lines.append("\n### Typography")
            for typo in context["typography"][:1]:
                data = typo.get("data", {})
                lines.append(f"- **{typo['name']}**: {data.get('heading', '')} + {data.get('body', '')}")

        # Icons
        if context.get("icons"):
            lines.append("\n### Icons")
            for icon in context["icons"][:3]:
                data = icon.get("data", {})
                lines.append(f"- {icon['name']}: `{data.get('import', '')}`")

        return "\n".join(lines)


# Singleton instance
_uiux_context: Optional[UIUXContextBuilder] = None


def get_uiux_context() -> UIUXContextBuilder:
    """Get UI/UX context builder singleton."""
    global _uiux_context
    if _uiux_context is None:
        _uiux_context = UIUXContextBuilder()
    return _uiux_context