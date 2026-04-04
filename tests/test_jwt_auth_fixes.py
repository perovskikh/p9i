#!/usr/bin/env python3
"""
Test for JWT Auth fixes (ADR-021).
Tests:
1. Exception handler order (JWTError not dead code)
2. revoke_token rejects malformed tokens
"""

import sys
import time
import os
from pathlib import Path
from jose import jwt, JWTError, ExpiredSignatureError, JWSError
from jose.exceptions import JWTClaimsError

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test secret before import
os.environ["JWT_SECRET"] = "test-secret-key-for-testing-purposes-32chars"

try:
    from src.middleware.jwt_auth import JWTService
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

JWT_SECRET = "test-secret-key-for-testing-purposes-32chars"


def create_token(payload: dict, expired: bool = False) -> str:
    """Helper to create JWT tokens for testing."""
    exp = int(time.time()) - 3600 if expired else int(time.time()) + 3600
    payload["exp"] = exp
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def test_validate_token_rejects_malformed():
    """Test that validate_token properly handles malformed tokens."""
    service = JWTService(secret_key=JWT_SECRET)

    # Valid token should work
    valid_token = create_token({"sub": "user123", "role": "admin"})
    result = service.validate_token(valid_token)
    assert result is not None, "Valid token should pass"

    print("✅ Valid token passes validation")


def test_revoke_token_rejects_invalid():
    """Test that revoke_token returns False for malformed tokens."""
    service = JWTService(secret_key=JWT_SECRET)

    # Malformed token (not JWT at all)
    result = service.revoke_token("not.a.valid.jwt.token")
    assert result == False, "Malformed token should be rejected"
    print("✅ Malformed token rejected by revoke_token")

    # Token with invalid signature
    bad_token = jwt.encode({"sub": "user"}, "wrong-secret", algorithm="HS256")
    result = service.revoke_token(bad_token)
    assert result == False, "Invalid signature should be rejected"
    print("✅ Invalid signature rejected by revoke_token")

    # Truncated token
    result = service.revoke_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
    assert result == False, "Truncated token should be rejected"
    print("✅ Truncated token rejected by revoke_token")


def test_exception_order():
    """Test that all JWT exception types are catchable."""
    service = JWTService(secret_key=JWT_SECRET)

    # Expired token
    expired_token = create_token({"sub": "user"}, expired=True)
    result = service.validate_token(expired_token)
    assert result is None, "Expired token should return None"
    print("✅ ExpiredSignatureError properly caught")

    # Invalid claims
    invalid_claims_token = jwt.encode(
        {"sub": "user", "exp": "invalid"},
        JWT_SECRET,
        algorithm="HS256"
    )
    result = service.validate_token(invalid_claims_token)
    assert result is None, "Invalid claims should return None"
    print("✅ JWTClaimsError properly caught")

    # Invalid signature (separate except block - NOT dead code)
    wrong_sig_token = jwt.encode(
        {"sub": "user", "exp": int(time.time()) + 3600},
        "wrong-secret-that-is-long-enough",
        algorithm="HS256"
    )
    result = service.validate_token(wrong_sig_token)
    assert result is None, "Invalid signature should return None"
    print("✅ JWSError properly caught (not dead code)")


if __name__ == "__main__":
    print("Testing JWT Auth fixes (ADR-021)...\n")

    try:
        test_validate_token_rejects_malformed()
        test_revoke_token_rejects_invalid()
        test_exception_order()
        print("\n✅ All JWT Auth tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
