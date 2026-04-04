# src/domain/entities/tool_permissions.py
"""
Tool Permissions - Access control for agent tools.

Implements permission levels for coordinator pattern:
- READ_ONLY: glob, grep, read, bash (output only)
- READ_WRITE: + write, edit, bash (full)
- ADMIN: + delete, destroy
"""

from enum import Enum
from typing import List, Set


class ToolPermission(Enum):
    """Permission levels for tool access."""
    READ_ONLY = "read_only"      # glob, grep, read, limited bash
    READ_WRITE = "read_write"    # + write, edit, bash (full)
    ADMIN = "admin"              # + delete, destroy


# Tool categorization by permission level
READ_ONLY_TOOLS = {
    # File reading
    "glob", "grep", "read", "cat", "head", "tail",
    # Searching
    "search", "find", "whereis", "locate",
    # Info gathering
    "info", "stats", "list", "ls", "dir",
    # Read-only bash (output only)
    "bash_output", "bash_read",
}

READ_WRITE_TOOLS = {
    # File modification
    "write", "edit", "append", "insert",
    # File creation/deletion
    "create", "delete", "remove", "rm",
    # Bash with side effects
    "bash", "run", "execute", "shell",
    # Build/test
    "build", "test", "compile",
}

ADMIN_TOOLS = {
    # Dangerous operations
    "destroy", "drop", "truncate",
    # System operations
    "sudo", "chmod", "chown",
    # Infrastructure
    "deploy", "undeploy", "restart",
}


class ToolPermissions:
    """
    Access control for agent tools based on permission level.

    Usage:
        permissions = ToolPermissions(ToolPermission.READ_ONLY)
        if permissions.can_execute("read"):
            # allowed

        if permissions.can_execute("write"):
            # not allowed
    """

    def __init__(self, permission_level: ToolPermission):
        self.permission_level = permission_level
        self._allowed_tools = self._build_allowed_set(permission_level)
        self._disallowed_tools = self._build_disallowed_set(permission_level)

    def _build_allowed_set(self, level: ToolPermission) -> Set[str]:
        """Build set of allowed tools for permission level."""
        allowed = set()
        if level == ToolPermission.READ_ONLY:
            allowed.update(READ_ONLY_TOOLS)
        elif level == ToolPermission.READ_WRITE:
            allowed.update(READ_ONLY_TOOLS)
            allowed.update(READ_WRITE_TOOLS)
        elif level == ToolPermission.ADMIN:
            allowed.update(READ_ONLY_TOOLS)
            allowed.update(READ_WRITE_TOOLS)
            allowed.update(ADMIN_TOOLS)
        return allowed

    def _build_disallowed_set(self, level: ToolPermission) -> List[str]:
        """Build list of disallowed tools for permission level."""
        if level == ToolPermission.READ_ONLY:
            return list(READ_WRITE_TOOLS | ADMIN_TOOLS)
        elif level == ToolPermission.READ_WRITE:
            return list(ADMIN_TOOLS)
        return []

    def can_execute(self, tool_name: str) -> bool:
        """
        Check if tool is allowed for this permission level.

        Args:
            tool_name: Name of tool to check

        Returns:
            True if tool is allowed, False otherwise
        """
        return tool_name.lower() in self._allowed_tools

    def disallowed_tools(self) -> List[str]:
        """
        Get list of tools not allowed for this permission level.

        Returns:
            List of disallowed tool names
        """
        return self._disallowed_tools

    def filter_tools(self, tools: List[str]) -> List[str]:
        """
        Filter list of tools to only those allowed.

        Args:
            tools: List of tool names to filter

        Returns:
            List of allowed tool names
        """
        return [t for t in tools if self.can_execute(t)]


# Global read-only permissions for verification agents
READ_ONLY_PERMISSIONS = ToolPermissions(ToolPermission.READ_ONLY)
