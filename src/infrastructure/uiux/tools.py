# src/infrastructure/uiux/tools.py
"""
MCP tools for UI/UX design resources.

Provides search tools registered lazily.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Lazy registration flag
_uiux_tools_registered = False


def register_uiux_tools(mcp, search_instance=None):
    """
    Register UI/UX tools with MCP server.

    Uses lazy registration - only registers once.

    Args:
        mcp: FastMCP server instance
        search_instance: Optional BM25Search instance (for testing)
    """
    global _uiux_tools_registered

    if _uiux_tools_registered:
        logger.info("UI/UX tools already registered, skipping")
        return

    from .search import get_search, BM25Search

    search = search_instance or get_search()

    # ==================== Search Tools ====================

    @mcp.tool()
    async def search_ui_styles(
        query: str,
        max_results: int = 3
    ) -> dict:
        """
        Search UI design styles (Glassmorphism, Minimalism, Brutalism, etc.)

        Args:
            query: Natural language search query
            max_results: Maximum results to return (1-10)

        Returns:
            dict with results and metadata
        """
        try:
            results = search.search_styles(query, max_results=max_results)
            return {
                "status": "success",
                "query": query,
                "category": "styles",
                "total": len(results),
                "results": [r.to_dict() for r in results]
            }
        except Exception as e:
            logger.error(f"search_ui_styles error: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def search_colors(
        query: str,
        max_results: int = 3
    ) -> dict:
        """
        Search color palettes by industry or use case

        Args:
            query: Natural language query (e.g., "fintech", "dark mode", "healthcare")
            max_results: Maximum results to return (1-10)

        Returns:
            dict with color palettes
        """
        try:
            results = search.search_colors(query, max_results=max_results)
            return {
                "status": "success",
                "query": query,
                "category": "colors",
                "total": len(results),
                "results": [r.to_dict() for r in results]
            }
        except Exception as e:
            logger.error(f"search_colors error: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def search_typography(
        query: str,
        max_results: int = 3
    ) -> dict:
        """
        Search font pairings and typography recommendations

        Args:
            query: Natural language query (e.g., "modern sans", "editorial serif")
            max_results: Maximum results to return (1-10)

        Returns:
            dict with typography recommendations
        """
        try:
            results = search.search_typography(query, max_results=max_results)
            return {
                "status": "success",
                "query": query,
                "category": "typography",
                "total": len(results),
                "results": [r.to_dict() for r in results]
            }
        except Exception as e:
            logger.error(f"search_typography error: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def search_icons(
        query: str,
        max_results: int = 3
    ) -> dict:
        """
        Search icon sets and recommendations

        Args:
            query: Natural language query (e.g., "navigation", "settings")
            max_results: Maximum results to return (1-10)

        Returns:
            dict with icon recommendations
        """
        try:
            results = search.search_icons(query, max_results=max_results)
            return {
                "status": "success",
                "query": query,
                "category": "icons",
                "total": len(results),
                "results": [r.to_dict() for r in results]
            }
        except Exception as e:
            logger.error(f"search_icons error: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def search_ux_guidelines(
        query: str,
        max_results: int = 3
    ) -> dict:
        """
        Search UX best practices and guidelines

        Args:
            query: Natural language query (e.g., "accessibility", "mobile patterns")
            max_results: Maximum results to return (1-10)

        Returns:
            dict with UX guidelines
        """
        try:
            results = search.search_ux_guidelines(query, max_results=max_results)
            return {
                "status": "success",
                "query": query,
                "category": "ux_guidelines",
                "total": len(results),
                "results": [r.to_dict() for r in results]
            }
        except Exception as e:
            logger.error(f"search_ux_guidelines error: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def search_stack(
        query: str,
        stack_name: Optional[str] = None,
        max_results: int = 3
    ) -> dict:
        """
        Search framework-specific guidelines (React, Vue, Flutter, etc.)

        Args:
            query: Natural language query (e.g., "hooks", "composition API")
            stack_name: Framework name (react, vue, flutter, nextjs, etc.)
            max_results: Maximum results to return (1-10)

        Returns:
            dict with framework guidelines
        """
        try:
            results = search.search_stack(query, framework=stack_name, max_results=max_results)
            return {
                "status": "success",
                "query": query,
                "category": "stack",
                "framework": stack_name,
                "total": len(results),
                "results": [r.to_dict() for r in results]
            }
        except Exception as e:
            logger.error(f"search_stack error: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def search_all(
        query: str,
        max_results: int = 3
    ) -> dict:
        """
        Unified search across all UI/UX design domains

        Args:
            query: Natural language query
            max_results: Maximum results per category

        Returns:
            dict with results from all categories
        """
        try:
            # Search each category
            categories = ["styles", "colors", "typography", "icons", "ux_guidelines", "stack"]
            all_results = {}

            for cat in categories:
                results = search.search(query, category=cat, max_results=max_results)
                all_results[cat] = [r.to_dict() for r in results]

            total = sum(len(v) for v in all_results.values())

            return {
                "status": "success",
                "query": query,
                "total": total,
                "results": all_results
            }
        except Exception as e:
            logger.error(f"search_all error: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def get_design_system(
        mode: str = "light"
    ) -> dict:
        """
        Generate a complete design system with colors, typography, and style

        Args:
            mode: Color mode - "light" or "dark"

        Returns:
            dict with complete design system tokens
        """
        try:
            # Get colors for mode
            color_query = "dark mode" if mode == "dark" else "light"
            colors = search.search_colors(color_query, max_results=1)

            # Get typography
            typography = search.search_typography("modern", max_results=1)

            # Get styles
            style_query = "minimal" if mode == "light" else "glassmorphism"
            styles = search.search_styles(style_query, max_results=1)

            design_system = {
                "mode": mode,
                "colors": colors[0].to_dict() if colors else {},
                "typography": typography[0].to_dict() if typography else {},
                "style": styles[0].to_dict() if styles else {},
            }

            return {
                "status": "success",
                "design_system": design_system
            }
        except Exception as e:
            logger.error(f"get_design_system error: {e}")
            return {"status": "error", "error": str(e)}

    # Mark as registered
    _uiux_tools_registered = True
    logger.info("UI/UX tools registered successfully")
