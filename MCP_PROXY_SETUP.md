# MCP Proxy Setup

## Two Connection Options

### Option A: HTTP-to-STDIO Proxy (Recommended for Claude Code)

Uses `p9i_stdio_bridge.py` to bridge Claude Code (stdio) to MCP server (HTTP).

**Setup:**

```json
{
  "mcpServers": {
    "p9i": {
      "command": "python3",
      "args": ["/path/to/p9i/p9i_stdio_bridge.py"],
      "env": {
        "MCP_PROXY_URL": "https://mcp.coderweb.ru/mcp",
        "P9I_API_KEY": "sk-p9i-codeshift-mcp.coderweb.ru"
      }
    }
  }
}
```

### Option B: Direct HTTP Connection

Direct connection without proxy.

```json
{
  "mcpServers": {
    "p9i": {
      "type": "http",
      "url": "https://mcp.coderweb.ru/mcp",
      "headers": {
        "X-API-Key": "sk-p9i-codeshift-mcp.coderweb.ru"
      }
    }
  }
}
```

## Session Management

The server manages sessions via `Mcp-Session-Id` header. On first request, a session is created automatically.

### Session Tools

| Tool | Description |
|------|-------------|
| `create_mcp_session` | Create new session |
| `get_mcp_session` | Get session info |
| `update_mcp_session` | Update session state |
| `delete_mcp_session` | Delete session |
| `list_mcp_sessions` | List active sessions |

## Architecture

```
Option A (Proxy):
Claude Code (stdio) → p9i_stdio_bridge.py → HTTPS → mcp.coderweb.ru/mcp

Option B (Direct):
Claude Code → HTTPS → mcp.coderweb.ru/mcp
```

## Files

- `p9i_stdio_bridge.py` — STDIO-to-HTTP proxy bridge
- `src/services/mcp_session_manager.py` — Session management

## Troubleshooting

### "Session not found" error
- **With proxy (Option A)**: Normal on first request, proxy handles it automatically
- **Without proxy (Option B)**: Session is created automatically on first call

### MCP server not detected
1. Ensure `.mcp.json` is in the project root
2. Check path to `p9i_stdio_bridge.py` is correct
3. Verify Python is in your PATH
