# AI Agent Prompt: Browser Integration

**Version:** 1.0
**Date:** 2026-03-24
**Purpose:** Реализация browser automation с полным циклом тестирования

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Full Cycle Implementation |
| **Время выполнения** | 60–180 мин |
| **Домен** | Browser Automation, Playwright, CDP |

**Пример запроса:**

> «Реализуй browser integration с Playwright. use p9i»
> «Создай автоматизацию браузера для e2e тестов. use p9i»

**Ожидаемый результат:**
- Playwright browser automation модуль
- Unit тесты
- E2E тесты
- Документация

---

## Mission Statement

Ты — AI-агент, специализирующийся на **browser automation** с использованием Playwright.

**Что реализует этот промпт:**
- Browser tools модуль для MCP
- Playwright integration
- Скриншоты, навигация, клики
- E2E тесты

---

## Реализация

### 1. Dependencies (pyproject.toml)

```toml
[project.optional-dependencies]
browser = [
    "playwright>=1.40.0",
]
```

### 2. Browser Tools Module

Создай `src/infrastructure/browser/tools.py`:

```python
"""Browser Automation Tools for MCP Server."""

from playwright.async_api import async_playwright
from typing import Optional
import asyncio

_browser = None
_context = None

async def get_browser_context():
    global _browser, _context
    if _browser is None:
        pw = await async_playwright().start()
        _browser = await pw.chromium.launch(headless=True)
        _context = await _browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
    return _browser, _context

async def browser_navigate(url: str) -> dict:
    """Navigate to URL."""
    browser, context = await get_browser_context()
    page = await context.new_page()
    await page.goto(url)
    return {"url": url, "title": await page.title()}

async def browser_screenshot(name: str = "screenshot") -> dict:
    """Take screenshot."""
    browser, context = await get_browser_context()
    page = context.pages[0] if context.pages else await context.new_page()
    path = f"/tmp/{name}.png"
    await page.screenshot(path=path)
    return {"path": path}

async def browser_click(selector: str) -> dict:
    """Click element."""
    browser, context = await get_browser_context()
    page = context.pages[0]
    await page.click(selector)
    return {"selector": selector, "status": "clicked"}

async def browser_type(selector: str, text: str) -> dict:
    """Type text into element."""
    browser, context = await get_browser_context()
    page = context.pages[0]
    await page.fill(selector, text)
    return {"selector": selector, "text": text}

async def browser_evaluate(script: str) -> dict:
    """Execute JavaScript in page context."""
    browser, context = await get_browser_context()
    page = context.pages[0]
    result = await page.evaluate(script)
    return {"result": result}

async def browser_close() -> dict:
    """Close browser."""
    global _browser, _context
    if _browser:
        await _context.close()
        await _browser.close()
        _browser = None
        _context = None
    return {"status": "closed"}
```

### 3. MCP Tools Registration

Зарегистрируй в `src/api/server.py`:

```python
from src.infrastructure.browser import register_browser_tools

# Register browser tools
register_browser_tools(mcp)
```

### 4. Docker Integration

```dockerfile
# docker/Dockerfile
RUN apt-get update && apt-get install -y \
    chromium \
    && playwright install chromium \
    && rm -rf /var/lib/apt/lists/*
```

### 5. Environment Variables

```bash
# .env
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=30000
BROWSER_VIEWPORT_WIDTH=1280
BROWSER_VIEWPORT_HEIGHT=720
```

---

## Тесты

### Unit Tests

```python
# tests/test_browser_tools.py
import pytest
from src.infrastructure.browser.tools import browser_navigate

@pytest.mark.asyncio
async def test_navigate():
    result = await browser_navigate("https://example.com")
    assert result["url"] == "https://example.com"
```

---

## Результат

- `src/infrastructure/browser/tools.py` - Browser tools
- `tests/test_browser_tools.py` - Unit tests
- `pyproject.toml` - Updated dependencies
- `docker/Dockerfile` - Chrome installation
