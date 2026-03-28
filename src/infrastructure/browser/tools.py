# src/infrastructure/browser/tools.py
"""Browser automation tools for MCP server using Playwright."""

import os
import asyncio
from typing import Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Global browser state
_browser = None
_playwright = None
_context = None

# Lazy registration flag
_browser_tools_registered = False

# Configuration from environment
HEADLESS = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30000"))
VIEWPORT_WIDTH = int(os.getenv("BROWSER_VIEWPORT_WIDTH", "1280"))
VIEWPORT_HEIGHT = int(os.getenv("BROWSER_VIEWPORT_HEIGHT", "720"))


def is_playwright_available() -> bool:
    """Check if playwright is installed."""
    try:
        import playwright
        return True
    except ImportError:
        return False


async def init_browser():
    """Initialize browser eagerly."""
    global _browser, _playwright, _context

    if _browser is not None:
        return

    if not is_playwright_available():
        raise ImportError(
            "playwright not installed. Install with: pip install playwright && playwright install chromium"
        )

    try:
        from playwright.async_api import async_playwright
        pw = await async_playwright().start()
        _playwright = pw
        _browser = await pw.chromium.launch(headless=HEADLESS)
        _context = await _browser.new_context(
            viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT}
        )
        logger.info("Browser initialized successfully")
    except Exception as e:
        logger.error(f"Browser init failed: {e}")
        _browser = _playwright = _context = None
        raise


async def get_page():
    """Get or create page."""
    if _browser is None:
        await init_browser()

    if not _context.pages:
        return await _context.new_page()
    return _context.pages[0]


def register_browser_tools(mcp):
    """Register browser automation tools with MCP server."""

    global _browser_tools_registered

    if _browser_tools_registered:
        logger.info("Browser tools already registered, skipping")
        return

    # Check if playwright is available
    if not is_playwright_available():
        logger.warning("playwright not installed - browser tools will not be available")
        # Still register the tools, but they'll return error messages
        _browser_tools_registered = True
        return

    _browser_tools_registered = True

    # Initialize browser on startup
    @mcp.tool()
    async def browser_status():
        """Get browser status."""
        return {
            "status": "running" if _browser else "stopped",
            "headless": HEADLESS,
            "viewport": {"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
            "timeout": TIMEOUT
        }

    @mcp.tool()
    async def browser_init():
        """Initialize browser (call first)."""
        try:
            await init_browser()
            return {"status": "success", "message": "Browser initialized"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def browser_navigate(url: str) -> dict:
        """Navigate to a URL in the browser."""
        try:
            await init_browser()  # Ensure browser is initialized
            page = await get_page()
            response = await page.goto(url, timeout=TIMEOUT)
            title = await page.title()
            return {"status": "success", "url": url, "title": title, "status_code": response.status if response else None}
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def browser_screenshot(name: str = "screenshot", full_page: bool = False, path: str = "/tmp") -> dict:
        """Take a screenshot of the current page."""
        try:
            await init_browser()
            page = await get_page()
            save_path = Path(path)
            save_path.mkdir(parents=True, exist_ok=True)
            file_path = save_path / f"{name}.png"
            await page.screenshot(path=str(file_path), full_page=full_page)
            return {"status": "success", "path": str(file_path), "full_page": full_page}
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def browser_click(selector: str) -> dict:
        """Click an element by CSS selector."""
        try:
            await init_browser()
            page = await get_page()
            await page.click(selector, timeout=TIMEOUT)
            return {"status": "success", "selector": selector}
        except Exception as e:
            return {"status": "error", "error": str(e), "selector": selector}

    @mcp.tool()
    async def browser_type(selector: str, text: str, delay: int = 0) -> dict:
        """Type text into an element."""
        try:
            await init_browser()
            page = await get_page()
            await page.fill(selector, text, timeout=TIMEOUT)
            return {"status": "success", "selector": selector, "text": text}
        except Exception as e:
            return {"status": "error", "error": str(e), "selector": selector}

    @mcp.tool()
    async def browser_evaluate(script: str) -> dict:
        """Execute JavaScript in the browser page context."""
        try:
            await init_browser()
            page = await get_page()
            result = await page.evaluate(script, timeout=TIMEOUT)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def browser_get_html(selector: Optional[str] = None) -> dict:
        """Get HTML content from the page or element."""
        try:
            await init_browser()
            page = await get_page()
            if selector:
                html = await page.locator(selector).inner_html()
            else:
                html = await page.content()
            return {"status": "success", "html": html[:50000]}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def browser_wait(selector: str, timeout: int = TIMEOUT) -> dict:
        """Wait for an element to appear."""
        try:
            await init_browser()
            page = await get_page()
            await page.wait_for_selector(selector, timeout=timeout)
            return {"status": "success", "selector": selector}
        except Exception as e:
            return {"status": "error", "error": str(e), "selector": selector}

    @mcp.tool()
    async def browser_close() -> dict:
        """Close the browser and cleanup resources."""
        global _browser, _playwright, _context

        try:
            if _context:
                await _context.close()
            if _browser:
                await _browser.close()
            if _playwright:
                await _playwright.stop()

            _browser = _playwright = _context = None
            return {"status": "success", "message": "Browser closed"}
        except Exception as e:
            return {"status": "error", "error": str(e)}