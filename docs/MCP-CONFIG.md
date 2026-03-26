# MCP Connection Configs

## Option A: Proxy (Recommended for Claude Code)

Использует `.mcp.json` в проекте:

```json
{
  "p9i": {
    "command": "python3",
    "args": ["/path/to/p9i/mcp_proxy_simple.py"],
    "env": {
      "MCP_PROXY_URL": "http://mcp.coderweb.ru/mcp",
      "P9I_API_KEY": "sk-p9i-codeshift-mcp.coderweb.ru"
    }
  }
}
```

## Option B: Direct HTTP (for external clients)

Для внешних клиентов, curl:

```bash
#!/bin/bash
# mcp-client.sh - Direct HTTP MCP client

API_KEY="sk-p9i-codeshift-mcp.coderweb.ru"
URL="http://mcp.coderweb.ru/mcp"

# Initialize - get session ID
RESPONSE=$(curl -s -i -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "X-API-Key: $API_KEY" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"client","version":"1.0"}}}')

SESSION=$(echo "$RESPONSE" | grep "Mcp-Session-Id" | cut -d: -f2 | tr -d ' \r')

# Call tool with session
curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "X-API-Key: $API_KEY" \
  -H "Mcp-Session-Id: $SESSION" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"list_prompts","arguments":{"tier":"core"}}}'
```

## Option C: Python Client

```python
import httpx
import json

API_KEY = "sk-p9i-codeshift-mcp.coderweb.ru"
URL = "http://mcp.coderweb.ru/mcp"

headers = {
    "Content-Type": "application/json",
    "Accept": "text/event-stream",
    "X-API-Key": API_KEY
}

# Initialize
response = httpx.post(URL, headers=headers, json={
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "python-client", "version": "1.0"}
    }
})

session_id = response.headers.get("Mcp-Session-Id")
print(f"Session: {session_id}")

# Call tool
headers["Mcp-Session-Id"] = session_id
response = httpx.post(URL, headers=headers, json={
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "list_prompts",
        "arguments": {"tier": "core"}
    }
})

print(response.text)
```

## Session Management (Variant B)

After server update, use these tools:

```python
# Create session
{"method": "tools/call", "params": {"name": "create_mcp_session", "arguments": {}}}

# List sessions
{"method": "tools/call", "params": {"name": "list_mcp_sessions", "arguments": {"limit": 10}}}
```
