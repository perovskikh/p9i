# MCP Proxy Setup for p9i

This guide explains how to set up the MCP proxy to connect Claude Code to the remote p9i MCP server.

## Quick Start

### 1. Copy `.mcp.json` to your project

Create or update `.mcp.json` in your project root:

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

Replace `/path/to/p9i` with the actual path to your p9i installation.

### 2. Run Claude Code

Start Claude Code in the project directory. It should detect the MCP server from `.mcp.json`.

## Alternative: Environment Variables

You can also set environment variables in your shell:

```bash
export MCP_PROXY_URL=http://mcp.coderweb.ru/mcp
export P9I_API_KEY=sk-p9i-codeshift-mcp.coderweb.ru
```

Then run the proxy manually:

```bash
python3 mcp_proxy_simple.py
```

## Troubleshooting

### "Session not found" error

This occurs when using HTTP transport directly without the proxy. Make sure you're using the proxy.

### MCP server not detected

- Ensure `.mcp.json` is in the project root
- Check that the path to `mcp_proxy_simple.py` is correct
- Verify Python is in your PATH

### Connection refused

Check that the MCP server is running:
```bash
curl http://mcp.coderweb.ru/mcp
```

Should return JSON-RPC error (normal) but not connection refused.

## Files

- `mcp_proxy_simple.py` - Simple curl-based proxy (recommended)
- `mcp_proxy.py` - Alternative version with more features

## Architecture

```
Claude Code (stdio) --> mcp_proxy.py --> HTTP --> mcp.coderweb.ru/mcp
```