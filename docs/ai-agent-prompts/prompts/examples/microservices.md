# Example: Microservices Architecture Adaptation

## Scenario

**Input:** A microservices-based e-commerce platform

**Project Structure:**
```
ecommerce-platform/
├── services/
│   ├── user-service/        # Python/FastAPI
│   │   ├── app/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── product-service/     # Node.js/Express
│   │   ├── src/
│   │   ├── package.json
│   │   └── Dockerfile
│   ├── order-service/       # Go
│   │   ├── cmd/
│   │   ├── go.mod
│   │   └── Dockerfile
│   └── notification-service/ # Node.js
│       ├── src/
│       └── package.json
├── shared/
│   ├── proto/              # gRPC definitions
│   ├── config/             # Shared config
│   └── libs/              # Shared libraries
├── infrastructure/
│   ├── docker-compose.yml
│   ├── kubernetes/
│   └── terraform/
├── api-gateway/            # Kong or nginx
└── README.md
```

---

## Running the Adapter

```bash
claude "Using prompts/universal-adapter.md, analyze this microservices project"
```

---

## Generated Output

### ANALYSIS-EcommercePlatform.md

```markdown
# Project Analysis: E-Commerce Platform

## Overview

Microservices-based e-commerce platform with 4 services,
shared protobuf definitions, Kubernetes deployment, and API Gateway.

## Technology Stack

### Services

| Service | Language | Framework | Port | Purpose |
|---------|----------|-----------|------|---------|
| user-service | Python | FastAPI | 8001 | User management, auth |
| product-service | Node.js | Express | 8002 | Product catalog |
| order-service | Go | Chi | 8003 | Order processing |
| notification-service | Node.js | Express | 8004 | Email/push notifications |

### Infrastructure

| Component | Technology | Notes |
|-----------|-----------|-------|
| API Gateway | Kong / Nginx | Routes traffic to services |
| Communication | REST + gRPC | Via shared/proto |
| Database | PostgreSQL | Per-service |
| Message Queue | RabbitMQ | Async communication |
| Container | Docker | Per-service images |
| Orchestration | Kubernetes | Production deployment |
| IaC | Terraform | Cloud infrastructure |

## Architecture

```
                    ┌─────────────┐
                    │  API Gateway │
                    │   (Kong)     │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ user-service │   │product-service│   │order-service│
│   (Python)   │   │  (Node.js)   │   │    (Go)     │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  PostgreSQL │   │  PostgreSQL │   │  PostgreSQL │
└─────────────┘   └─────────────┘   └─────────────┘
       │
       ▼
┌─────────────┐
│notification- │
│  service    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  RabbitMQ   │
└─────────────┘
```

## Service Details

### User Service (Port 8001)
- **Path:** `services/user-service/`
- **Language:** Python 3.11, FastAPI
- **Database:** PostgreSQL (users, sessions)
- **Auth:** JWT tokens
- **API:** REST `/api/v1/users/*`

### Product Service (Port 8002)
- **Path:** `services/product-service/`
- **Language:** Node.js 20, Express
- **Database:** PostgreSQL (products, categories)
- **API:** REST `/api/v1/products/*`

### Order Service (Port 8003)
- **Path:** `services/order-service/`
- **Language:** Go 1.21
- **Database:** PostgreSQL (orders, line_items)
- **API:** REST `/api/v1/orders/*`

### Notification Service (Port 8004)
- **Path:** `services/notification-service/`
- **Language:** Node.js 20
- **Queue:** RabbitMQ consumer
- **Sends:** Email, push notifications

## Communication Patterns

### Synchronous (REST)
- API Gateway → Services
- Frontend → API Gateway

### Asynchronous (RabbitMQ)
- order-service → notification-service
- Events: `order.created`, `order.shipped`

### Shared Components

| Component | Path | Purpose |
|-----------|------|---------|
| Protobuf | `shared/proto/` | gRPC definitions |
| Config | `shared/config/` | Shared configuration |
| Libraries | `shared/libs/` | Common code |

## Development Setup

### Prerequisites
- Docker + Docker Compose
- Go 1.21
- Node.js 20
- Python 3.11
- kubectl (for K8s)

### Running Locally
```bash
# Start infrastructure only
docker-compose -f infrastructure/docker-compose.yml up -d

# Start all services
docker-compose up -d

# Or start individual services
cd services/user-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### Testing
```bash
# Run all service tests
docker-compose exec user-service pytest
docker-compose exec product-service npm test
docker-compose exec order-service go test ./...

# Integration tests
docker-compose -f docker-compose.test.yml up -d
```

## Key Files

1. **`infrastructure/docker-compose.yml`** — Local dev environment
2. **`services/user-service/app/main.py`** — User service entry
3. **`shared/proto/*.proto`** — gRPC definitions
4. **`api-gateway/kong.yml`** — API routing rules

## Common Gotchas

- **Service Discovery:** Use Docker network names in development
- **Databases:** Each service has its own PostgreSQL schema
- **Messaging:** Queue must be running for async features
- **Ports:** Watch for port conflicts in local dev

## Risks & Gaps

| Issue | Severity | Recommendation |
|-------|----------|----------------|
| No service mesh | Medium | Consider Istio for production |
| No distributed tracing | High | Add Jaeger |
| No circuit breakers | Medium | Add resilience patterns |
| Documentation spread | Medium | Centralize API docs |

## Next Steps

1. **Start infrastructure:** `docker-compose -f infrastructure/docker-compose.yml up -d`
2. **Start services:** `docker-compose up -d` (all) or individually
3. **Test health:** `curl localhost:8001/health`, etc.
4. **Read API Gateway:** `api-gateway/kong.yml` for routing
5. **Explore one service:** Start with `user-service/`
```

---

## Key Insights

### What the Adapter Identified

1. **4 distinct services** with different languages
2. **REST + async** communication patterns
3. **Shared infrastructure** (protobuf, config)
4. **Kubernetes + Terraform** for production
5. **Per-service databases**

### Architecture Diagram

The adapter created a visual architecture showing:
- Service-to-gateway relationships
- Database ownership
- Message queue for async

---

## Follow-up Questions

> "How do services communicate?"

> "What's the deployment process?"

> "How do I add a new service?"

---

**See also:**
- [Python Example](python.md)
- [Node.js Example](nodejs.md)
- [Go Example](go.md)
