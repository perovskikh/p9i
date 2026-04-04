# p9i CLI

CLI для сборки и запуска p9i-AI Prompt System с API ключами из .env

## Использование

```bash
# Сборка образа с ключами из .env
python3 -m cli.main build

# Запуск в stdio режиме (без auth, для Claude Code)
python3 -m cli.main run

# Сборка + запуск
python3 -m cli.main start

# Управление JWT токенами
python3 -m cli.jwt generate --subject my-project --role developer
python3 -m cli.jwt validate <token>
```

## Режимы работы

| Режим | Auth | Описание |
|-------|------|----------|
| `run` (stdio) | ❌ Нет | Локальное подключение, доверенная сеть |
| HTTP (docker-compose) | ✅ JWT | `Authorization: Bearer <token>` |

## JWT Authentication (HTTP Mode)

Для HTTP доступа используется JWT аутентификация:

```bash
# Генерация токена
python3 -m cli.jwt generate --subject my-project --role developer

# Пример подключения в Claude Code
{
  "mcpServers": {
    "p9i": {
      "url": "https://p9i.ru/mcp",
      "headers": {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIs..."
      }
    }
  }
}
```

## Требования

- Docker
- .env файл с API ключами (MINIMAX_API_KEY, ZAI_API_KEY, и т.д.)
- Для JWT: JWT_SECRET и JWT_ADMIN_KEY в .env