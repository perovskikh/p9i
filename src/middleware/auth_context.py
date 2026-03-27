# src/middleware/auth_context.py
"""
Auth context - Extract Authorization header from MCP HTTP requests.

For streamable-http transport, we need to manually extract auth headers.
"""

import os
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Global request context for storing auth info between requests
_auth_context = {}


def set_auth_context(authorization: str = None, x_api_key: str = None):
    """Set auth context from HTTP headers (called by MCP server)."""
    global _auth_context
    _auth_context = {
        "authorization": authorization,
        "x_api_key": x_api_key,
    }
    logger.debug(f"Auth context set: auth={authorization[:20] if authorization else None}...")


def get_auth_header() -> Optional[str]:
    """Get Authorization header from context."""
    return _auth_context.get("authorization")


def get_api_key() -> Optional[str]:
    """Get X-API-Key from context."""
    return _auth_context.get("x_api_key")


def clear_auth_context():
    """Clear auth context after request."""
    global _auth_context
    _auth_context = {}


def extract_auth_from_request(headers: dict) -> Tuple[Optional[str], Optional[str]]:
    """Extract auth info from HTTP headers dict.

    Args:
        headers: Dict of HTTP headers (lowercase keys)

    Returns:
        Tuple of (authorization, api_key)
    """
    authorization = headers.get("authorization")
    api_key = headers.get("x-api-key") or headers.get("api_key")
    return authorization, api_key