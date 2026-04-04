#!/usr/bin/env python3
"""
Test for Tool Permissions (ADR-020 Phase 3).
Tests ToolPermission class and permission checks.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domain.entities.tool_permissions import (
    ToolPermission,
    ToolPermissions,
    READ_ONLY_PERMISSIONS,
    READ_ONLY_TOOLS,
    READ_WRITE_TOOLS,
    ADMIN_TOOLS,
)


def test_read_only_permissions():
    """READ_ONLY permission level should allow only read operations."""
    perms = ToolPermissions(ToolPermission.READ_ONLY)

    # Read operations allowed
    assert perms.can_execute("glob")
    assert perms.can_execute("grep")
    assert perms.can_execute("read")
    assert perms.can_execute("search")
    print("✅ Read operations allowed")

    # Write operations NOT allowed
    assert not perms.can_execute("write")
    assert not perms.can_execute("edit")
    assert not perms.can_execute("delete")
    assert not perms.can_execute("bash")
    print("✅ Write operations blocked")


def test_read_write_permissions():
    """READ_WRITE permission level should allow read + write."""
    perms = ToolPermissions(ToolPermission.READ_WRITE)

    # Read operations allowed
    assert perms.can_execute("read")
    assert perms.can_execute("grep")
    print("✅ Read operations allowed")

    # Write operations allowed
    assert perms.can_execute("write")
    assert perms.can_execute("edit")
    assert perms.can_execute("bash")
    print("✅ Write operations allowed")

    # Admin operations NOT allowed
    assert not perms.can_execute("destroy")
    assert not perms.can_execute("sudo")
    print("✅ Admin operations blocked")


def test_admin_permissions():
    """ADMIN permission level should allow everything."""
    perms = ToolPermissions(ToolPermission.ADMIN)

    assert perms.can_execute("read")
    assert perms.can_execute("write")
    assert perms.can_execute("destroy")
    assert perms.can_execute("deploy")
    print("✅ All operations allowed for ADMIN")


def test_disallowed_tools():
    """disallowed_tools() returns correct list."""
    read_only = ToolPermissions(ToolPermission.READ_ONLY)
    disallowed = read_only.disallowed_tools()
    assert "write" in disallowed
    assert "delete" in disallowed
    assert "destroy" in disallowed
    print("✅ Disallowed tools listed correctly")


def test_filter_tools():
    """filter_tools() returns only allowed tools."""
    perms = ToolPermissions(ToolPermission.READ_ONLY)
    tools = ["read", "write", "grep", "edit", "bash"]
    filtered = perms.filter_tools(tools)
    assert filtered == ["read", "grep"]
    print("✅ Tools filtered correctly")


def test_global_read_only():
    """READ_ONLY_PERMISSIONS global instance works."""
    assert READ_ONLY_PERMISSIONS.can_execute("read")
    assert not READ_ONLY_PERMISSIONS.can_execute("write")
    print("✅ Global READ_ONLY_PERMISSIONS works")


def test_case_insensitive():
    """Tool names are case insensitive."""
    perms = ToolPermissions(ToolPermission.READ_ONLY)
    assert perms.can_execute("READ")
    assert perms.can_execute("Read")
    assert perms.can_execute("read")
    print("✅ Case insensitive matching")


if __name__ == "__main__":
    print("Testing Tool Permissions (ADR-020 Phase 3)...\n")

    try:
        test_read_only_permissions()
        test_read_write_permissions()
        test_admin_permissions()
        test_disallowed_tools()
        test_filter_tools()
        test_global_read_only()
        test_case_insensitive()
        print("\n✅ All Tool Permissions tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
