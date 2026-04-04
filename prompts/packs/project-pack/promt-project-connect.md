# Project Connection Prompt

## Purpose
Connect to an existing project via SFTP or local mount for code exploration and prompt execution.

## When to Use
- User wants to work with an existing project
- Switching between projects
- Initial setup of Claude Code for a project

## Workflow

### Step 1: Get Project Details

```python
project = await p9i.get_project(project_id="proj_xxx")
```

### Step 2: Establish Connection

#### Option A: SFTP Connection (Remote Project)

```python
# Establish SFTP connection
sftp = await p9i.connect_sftp(project_id="proj_xxx")

# Verify connection
if sftp:
    files = await sftp.list_dir("/")
    print(f"Connected! Found {len(files)} items")
```

#### Option B: Local Project Path

```python
# Use default local path
project_path = project.default_project_path  # e.g., "/project"
```

### Step 3: Adapt to Project

```python
result = await p9i.adapt_to_project(
    project_path="/project",  # or remote SFTP path
    project_description=f"Working on {project.name}"
)
```

## MCP Configuration for Remote Projects

When using SFTP, the project code is accessed via p9i's SFTP bridge:

```json
{
  "mcpServers": {
    "p9i": {
      "command": "python3",
      "args": ["/path/to/p9i_stdio_bridge.py"],
      "env": {
        "P9I_API_KEY": "sk-p9i-xxx",
        "P9I_PROJECT_ID": "proj_xxx"
      }
    }
  }
}
```

The SFTP bridge handles remote file access transparently.

## Connection Status Check

```python
# Check if SFTP is connected
is_connected = await p9i.is_sftp_connected(project_id="proj_xxx")

# Get connection details
info = await p9i.get_project_connection_info(project_id="proj_xxx")
# Returns: {host, port, username, path, connected_at}
```

## Disconnect

```python
# Disconnect when done
await p9i.disconnect_sftp(project_id="proj_xxx")
```

## Error Handling

| Error | Solution |
|-------|----------|
| SFTP connection timeout | Check network/firewall, retry |
| Authentication failed | Verify SSH credentials |
| Path not found | Check `sftp_project_path` setting |
| Project not found | Verify `project_id` is correct |

## Response Template

```
## Connected to Project ✅

**Project**: {name}
**Connection**: {sftp_host or "local"}
**Path**: {project_path}
**Stack**: {stack technologies}

### Explorer Ready

Use these commands:

- `explorer_search("query")` - Search code
- `explorer_index()` - Rebuild index
- `reviewer_quality()` - Analyze code

### Prompts Available

Project-specific prompts override universal ones.
```

## Session Binding

Once connected, the session is bound to the project:
- All explorer operations use project path
- Prompts can access project context
- API keys scoped to project
