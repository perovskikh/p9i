# MCP Proxy Setup for p9i

This guide explains how to set up the MCP proxy to connect Claude Code to the remote p9i MCP server.

## Two Connection Options

### Option A: HTTP-to-STDIO Proxy (Recommended for Claude Code)

Uses `p9i_stdio_bridge.py` to bridge Claude Code (stdio) to MCP server (HTTP).

**Pros:**
- Simple setup
- Handles session management automatically
- Works reliably with Claude Code

**Cons:**
- Additional process running

### Option B: Direct HTTP Connection (Production)

Direct connection without proxy, using server-side session management.

**Pros:**
- No proxy process needed
- Lower latency
- Server-side sessions persist across reconnections

**Cons:**
- Requires session creation step

---

## Option A: Proxy Setup (Recommended)

### 1. Copy `.mcp.json` to your project

Create or update `.mcp.json` in your project root:

```json
{
  "p9i": {
    "command": "python3",
    "args": ["/path/to/p9i/p9i_stdio_bridge.py"],
    "env": {
      "MCP_PROXY_URL": "http://mcp.coderweb.ru/mcp",
      "P9I_API_KEY": "sk-p9i-codeshift-mcp.coderweb.ru"
    }
  }
}
```

Replace `/path/to/p9i` with the actual path to your p9i installation.

### 2. Run Claude Code

Start Claude Code in the project directory. It should detect the MCP server from `.mcp.json`.

## Option B: Direct HTTP Connection

For production setups, you can connect directly without the proxy.

### 1. Create a Session

First, create an MCP session using the `create_mcp_session` tool:

```python
# Or via curl:
curl -X POST http://mcp.coderweb.ru/mcp \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk-p9i-codeshift-mcp.coderweb.ru" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "create_mcp_session",
      "arguments": {}
    }
  }'
```

The response will include a `session_id`:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\"status\": \"success\", \"session_id\": \"abc-123...\", \"message\": \"...\"}"
    }]
  }
}
```

### 2. Use Session ID in Requests

For all subsequent requests, include the session ID:

```bash
curl -X POST http://mcp.coderweb.ru/mcp \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk-p9i-codeshift-mcp.coderweb.ru" \
  -H "Mcp-Session-Id: abc-123..." \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", ...}'
```

### Session Management Tools

The server provides these session tools:

| Tool | Description |
|------|-------------|
| `create_mcp_session` | Create new session |
| `get_mcp_session` | Get session info |
| `update_mcp_session` | Update session state |
| `delete_mcp_session` | Delete session |
| `list_mcp_sessions` | List active sessions |

---

## Alternative: Environment Variables

You can also set environment variables in your shell:

```bash
export MCP_PROXY_URL=http://mcp.coderweb.ru/mcp
export P9I_API_KEY=sk-p9i-codeshift-mcp.coderweb.ru
```

Then run the proxy manually:

```bash
python3 p9i_stdio_bridge.py
```

## Troubleshooting

### "Session not found" error

- **With proxy (Option A)**: This is normal on first request, proxy handles it automatically
- **Without proxy (Option B)**: Create a session first using `create_mcp_session`

### MCP server not detected

- Ensure `.mcp.json` is in the project root
- Check that the path to `p9i_stdio_bridge.py` is correct
- Verify Python is in your PATH

### Connection refused

Check that the MCP server is running:
```bash
curl http://mcp.coderweb.ru/mcp
```

Should return JSON-RPC error (normal) but not connection refused.

## Architecture

```
Option A (Proxy):
Claude Code (stdio) --> p9i_stdio_bridge.py --> HTTP --> mcp.coderweb.ru/mcp

Option B (Direct):
Claude Code --> HTTP --> mcp.coderweb.ru/mcp (with session management)
```

## Files

- `p9i_stdio_bridge.py` - Simple curl-based proxy (Option A)
- `mcp_proxy.py` - Alternative version with more features
- `src/services/mcp_session_manager.py` - Session management (Option B)