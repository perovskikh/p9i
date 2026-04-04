#!/usr/bin/env python3
"""
p9i-AI Prompt System - JWT Token Generator

Generate JWT tokens for MCP HTTP authentication.

Usage:
    python3 -m cli.main jwt generate --subject my-project --role admin
    python3 -m cli.main jwt validate <token>
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).parent.parent


def load_env():
    """Load environment variables from .env file."""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        print(f"Error: .env file not found at {env_path}")
        sys.exit(1)

    env_vars = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    return env_vars


def generate_token(args):
    """Generate a JWT token."""
    from jose import jwt

    env_vars = load_env()
    secret = env_vars.get("JWT_SECRET") or "p9i-jwt-secret-change-in-production"
    admin_key = env_vars.get("JWT_ADMIN_KEY")

    # Check admin key if generating admin token
    if args.role == "admin" and args.admin_key != admin_key:
        print(f"Error: Invalid admin key. Use --admin-key or set JWT_ADMIN_KEY in .env")
        sys.exit(1)

    # Build payload
    now = datetime.utcnow()
    exp = now + timedelta(hours=args.expiry)

    payload = {
        "sub": args.subject,
        "role": args.role,
        "permissions": args.permissions.split(",") if args.permissions else ["read_prompts", "run_prompt"],
        "tier_access": args.tier_access.split(",") if args.tier_access else ["universal"],
        "exp": int(exp.timestamp()),
        "iat": int(now.timestamp()),
    }

    token = jwt.encode(payload, secret, algorithm="HS256")

    print(f"Generated JWT token for: {args.subject}")
    print(f"Role: {args.role}")
    print(f"Expires: {exp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"\nToken:")
    print(token)
    domain = env_vars.get("DOMAIN", os.getenv("DOMAIN", "p9i.ru"))
    print(f"\nUsage in Claude Code:")
    print(f'{{"url": "https://{domain}/mcp", "headers": {{"Authorization": "Bearer {token}"}}}}')


def validate_token(args):
    """Validate a JWT token."""
    from jose import jwt, JWTError, ExpiredSignatureError

    env_vars = load_env()
    secret = env_vars.get("JWT_SECRET") or "p9i-jwt-secret-change-in-production"

    try:
        payload = jwt.decode(
            args.token,
            secret,
            algorithms=["HS256"],
            options={"verify_exp": True}
        )

        exp = datetime.fromtimestamp(payload["exp"])
        iat = datetime.fromtimestamp(payload["iat"])

        print(f"✓ Token is valid")
        print(f"Subject: {payload['sub']}")
        print(f"Role: {payload['role']}")
        print(f"Permissions: {payload['permissions']}")
        print(f"Tier access: {payload['tier_access']}")
        print(f"Issued at: {iat.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"Expires: {exp.strftime('%Y-%m-%d %H:%M:%S UTC')}")

    except ExpiredSignatureError:
        print(f"✗ Token has expired")
    except JWTError as e:
        print(f"✗ Invalid token: {e}")


def main():
    parser = argparse.ArgumentParser(
        prog="p9i jwt",
        description="p9i-AI Prompt System JWT Token Management"
    )

    subparsers = parser.add_subparsers(dest="command", help="JWT commands")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate JWT token")
    gen_parser.add_argument("--subject", "-s", required=True, help="Subject (project/user ID)")
    gen_parser.add_argument("--role", "-r", default="user", choices=["admin", "developer", "user"], help="Role")
    gen_parser.add_argument("--expiry", "-e", type=int, default=24, help="Expiry hours (default: 24)")
    gen_parser.add_argument("--permissions", default="", help="Comma-separated permissions")
    gen_parser.add_argument("--tier-access", default="", help="Comma-separated tier access")
    gen_parser.add_argument("--admin-key", default="", help="Admin key for admin role")

    # Validate command
    val_parser = subparsers.add_parser("validate", help="Validate JWT token")
    val_parser.add_argument("token", help="JWT token to validate")

    args = parser.parse_args()

    if args.command == "generate":
        generate_token(args)
    elif args.command == "validate":
        validate_token(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()