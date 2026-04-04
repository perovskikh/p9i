#!/usr/bin/env python3
"""
Test for Prompt Injection Sanitization (ADR-013).
Tests sanitize_for_prompt function.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domain.services.prompt_guard import (
    sanitize_for_prompt,
    sanitize_dict,
    check_for_injection
)


def test_sanitize_normal_text():
    """Normal text should pass through unchanged."""
    result = sanitize_for_prompt("Hello, world!")
    assert result == "Hello, world!"
    print("✅ Normal text unchanged")


def test_sanitize_template_injection():
    """Template injection patterns should be removed."""
    # {{variable}} injection
    result = sanitize_for_prompt("Hello {{name}}!")
    assert "{{" not in result and "}}" not in result
    print("✅ Template injection blocked: {{}}")

    # ${{}} nested - removes all dangerous chars
    result = sanitize_for_prompt("${{{{config}}}}")
    # All injection chars removed: $, {, }
    assert "$" not in result and "{" not in result and "}" not in result
    print("✅ Nested template injection blocked")


def test_sanitize_shell_injection():
    """Shell-like patterns should be removed."""
    # $() command substitution - removes $(
    result = sanitize_for_prompt("Running $(whoami)")
    assert "$(" not in result
    # ) remains but that's okay - the dangerous $( is gone
    print("✅ Command substitution blocked: $()")

    # ${} variable - removes ${
    result = sanitize_for_prompt("Value is ${SECRET}")
    assert "${" not in result
    # } remains but that's okay - the dangerous ${ is gone
    print("✅ Variable expansion blocked: ${}")


def test_sanitize_backtick():
    """Backticks should be removed."""
    result = sanitize_for_prompt("Result: `ls -la`")
    assert "`" not in result
    print("✅ Backticks removed")


def test_sanitize_xss():
    """XSS patterns should be blocked."""
    result = sanitize_for_prompt("<script>alert('xss')</script>")
    assert "<script>" not in result.lower()
    print("✅ XSS blocked")


def test_sanitize_non_string():
    """Non-string values should be converted."""
    result = sanitize_for_prompt(123)
    assert result == "123"
    print("✅ Non-string converted")


def test_sanitize_none():
    """None should return empty string."""
    result = sanitize_for_prompt(None)
    assert result == ""
    print("✅ None returns empty string")


def test_sanitize_length_limit():
    """Long inputs should be truncated."""
    long_text = "a" * 5000
    result = sanitize_for_prompt(long_text)
    assert len(result) <= 2000
    print("✅ Length limited to 2000 chars")


def test_check_for_injection():
    """Check if value contains injection patterns."""
    assert check_for_injection("{{variable}}") == True
    assert check_for_injection("$(whoami)") == True
    assert check_for_injection("normal text") == False
    print("✅ Injection detection works")


def test_sanitize_dict():
    """Dictionary values should be sanitized."""
    data = {
        "task": "Normal task",
        "name": "{{injected}}",
        "command": "$(whoami)"
    }
    result = sanitize_dict(data)
    assert result["task"] == "Normal task"
    assert "{{" not in result["name"]
    assert "$(" not in result["command"]
    print("✅ Dictionary sanitized correctly")


if __name__ == "__main__":
    print("Testing Prompt Injection Sanitization (ADR-013)...\n")

    try:
        test_sanitize_normal_text()
        test_sanitize_template_injection()
        test_sanitize_shell_injection()
        test_sanitize_backtick()
        test_sanitize_xss()
        test_sanitize_non_string()
        test_sanitize_none()
        test_sanitize_length_limit()
        test_check_for_injection()
        test_sanitize_dict()
        print("\n✅ All Prompt Injection tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
