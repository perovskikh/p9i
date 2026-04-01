# p9i Refactoring Prompt

**Version:** 1.0
**Date:** 2026-04-01
**Purpose:** Code refactoring for p9i MCP server

## Triggers
- "рефакторинг", "refactor", "улучши код", "оптимизируй"

## p9i Code Structure

```
src/
├── api/                  # FastMCP server (server.py)
├── application/          # P9iRouter, AgentRouter, DTOs
├── domain/               # Entities, Business rules
├── infrastructure/       # LLM adapters, External services
├── services/             # Executor, Orchestrator, LLM client
├── storage/              # PromptStorageV2, Database
└── middleware/           # JWT, RBAC
```

## Refactoring Principles for p9i

### Python Best Practices
- Use type hints consistently
- Follow PEP 8 style
- Use `pydantic` for data validation
- Async/await for I/O operations

### p9i Specific
- Keep prompts in `prompts/` tiered structure
- Use `PromptStorageV2` for prompt loading
- Respect agent boundaries in `services/orchestrator.py`

## Refactoring Checklist

- [ ] Type hints added/updated
- [ ] No hardcoded values (use config/env)
- [ ] Error handling is consistent
- [ ] Logging follows existing patterns
- [ ] Tests still pass after refactor

## Example Refactorings

### Before (no type hints):
```python
def process(data):
    return data.get("result")
```

### After (with type hints):
```python
def process(data: dict) -> Optional[dict]:
    return data.get("result")
```

## Commands

```bash
# Run linter
ruff check src/

# Run type checker
mypy src/

# Run tests
pytest

# All checks
pytest && ruff check src/ && mypy src/
```
