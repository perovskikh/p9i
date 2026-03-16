# MCP Servers Configuration

## Claude Code Integration

Добавь в `~/.claude/settings.json` или настройки проекта:

```json
{
  "mcpServers": {
    "ai-prompt-system": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "perovskikh/ai-prompt-system"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@context7/mcp-server"]
    },
    "github": {
      "command": "uvx",
      "args": ["mcp-server-github", "--token", "${GITHUB_TOKEN}"],
      "env": {
        "GITHUB_TOKEN": "your-token-here"
      }
    }
  }
}
```

## Доступные MCP инструменты

### AI Prompt System (локальный)
- `run_prompt` — выполнить промт
- `run_prompt_chain` — выполнить цепочку
- `list_prompts` — список промтов
- `get_project_memory` — память проекта
- `save_project_memory` — сохранить память

### Context7 (документация)
- `resolve-library-id` — найти библиотеку
- `query-docs` — получить документацию

### GitHub (опционально)
- `get_issues` — получить issues
- `create_issue` — создать issue
- `search_code` — искать в коде

## Troubleshooting

### MCP не подключается
```bash
# Проверить статус
docker ps | grep ai-prompt-system

# Перезапустить
docker compose restart mcp-server
```

### Конфликт портов
```bash
# Изменить порт в docker-compose.yml
ports:
  - "8001:8000"
```