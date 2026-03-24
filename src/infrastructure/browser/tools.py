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

# Configuration from environment
HEADLESS = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30000"))
VIEWPORT_WIDTH = int(os.getenv("BROWSER_VIEWPORT_WIDTH", "1280"))
VIEWPORT_HEIGHT = int(os.getenv("BROWSER_VIEWPORT_HEIGHT", "720"))


async def _get_browser_context():
    """Get or create browser context."""
    global _browser, _playwright, _context

    if _browser is None:
        try:
            _playwright = await asyncio.wait_for(
                async_playwright().start(),
                timeout=10
            )
            _browser = await asyncio.wait_for(
                _playwright.chromium.launch(headless=HEADLESS),
                timeout=30
            )
            _context = await _browser.new_context(
                viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT}
            )
            logger.info("Browser launched successfully")
        except asyncio.TimeoutError:
            logger.error("Browser launch timeout")
            raise Exception("Failed to launch browser: timeout")
        except Exception as e:
            logger.error(f"Browser launch failed: {e}")
            raise Exception(f"Failed to launch browser: {e}")

    return _browser, _context


async def _ensure_page() -> object:
    """Ensure we have at least one page."""
    browser, context = await _get_browser_context()
    if not context.pages:
        return await context.new_page()
    return context.pages[0]


def register_browser_tools(mcp):
    """Register browser automation tools with MCP server."""

    @mcp.tool()
    async def browser_navigate(url: str) -> dict:
        """
        Navigate to a URL in the browser.

        Args:
            url: The URL to navigate to

        Returns:
            dict with status, url, and title
        """
        try:
            page = await _ensure_page()
            response = await page.goto(url, timeout=TIMEOUT)
            title = await page.title()

            return {
                "status": "success",
                "url": url,
                "title": title,
                "status_code": response.status if response else None
            }
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def browser_screenshot(
        name: str = "screenshot",
        full_page: bool = False,
        path: str = "/tmp"
    ) -> dict:
        """
        Take a screenshot of the current page.

        Args:
            name: Screenshot filename (without extension)
            full_page: Capture full scrollable page
            path: Directory to save screenshot

        Returns:
            dict with status and path
        """
        try:
            page = await _ensure_page()

            # Ensure path exists
            save_path = Path(path)
            save_path.mkdir(parents=True, exist_ok=True)

            file_path = save_path / f"{name}.png"
            await page.screenshot(path=str(file_path), full_page=full_page)

            return {
                "status": "success",
                "path": str(file_path),
                "full_page": full_page
            }
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def browser_click(selector: str) -> dict:
        """
        Click an element by CSS selector.

        Args:
            selector: CSS selector of the element to click

        Returns:
            dict with status and selector
        """
        try:
            page = await _ensure_page()
            await page.click(selector, timeout=TIMEOUT)

            return {"status": "success", "selector": selector}
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return {"status": "error", "error": str(e), "selector": selector}

    @mcp.tool()
    async def browser_type(selector: str, text: str, delay: int = 0) -> dict:
        """
        Type text into an element.

        Args:
            selector: CSS selector of the input element
            text: Text to type
            delay: Delay between keystrokes in ms

        Returns:
            dict with status, selector, and text
        """
        try:
            page = await _ensure_page()
            await page.fill(selector, text, timeout=TIMEOUT)

            return {"status": "success", "selector": selector, "text": text}
        except Exception as e:
            logger.error(f"Type failed: {e}")
            return {"status": "error", "error": str(e), "selector": selector}

    @mcp.tool()
    async def browser_evaluate(script: str) -> dict:
        """
        Execute JavaScript in the browser page context.

        Args:
            script: JavaScript code to execute

        Returns:
            dict with status and result
        """
        try:
            page = await _ensure_page()
            result = await page.evaluate(script, timeout=TIMEOUT)

            return {"status": "success", "result": result}
        except Exception as e:
            logger.error(f"Evaluate failed: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def browser_get_html(selector: Optional[str] = None) -> dict:
        """
        Get HTML content from the page or element.

        Args:
            selector: Optional CSS selector (if not provided, returns page HTML)

        Returns:
            dict with status and html content
        """
        try:
            page = await _ensure_page()

            if selector:
                html = await page.locator(selector).inner_html()
            else:
                html = await page.content()

            return {"status": "success", "html": html[:50000]}  # Limit size
        except Exception as e:
            logger.error(f"Get HTML failed: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def browser_wait(selector: str, timeout: int = TIMEOUT) -> dict:
        """
        Wait for an element to appear.

        Args:
            selector: CSS selector to wait for
            timeout: Wait timeout in ms

        Returns:
            dict with status and selector
        """
        try:
            page = await _ensure_page()
            await page.wait_for_selector(selector, timeout=timeout)

            return {"status": "success", "selector": selector}
        except Exception as e:
            logger.error(f"Wait failed: {e}")
            return {"status": "error", "error": str(e), "selector": selector}

    @mcp.tool()
    async def browser_close() -> dict:
        """
        Close the browser and cleanup resources.

        Returns:
            dict with status
        """
        global _browser, _playwright, _context

        try:
            if _context:
                await _context.close()
            if _browser:
                await _browser.close()
            if _playwright:
                await _playwright.stop()

            _browser = None
            _playwright = None
            _context = None

            return {"status": "success", "message": "Browser closed"}
        except Exception as e:
            logger.error(f"Close failed: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def browser_status() -> dict:
        """
        Get browser status and configuration.

        Returns:
            dict with browser status
        """
        global _browser

        return {
            "status": "running" if _browser else "stopped",
            "headless": HEADLESS,
            "viewport": {"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
            "timeout": TIMEOUT
        }


# Lazy import for playwright
async def async_playwright():
    """Import and return playwright async module."""
    from playwright.async_api import async_playwright as ap
    return ap
