# AI Agent Prompt: GitHub MCP Integration

**Version:** 1.0
**Date:** 2026-03-21
**Purpose:** Интеграция с GitHub MCP для управления PR, issues, CI/CD

---

## Overview

GitHub MCP Server позволяет AI агентам:
- Управлять репозиториями (чтение кода, файлов, коммитов)
- Работать с Issues и PR (создание, обновление, мердж)
- Анализировать CI/CD (GitHub Actions, workflow runs)
- Анализировать безопасность (Dependabot alerts)

---

## Environment Variables

```bash
# .env
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_MCP_URL=https://api.githubcopilot.com/mcp/
```

---

## MCP Tools Available

| Tool | Description |
|------|-------------|
| `github_list_repositories` | Список доступных репозиториев |
| `github_search_code` | Поиск кода в репозитории |
| `github_list_issues` | Список issues с фильтрами |
| `github_create_issue` | Создать новую issue |
| `github_update_issue` | Обновить issue |
| `github_list_pulls` | Список pull requests |
| `github_create_pull` | Создать PR |
| `github_merge_pull` | Замерджить PR |
| `github_list_actions` | Список GitHub Actions |
| `github_get_workflow_run` | Получить статус workflow |
| `github_list_deployments` | Список deployments |
| `github_get_dependabot_alerts` | Dependabot alerts |

---

## Workflow Examples

### 1. Создание Issue
```
Используя GitHub MCP, создай issue в репозитории owner/repo:
- Title: "Bug: API returns 500 on /users endpoint"
- Labels: bug, priority-high
- Assignee: @developer
```

### 2. Анализ PR
```
Проанализируй PR #123 в репозитории owner/repo:
- Проверь changed files
- Оставь review comments
- Approve или Request changes
```

### 3. CI/CD Мониторинг
```
Проверь статус workflow run для последнего commit в owner/repo:
- Покажи результаты
- Если failed - покажи error logs
```

### 4. Создание PR
```
Создай pull request:
- Из branch: feature/new-api
- В branch: main
- Title: "Add new API endpoint for users"
- Description: ## Summary\n- Added GET /users endpoint\n## Tests\n- Added unit tests
```

---

## Implementation

```python
import httpx

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MCP_URL = os.getenv("GITHUB_MCP_URL", "https://api.githubcopilot.com/mcp/")

async def github_mcp_call(method: str, params: dict) -> dict:
    """Call GitHub MCP tool."""
    response = await httpx.post(
        GITHUB_MCP_URL,
        json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": method,
                "arguments": params
            },
            "id": 1
        },
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Content-Type": "application/json"
        }
    )
    return response.json()
```

---

## Error Handling

| Error | Solution |
|-------|----------|
| 401 Unauthorized | Проверь GITHUB_TOKEN |
| 403 Forbidden | Проверь права токена (repo, workflow) |
| 404 Not Found | Проверь owner/repo название |
| Rate Limited | Подожди или используй другой токен |

---

user:
Выполни GitHub MCP операцию: [описание задачи]