# AI Agent Prompt: GitMCP Integration

**Version:** 1.0
**Date:** 2026-03-21
**Purpose:** Интеграция с GitMCP для понимания чужих репозиториев и документации

---

## Overview

GitMCP — бесплатный MCP сервер для доступа к документации и коду любого GitHub проекта.

**Цель:** Предотвратить hallucinations при работе с незнакомыми библиотеками/репозиториями.

---

## Environment Variables

```bash
# .env
# GitMCP не требует токена - использует публичный доступ
GITMCP_ENABLED=true
```

---

## GitMCP URLs

| Type | URL Format | Example |
|------|------------|---------|
| Specific repo | `https://gitmcp.io/{owner}/{repo}` | `https://gitmcp.io/fastapi/fastapi` |
| Generic | `https://gitmcp.io/docs` | Для переключения между репозиториями |

---

## MCP Tools Available

| Tool | Description |
|------|-------------|
| `search_code` | Поиск кода в репозитории |
| `get_file_contents` | Чтение файлов |
| `get_directory_tree` | Структура директорий |
| `search_documentation` | Поиск в документации |
| `get_readme` | Получить README |
| `get_api_docs` | Получить API документацию |
| `get_dependencies` | Получить зависимости (package.json, requirements.txt) |

---

## Use Cases

### 1. Изучение незнакомой библиотеки
```
Используя GitMCP, изучи библиотеку facebook/react:
- Покажи структуру проекта
- Найди как использовать useState hook
- Покажи примеры кода из реальных файлов
```

### 2. Понимание API
```
Получи документацию по Supabase JS:
- Как создать таблицу
- Как сделать запрос к базе
- Примеры аутентификации
```

### 3. Анализ зависимостей
```
Проверь зависимости проекта owner/repo:
- Какие версии Node.js/React используются
- Какие есть peer dependencies
- Есть ли устаревшие пакеты
```

### 4. Изучение архитектуры
```
Проанализируй архитектуру проекта vercel/next.js:
- Структура директорий
- Главные модули
- Как организован роутинг
```

---

## Implementation

```python
import httpx

GITMCP_URL = "https://gitmcp.io/{owner}/{repo}"

async def gitmcp_call(tool: str, params: dict) -> dict:
    """Call GitMCP tool."""
    response = await httpx.post(
        f"https://gitmcp.io/{params.get('owner')}/{params.get('repo')}/mcp",
        json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool,
                "arguments": params
            },
            "id": 1
        },
        headers={"Content-Type": "application/json"}
    )
    return response.json()
```

---

## Best Practices

1. **Всегда используй GitMCP** для незнакомых библиотек
2. **Проверяй актуальность** — GitMCP берёт latest из GitHub
3. **Используй конкретные URL** для стабильности
4. **Комбинируй с Context7** — GitMCP для кода, Context7 для документации

---

## Compared to Context7

| Feature | GitMCP | Context7 |
|---------|--------|----------|
| Source | GitHub repos | Official docs |
| Use case | Понимание конкретного repo | Best practices для библиотеки |
| Updates | Real-time from GitHub | Специально обработанные docs |
| Coverage | Любой public repo | 50+ популярных библиотек |

---

user:
Изучи репозиторий [owner/repo] используя GitMCP: [вопрос]