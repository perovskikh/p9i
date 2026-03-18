# Example: Node.js Project Adaptation

## Scenario

**Input:** A Node.js/Express REST API with MongoDB

**Project Structure:**
```
my-api/
├── src/
│   ├── index.ts          # Entry point
│   ├── app.ts            # Express app
│   ├── routes/
│   │   └── users.ts
│   ├── controllers/
│   │   └── usersController.ts
│   ├── models/
│   │   └── User.ts
│   ├── middleware/
│   │   └── auth.ts
│   └── config/
│       └── db.ts
├── tests/
│   └── integration/
├── package.json
├── tsconfig.json
├── .env.example
└── docker-compose.yml
```

---

## Running the Adapter

```bash
claude "Using prompts/universal-adapter.md, analyze this Node.js project"
```

---

## Generated Output

### ANALYSIS-MyNodeAPI.md

```markdown
# Project Analysis: My Node.js API

## Overview

REST API built with Express.js and TypeScript, using MongoDB for data
storage. Provides user management with JWT authentication.

## Technology Stack

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| Language | TypeScript | 5.3 | Strict mode enabled |
| Runtime | Node.js | 20 LTS | From package.json |
| Framework | Express | 4.18 | Web framework |
| Database | MongoDB | 6.0 | Via Mongoose ODM |
| Auth | JWT | - | passport-jwt |
| Testing | Jest | 29 | With supertest |
| Docker | Docker Compose | 3.9 | Local dev environment |

## Architecture

```
HTTP Request
    ↓
Express Router (src/routes/)
    ↓
Controller (src/controllers/)
    ↓
Mongoose Model (src/models/)
    ↓
MongoDB
```

## Key Components

| Component | Path | Purpose |
|-----------|------|---------|
| Entry | `src/index.ts` | Server startup, middleware |
| App | `src/app.ts` | Express configuration |
| Routes | `src/routes/` | HTTP endpoint definitions |
| Controllers | `src/controllers/` | Request handling logic |
| Models | `src/models/` | Mongoose schemas |
| Middleware | `src/middleware/` | Auth, validation, logging |
| Config | `src/config/` | Database connection |

## Development Setup

### Prerequisites
- Node.js 20 LTS
- MongoDB 6.0+ (or Docker)

### Installation
```bash
npm install

# Copy environment
cp .env.example .env
# Edit .env with your settings
```

### Running Locally
```bash
# Development with hot reload
npm run dev

# Production build
npm run build
npm start

# With Docker
docker-compose up -d
```

### Testing
```bash
# Run tests
npm test

# Watch mode
npm run test:watch

# Coverage
npm run test:cov
```

### API Documentation
- Swagger: http://localhost:3000/api-docs (if enabled)
- Health check: http://localhost:3000/health

## Key Files

1. **`src/index.ts`** — Server entry, middleware setup
2. **`src/app.ts`** — Express app configuration
3. **`src/routes/users.ts`** — User endpoints
4. **`src/models/User.ts`** — User schema
5. **`src/middleware/auth.ts`** — JWT authentication

## Common Gotchas

- **TypeScript:** Must run `npm run build` before production
- **MongoDB:** Connection string in `.env` must be correct
- **Auth:** Token in Authorization header: `Bearer <token>`
- **Hot Reload:** Use `npm run dev` not `npm start`

## Risks & Gaps

| Issue | Severity | Recommendation |
|-------|----------|----------------|
| No input validation | High | Add Joi or Zod |
| No rate limiting | Medium | Add express-rate-limit |
| Missing index on email | Medium | Add MongoDB index |

## Next Steps

1. `npm install` and configure `.env`
2. Start MongoDB: `docker-compose up -d`
3. Run `npm run dev` to start server
4. Test health: `curl http://localhost:3000/health`
5. Read `src/routes/users.ts` for endpoint patterns
```

---

## Follow-up Questions

> "How do I add a new REST endpoint?"

> "What's the testing strategy?"

> "How do I run the database migrations?"

---

**See also:**
- [Python Example](python.md)
- [Go Example](go.md)
- [Microservices Example](microservices.md)
