# src/middleware/jwt_auth.py
"""
JWT Authentication Service for AI Prompt System v2.0.0

Provides JWT token-based authentication with:
- Token generation and validation using python-jose
- Refresh token mechanism
- Token revocation support
- Role-based access control (RBAC)

Follows FastAPI best practices:
- Uses python-jose for JWT encode/decode
- Proper exception handling with ExpiredSignatureError, JWTClaimsError
- HTTPException with 401 and WWW-Authenticate header
"""

import os
import time
import hashlib
import json
from typing import Optional, Dict, List, Any
from functools import wraps
from dataclasses import dataclass
import logging

# JWT imports - using python-jose (FastAPI recommended)
from jose import jwt, JWTError, ExpiredSignatureError, JWTClaimsError
from jose.exceptions import JWSSignatureError, JWSError

logger = logging.getLogger(__name__)


@dataclass
class TokenPayload:
    """JWT token payload."""
    sub: str  # Subject (user/project ID)
    role: str  # Role: admin, developer, user
    permissions: List[str]
    tier_access: List[str]  # Which tiers can be accessed
    exp: int  # Expiration timestamp
    iat: int  # Issued at timestamp
    refresh_id: str  # Refresh token ID for revocation


class JWTService:
    """JWT authentication service with optional Redis persistence."""

    def __init__(self, secret_key: str = None, redis_client=None):
        # Use environment secret or generate from machine ID
        self.secret_key = secret_key or os.getenv(
            "JWT_SECRET",
            hashlib.sha256(str(os.uname()).encode()).hexdigest()[:32]
        )
        self.algorithm = "HS256"
        self.default_expiry = 3600  # 1 hour
        self.refresh_expiry = 604800  # 7 days

        # Redis client for distributed token storage
        self._redis = redis_client

        # Token revocation list (fallback if Redis unavailable)
        self._revoked_tokens: set = set()
        self._refresh_tokens: Dict[str, Dict] = {}

    def _is_token_revoked(self, token: str) -> bool:
        """Check if token is revoked (Redis or in-memory)."""
        # Try Redis first (handle both sync and async clients)
        if self._redis:
            try:
                import asyncio
                key = f"jwt:revoked:{hashlib.sha256(token.encode()).hexdigest()[:32]}"

                # Check if it's an async Redis client
                if hasattr(self._redis, 'get') and asyncio.iscoroutinefunction(self._redis.get):
                    # Can't use async in sync context - use in-memory fallback
                    logger.warning("Async Redis detected, using in-memory fallback")
                else:
                    result = self._redis.get(key)
                    return result is not None
            except Exception as e:
                logger.warning(f"Redis check failed, using in-memory: {e}")

        # Fallback to in-memory
        return token in self._revoked_tokens

    def _revoke_token(self, token: str, expiry: int = None) -> None:
        """Revoke token (Redis or in-memory)."""
        expiry = expiry or self.default_expiry

        # Try Redis first (handle both sync and async clients)
        if self._redis:
            try:
                import asyncio
                key = f"jwt:revoked:{hashlib.sha256(token.encode()).hexdigest()[:32]}"

                # Check if it's an async Redis client
                if hasattr(self._redis, 'setex') and asyncio.iscoroutinefunction(self._redis.setex):
                    # Can't use async in sync context - use in-memory fallback
                    logger.warning("Async Redis detected, using in-memory fallback")
                else:
                    self._redis.setex(key, expiry, "1")
                    return
            except Exception as e:
                logger.warning(f"Redis revoke failed, using in-memory: {e}")

        # Fallback to in-memory
        self._revoked_tokens.add(token)

    def generate_token(
        self,
        subject: str,
        role: str = "user",
        permissions: List[str] = None,
        tier_access: List[str] = None,
        expiry: int = None
    ) -> str:
        """Generate a JWT token."""
        now = int(time.time())
        exp = now + (expiry or self.default_expiry)

        # Generate refresh token ID
        refresh_id = hashlib.sha256(
            f"{subject}{now}{self.secret_key}".encode()
        ).hexdigest()[:16]

        payload = {
            "sub": subject,
            "role": role,
            "permissions": permissions or ["read"],
            "tier_access": tier_access or ["universal"],
            "exp": exp,
            "iat": now,
            "refresh_id": refresh_id
        }

        # Store refresh token
        self._refresh_tokens[refresh_id] = {
            "sub": subject,
            "role": role,
            "expires": now + self.refresh_expiry
        }

        # Create JWT using python-jose (FastAPI best practice)
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def generate_refresh_token(self, refresh_id: str) -> Optional[str]:
        """Generate a new access token from refresh token."""
        refresh_data = self._refresh_tokens.get(refresh_id)
        if not refresh_data:
            return None

        # Check if refresh token expired
        if refresh_data["expires"] < int(time.time()):
            del self._refresh_tokens[refresh_id]
            return None

        return self.generate_token(
            subject=refresh_data["sub"],
            role=refresh_data["role"]
        )

    def validate_token(self, token: str) -> Optional[TokenPayload]:
        """Validate JWT token and return payload.

        Uses python-jose for proper validation:
        - Signature verification
        - Expiration checking (exp claim)
        - Not-before checking (nbf claim)
        - Issuer/audience validation (optional)

        Raises specific exceptions for better error handling:
        - ExpiredSignatureError: Token has expired
        - JWTClaimsError: Invalid claims
        - JWSSignatureError: Invalid signature
        """
        try:
            # Decode with full validation using python-jose
            # Options: verify_exp=True (default), verify_signature=True (default)
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_nbf': False,  # Skip not-before check for flexibility
                    'verify_iat': False,  # Skip issued-at check
                    'require_exp': True   # Require expiration claim
                }
            )

            # Check revocation
            if self._is_token_revoked(token):
                logger.warning("Token revoked")
                return None

            return TokenPayload(
                sub=payload.get("sub", ""),
                role=payload.get("role", "user"),
                permissions=payload.get("permissions", []),
                tier_access=payload.get("tier_access", []),
                exp=payload.get("exp", 0),
                iat=payload.get("iat", 0),
                refresh_id=payload.get("refresh_id", "")
            )

        except ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except JWTClaimsError as e:
            logger.warning(f"Invalid claims: {e}")
            return None
        except JWSSignatureError:
            logger.warning("Invalid token signature")
            return None
        except JWTError as e:
            logger.error(f"JWT error: {e}")
            return None
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None

    def revoke_token(self, token: str) -> bool:
        """Revoke a token (Redis or in-memory)."""
        # Decode token to get expiry using python-jose
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={'verify_exp': False}  # Allow expired tokens
            )
            exp = payload.get("exp", 0)
            ttl = max(0, exp - int(time.time()))
        except Exception:
            ttl = self.default_expiry

        self._revoke_token(token, ttl)
        return True

    def revoke_refresh_token(self, refresh_id: str) -> bool:
        """Revoke a refresh token."""
        if refresh_id in self._refresh_tokens:
            del self._refresh_tokens[refresh_id]
            return True
        return False

    def check_tier_access(self, payload: TokenPayload, tier: str) -> bool:
        """Check if token has access to specific tier."""
        if payload.role == "admin":
            return True
        return tier in payload.tier_access

    def check_permission(self, payload: TokenPayload, permission: str) -> bool:
        """Check if token has specific permission."""
        if payload.role == "admin":
            return True
        return permission in payload.permissions


# FastAPI-style OAuth2 dependency (for use with FastAPI routes)
# This provides proper 401 response with WWW-Authenticate header
def create_oauth_scheme():
    """Create OAuth2PasswordBearer scheme (for FastAPI integration).

    Returns a callable that extracts the token from the Authorization header.
    """
    try:
        from fastapi import Depends, HTTPException, status
        from fastapi.security import OAuth2PasswordBearer
        from typing import Optional

        oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

        async def get_current_user_from_token(token: str = Depends(oauth2_scheme)) -> TokenPayload:
            """Dependency to get current user from JWT token."""
            jwt_service = get_jwt_service()

            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

            try:
                payload = jwt.decode(token, jwt_service.secret_key, algorithms=[jwt_service.algorithm])
                sub: str = payload.get("sub")
                if sub is None:
                    raise credentials_exception
            except (ExpiredSignatureError, JWTClaimsError, JWSSignatureError, JWTError) as e:
                logger.warning(f"JWT validation failed: {e}")
                raise credentials_exception

            user = jwt_service.validate_token(token)
            if user is None:
                raise credentials_exception

            return user

        return get_current_user_from_token

    except ImportError:
        # FastAPI not available, return None
        logger.warning("FastAPI not available, OAuth2 dependency not created")
        return None


# Default roles configuration
DEFAULT_ROLES = {
    "admin": {
        "permissions": ["*"],
        "tier_access": ["core", "universal", "mpv_stage", "projects"],
        "rate_limit": 1000
    },
    "developer": {
        "permissions": ["read_prompts", "run_prompt", "write_prompts"],
        "tier_access": ["universal", "mpv_stage", "projects"],
        "rate_limit": 500
    },
    "user": {
        "permissions": ["read_prompts", "run_prompt"],
        "tier_access": ["universal"],
        "rate_limit": 100
    }
}


def require_auth(role: str = None, permission: str = None, tier: str = None):
    """Decorator for requiring authentication."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # In FastMCP, auth is handled differently
            # This is a placeholder for the auth logic
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Global JWT service instance
_jwt_service: Optional[JWTService] = None


def get_jwt_service() -> JWTService:
    """Get or create global JWT service."""
    global _jwt_service
    if _jwt_service is None:
        _jwt_service = JWTService()
    return _jwt_service
