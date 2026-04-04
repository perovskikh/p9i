# src/middleware/auth_middleware.py
"""
Auth Middleware for FastMCP - extracts Authorization header for JWT validation.

This middleware extracts the Authorization header from incoming HTTP requests
and makes it available for JWT validation in MCP tools.
"""

import logging
from contextvars import ContextVar
from typing import Callable
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Context variables for async-safe request-local storage
_current_authorization: ContextVar[str | None] = ContextVar("current_authorization", default=None)
_current_api_key: ContextVar[str | None] = ContextVar("current_api_key", default=None)


class AuthHeaderMiddleware(BaseHTTPMiddleware):
    """Middleware to extract Authorization header from requests."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract Authorization header
        auth_header = request.headers.get("authorization")
        api_key = request.headers.get("x-api-key")

        # Log for debugging (masked)
        if auth_header:
            masked = auth_header[:20] + "..." if len(auth_header) > 20 else auth_header
            logger.info(f"Auth header detected: Bearer {masked}")

        # Store in context variables for access by MCP tools
        _current_authorization.set(auth_header)
        _current_api_key.set(api_key)

        # Also store X-API-Key if present
        if api_key:
            logger.info(f"X-API-Key detected (masked): {api_key[:10]}...")

        # Continue to the actual request handler
        response = await call_next(request)

        return response


def get_current_auth_header() -> str | None:
    """Get Authorization header from current request context."""
    return _current_authorization.get()


def get_current_api_key() -> str | None:
    """Get X-API-Key from current request context."""
    return _current_api_key.get()