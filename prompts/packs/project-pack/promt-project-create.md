# Project Creation Prompt

## Purpose
Create a new project in p9i with optional SFTP configuration for remote access.

## When to Use
- User wants to add a new client project to the p9i SaaS platform
- Setting up a new development environment
- Onboarding a new customer project

## Workflow

### Step 1: Gather Project Information

Ask the user for:
- **Project name**: Unique identifier (e.g., "acme-frontend")
- **Description**: Brief project description
- **Owner ID**: User or organization identifier
- **SFTP Configuration** (optional):
  - `sftp_host`: Server IP or hostname
  - `sftp_port`: SSH port (default: 22)
  - `sftp_username`: SSH username
  - `sftp_project_path`: Remote path to project directory

### Step 2: Create Project via MCP

```python
result = await p9i.create_project(
    name="acme-frontend",
    description="Acme Corp frontend application",
    owner_id="user_123",
    sftp_host="45.67.89.10",      # Optional
    sftp_port=22,
    sftp_username="developer",
    sftp_project_path="/home/dev/acme",
    default_project_path="/project"
)
```

### Step 3: Create API Key

```python
# Create API key for the project
api_key, raw_key = await p9i.create_project_api_key(
    project_id=result["id"],
    name="Development Key",
    permissions=["read_prompts", "run_prompt", "explorer_search"],
    rate_limit=100
)
```

### Step 4: Provide Credentials

Return to user:
- `project_id`: UUID for future reference
- `api_key`: Raw API key (show ONLY once!)
- `mcp_config`: Ready-to-use MCP configuration snippet

## Response Template

```
## Project Created ✅

**Project ID**: `{project_id}`
**Name**: `{name}`
**API Key**: `{raw_key}` ⚠️ Save this now - it won't be shown again!

### MCP Configuration

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "p9i": {
      "command": "python3",
      "args": ["/path/to/p9i_stdio_bridge.py"],
      "env": {
        "P9I_API_KEY": "{raw_key}",
        "P9I_PROJECT_ID": "{project_id}"
      }
    }
  }
}
```

### Next Steps

1. Save the API key securely
2. Configure Claude Code to use the project
3. Run `adapt_to_project` to connect
```

## Error Handling

| Error | Solution |
|-------|----------|
| Project name already exists | Ask user for different name |
| SFTP connection failed | Verify host/credentials, retry without SFTP |
| Invalid permissions | Check permission list against allowed values |

## Permissions Reference

| Permission | Description |
|------------|-------------|
| `read_prompts` | Read prompt library |
| `run_prompt` | Execute prompts |
| `run_prompt_chain` | Execute prompt chains |
| `explorer_search` | Search project code |
| `explorer_index` | Rebuild project index |
| `reviewer_*` | All reviewer tools |
| `*` | All permissions (admin) |
