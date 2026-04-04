"""
Auth MCP Tools - JWT authentication tools.

These tools provide JWT token generation, validation, and revocation.

Based on JWT authentication patterns with secure token management.
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def register_auth_tools(mcp, jwt_service=None, jwt_enabled: bool = False):
    """
    Register JWT authentication tools with the MCP server.

    Args:
        mcp: FastMCP server instance
        jwt_service: JWTService instance (required if jwt_enabled=True)
        jwt_enabled: Whether JWT authentication is enabled
    """

    if jwt_enabled and jwt_service is None:
        raise ValueError("jwt_service is required when jwt_enabled=True")

    @mcp.tool()
    def generate_jwt_token(
        subject: str,
        role: str = "user",
        expiry_hours: int = 24,
        admin_key: str = None
    ) -> dict:
        """
        Generate a JWT access token for API authentication.

        Args:
            subject: User or project identifier
            role: Role (admin, developer, user)
            expiry_hours: Token expiration in hours (default 24)
            admin_key: Required admin key to generate tokens (from JWT_ADMIN_KEY env)
        """
        if not jwt_enabled:
            return {"status": "error", "error": "JWT authentication is not enabled"}

        # SECURITY: Require admin key for token generation
        jwt_admin_key = os.getenv("JWT_ADMIN_KEY")
        if jwt_admin_key and admin_key != jwt_admin_key:
            return {"status": "error", "error": "Invalid admin key"}

        # SECURITY: Prevent privilege escalation - only admin can create admin tokens
        if role == "admin" and admin_key != jwt_admin_key:
            return {"status": "error", "error": "Admin role requires valid admin key"}

        try:
            token = jwt_service.generate_token(
                subject=subject,
                role=role,
                expiry=expiry_hours * 3600
            )
            return {
                "status": "success",
                "token": token,
                "subject": subject,
                "role": role,
                "expires_in": expiry_hours * 3600
            }
        except Exception as e:
            logger.error(f"JWT token generation error: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    def validate_jwt_token(token: str) -> dict:
        """
        Validate a JWT token and return its payload.

        Args:
            token: JWT token to validate
        """
        if not jwt_enabled:
            return {"status": "error", "error": "JWT authentication is not enabled"}

        if not token:
            return {"status": "error", "error": "Token is required"}

        payload = jwt_service.validate_token(token)

        if payload:
            return {
                "status": "success",
                "valid": True,
                "subject": payload.sub,
                "role": payload.role,
                "permissions": payload.permissions,
                "tier_access": payload.tier_access,
                "expires_at": payload.exp
            }
        else:
            return {
                "status": "success",
                "valid": False,
                "error": "Invalid or expired token"
            }

    @mcp.tool()
    def revoke_jwt_token(token: str) -> dict:
        """
        Revoke a JWT token.

        Args:
            token: JWT token to revoke
        """
        if not jwt_enabled:
            return {"status": "error", "error": "JWT authentication is not enabled"}

        if jwt_service.revoke_token(token):
            return {"status": "success", "message": "Token revoked"}
        return {"status": "error", "error": "Failed to revoke token"}

    return [generate_jwt_token, validate_jwt_token, revoke_jwt_token]
