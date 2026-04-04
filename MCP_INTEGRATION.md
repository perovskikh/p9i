# MCP Server Configuration

## Claude Code Integration

### HTTP Connection (Recommended for Remote)

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

### Local Development with p9i_stdio_bridge

For Claude Code stdio compatibility with remote server:

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

### Environment Variables

```bash
export MCP_PROXY_URL=https://mcp.coderweb.ru/mcp
export P9I_API_KEY=sk-p9i-codeshift-mcp.coderweb.ru
```

## K3s Deployment Architecture

```
Internet → Traefik (ingress) → p9i-p9i-xxx:8000 → PostgreSQL + Redis
```

Access via:
- MCP: `https://mcp.coderweb.ru/mcp`
- Health: `https://mcp.coderweb.ru/nginx-health`

## Available MCP Tools

### Core
- `p9i` — Unified router
- `run_prompt` / `run_prompt_chain` — Execute prompts
- `list_prompts` / `get_prompt` — List/retrieve prompts

### Project Management
- `create_project` / `get_project` / `list_projects`
- `adapt_to_project` — Auto-detect stack

### Memory
- `get_project_memory` / `save_project_memory`

### Authentication
- `generate_jwt_token` / `validate_jwt_token` / `revoke_jwt_token`
- `create_api_key` / `list_api_keys` / `revoke_api_key`

### Design
- `generate_tailwind` / `generate_shadcn` / `generate_textual`

## Troubleshooting

### "Session not found" error
This is normal on first request. The proxy handles session creation automatically.

### Connection refused
Check that the MCP server is running:
```bash
kubectl get pods -n p9i
kubectl logs -n p9i deployment/p9i --tail=50
```

### Check K3s Status
```bash
make status   # kubectl get all -n p9i
make watch    # kubectl logs -n p9i -f
```
