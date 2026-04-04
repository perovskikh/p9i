"""
Session MCP Tools - MCP session management tools.

These tools provide MCP session management for direct HTTP connections.
Sessions are stored in Redis and persist across server restarts.
"""

import logging

logger = logging.getLogger(__name__)

# Global reference - will be set during registration
_get_session_manager_func = None


def register_session_tools(mcp, get_session_manager_func):
    """
    Register MCP session management tools with the MCP server.

    Args:
        mcp: FastMCP server instance
        get_session_manager_func: Function that returns MCPSessionManager instance
    """
    global _get_session_manager_func

    _get_session_manager_func = get_session_manager_func

    @mcp.tool()
    async def create_mcp_session(client_info: dict = None) -> dict:
        """
        Create a new MCP session for direct HTTP connections.

        This enables direct connections without using the proxy (p9i_stdio_bridge.py).
        Sessions are stored in Redis and persist across server restarts.

        Args:
            client_info: Optional client information (protocol version, capabilities, etc.)

        Returns:
            dict: Session ID and status
        """
        try:
            session_manager = await _get_session_manager_func()
            session_id = await session_manager.create_session(client_info)

            return {
                "status": "success",
                "session_id": session_id,
                "message": "Session created. Use session_id in X-MCP-Session-Id header for subsequent requests."
            }
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def get_mcp_session(session_id: str) -> dict:
        """
        Get MCP session information.

        Args:
            session_id: Session ID to retrieve

        Returns:
            dict: Session data
        """
        try:
            session_manager = await _get_session_manager_func()
            session = await session_manager.get_session(session_id)

            if session:
                return {"status": "success", "session": session}
            else:
                return {"status": "error", "error": "Session not found or expired"}
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def update_mcp_session(session_id: str, state: dict) -> dict:
        """
        Update session state.

        Args:
            session_id: Session ID to update
            state: State data to merge into session

        Returns:
            dict: Update status
        """
        try:
            session_manager = await _get_session_manager_func()
            success = await session_manager.update_session(session_id, state)

            if success:
                return {"status": "success", "message": "Session updated"}
            else:
                return {"status": "error", "error": "Session not found or failed to update"}
        except Exception as e:
            logger.error(f"Failed to update session: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def delete_mcp_session(session_id: str) -> dict:
        """
        Delete an MCP session.

        Args:
            session_id: Session ID to delete

        Returns:
            dict: Deletion status
        """
        try:
            session_manager = await _get_session_manager_func()
            success = await session_manager.delete_session(session_id)

            if success:
                return {"status": "success", "message": "Session deleted"}
            else:
                return {"status": "error", "error": "Session not found"}
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def list_mcp_sessions(limit: int = 100) -> dict:
        """
        List all active MCP sessions.

        Args:
            limit: Maximum number of sessions to return (default: 100)

        Returns:
            dict: List of active sessions
        """
        try:
            session_manager = await _get_session_manager_func()
            sessions = await session_manager.list_sessions(limit)

            return {
                "status": "success",
                "count": len(sessions),
                "sessions": sessions
            }
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return {"status": "error", "error": str(e)}

    return [create_mcp_session, get_mcp_session, update_mcp_session, delete_mcp_session, list_mcp_sessions]
