# src/application/dto/auth_dto.py
"""
Auth DTOs - Data Transfer Objects for authentication.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# Request DTOs
class GenerateTokenRequest(BaseModel):
    """Request to generate a JWT token."""
    subject: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default="user")
    permissions: List[str] = Field(default_factory=lambda: ["read"])
    tier_access: List[str] = Field(default_factory=lambda: ["universal"])
    expiry_hours: int = Field(default=24, ge=1, le=168)


class ValidateTokenRequest(BaseModel):
    """Request to validate a JWT token."""
    token: str = Field(..., min_length=1)


class RevokeTokenRequest(BaseModel):
    """Request to revoke a JWT token."""
    token: str = Field(..., min_length=1)


# Response DTOs
class TokenResponse(BaseModel):
    """Response containing a JWT token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_id: Optional[str] = None


class TokenValidationResponse(BaseModel):
    """Response from validating a token."""
    valid: bool
    subject: Optional[str] = None
    role: Optional[str] = None
    permissions: List[str] = []
    tier_access: List[str] = []
    expires_in: Optional[int] = None
    error: Optional[str] = None


class TokenRevokeResponse(BaseModel):
    """Response from revoking a token."""
    success: bool
    message: str
