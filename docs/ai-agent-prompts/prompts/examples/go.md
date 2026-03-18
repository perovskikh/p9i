# Example: Go Microservice Adaptation

## Scenario

**Input:** A Go REST API service

**Project Structure:**
```
my-service/
├── cmd/
│   └── server/
│       └── main.go          # Entry point
├── internal/
│   ├── handler/
│   │   └── users.go        # HTTP handlers
│   ├── service/
│   │   └── user_service.go # Business logic
│   ├── repository/
│   │   └── user_repo.go    # Database access
│   └── model/
│       └── user.go          # Data models
├── pkg/
│   └── config/
│       └── config.go        # Configuration
├── migrations/
├── docker/
│   └── Dockerfile
├── go.mod
├── go.sum
└── docker-compose.yml
```

---

## Running the Adapter

```bash
claude "Using prompts/universal-adapter.md, analyze this Go project"
```

---

## Generated Output

### ANALYSIS-MyGoService.md

```markdown
# Project Analysis: My Go Service

## Overview

Go REST API service using standard library or Chi router with PostgreSQL.
Follows standard Go project layout (cmd/internal/pkg).

## Technology Stack

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| Language | Go | 1.21 | From go.mod |
| Router | Chi | 5.4 | Lightweight router |
| Database | PostgreSQL | 15 | pgx driver |
| ORM | GORM | 1.25 | Or raw SQL |
| Auth | JWT | - | golang-jwt |
| Testing | Go testing | - | Built-in |
| Docker | Multi-stage | - | Optimized image |

## Architecture

```
HTTP Request
    ↓
Chi Router (cmd/server/main.go)
    ↓
Handler (internal/handler/)
    ↓
Service (internal/service/)
    ↓
Repository (internal/repository/)
    ↓
PostgreSQL
```

## Key Components

| Component | Path | Purpose |
|-----------|------|---------|
| Entry | `cmd/server/main.go` | Server startup, router setup |
| Handlers | `internal/handler/` | HTTP request/response |
| Services | `internal/service/` | Business logic |
| Repository | `internal/repository/` | Database operations |
| Models | `internal/model/` | Data structures |
| Config | `pkg/config/` | Configuration loading |

## Development Setup

### Prerequisites
- Go 1.21+
- PostgreSQL 15+
- Docker (optional)

### Installation
```bash
# Download dependencies
go mod download

# Copy environment
cp .env.example .env

# Run migrations
go run cmd/server/main.go migrate
```

### Running Locally
```bash
# Development
go run cmd/server/main.go

# With Docker
docker-compose up -d

# Production
go build -o server ./cmd/server
./server
```

### Testing
```bash
# Run tests
go test ./...

# With coverage
go test -cover ./...

# Specific package
go test ./internal/handler/ -v
```

### API
- Base URL: http://localhost:8080
- Health: http://localhost:8080/health

## Key Files

1. **`cmd/server/main.go`** — Application entry, routing
2. **`internal/handler/users.go`** — HTTP handlers
3. **`internal/service/user_service.go`** — Business logic
4. **`internal/repository/user_repo.go`** — DB queries
5. **`pkg/config/config.go`** — Config loading

## Common Gotchas

- **Go Modules:** Always work inside the module directory
- **Dependencies:** Use `go.mod` and `go.sum`, never vendor
- **Context:** Pass context.Context through all layers
- **Errors:** Return errors with context, don't log and continue

## Risks & Gaps

| Issue | Severity | Recommendation |
|-------|----------|----------------|
| No graceful shutdown | High | Add signal handling |
| Limited tests | Medium | Add integration tests |
| No API versioning | Low | Consider /v1 prefix |

## Next Steps

1. `go mod download` to fetch dependencies
2. Set up PostgreSQL: `docker-compose up -d db`
3. Run: `go run cmd/server/main.go`
4. Check health: `curl localhost:8080/health`
5. Read `cmd/server/main.go` for routing
```

---

## Follow-up Questions

> "How do I add a new endpoint?"

> "What's the error handling pattern?"

> "How do I run database migrations?"

---

**See also:**
- [Python Example](python.md)
- [Node.js Example](nodejs.md)
- [Microservices Example](microservices.md)
