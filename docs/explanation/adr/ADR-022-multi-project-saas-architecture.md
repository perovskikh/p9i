# ADR-022: Multi-Project SaaS Architecture

## Status

**Proposed** - 2026-04-03

## Context

p9i MCP server needs to serve hundreds of different client projects simultaneously. Each project requires:
- Isolated project context and prompt overrides
- Per-project API keys with rate limiting
- Remote project access via SFTP (client machines vary)
- Session binding to specific projects

Current architecture assumes single-project usage. We need multi-tenant SaaS capabilities.

## Decision

Implement database-backed multi-project architecture with the following components:

### 1. Project Entity (SQLAlchemy)

```python
class Project(Base):
    __tablename__ = "projects"

    id: UUID (PK)
    name: str
    description: str

    # SFTP Configuration (for remote projects)
    sftp_host: str (nullable)
    sftp_port: int (default 22)
    sftp_username: str (nullable)
    sftp_key_fingerprint: str (nullable)
    sftp_project_path: str (nullable)

    # Local fallback
    default_project_path: str = "/project"
    stack: JSON = []  # detected technologies

    owner_id: str (indexed)
    metadata: JSON = {}
    is_active: bool = True

    created_at: datetime
    updated_at: datetime

    # Relationships
    api_keys: List["ApiKey"]
```

### 2. ApiKey Entity (SQLAlchemy)

```python
class ApiKey(Base):
    __tablename__ = "api_keys"

    id: UUID (PK)
    key_hash: str (SHA256, indexed, unique)
    project_id: UUID (FK -> projects.id)

    name: str
    permissions: JSON = []  # ["read_prompts", "run_prompt", ...]
    rate_limit: int = 100  # requests per minute

    is_active: bool = True
    created_at: datetime
    last_used_at: datetime
```

### 3. Prompt Tier System (Extended)

Existing tiers (from ADR-002):

| Tier | Path | Purpose |
|------|------|---------|
| Tier 0: CORE | `prompts/core/` | Immutable baseline (SHA256 locked) |
| Tier 1: UNIVERSAL | `prompts/universal/` | General purpose prompts |
| Tier 2: PACKS | `prompts/packs/` | Plugin packs (k8s, ci-cd, etc.) |

**NEW Tier 3: PROJECTS**

| Tier | Path | Purpose |
|------|------|---------|
| Tier 3: PROJECTS | `prompts/projects/{project_id}/` | Project-specific overrides |

**Cascade Resolution**: `PROJECTS → PACKS → UNIVERSAL → CORE`

### 4. Project Service

```python
class ProjectService:
    async def create_project(data: CreateProjectDTO) -> Project
    async def get_project(project_id: str) -> Optional[Project]
    async def list_projects(owner_id: str) -> List[Project]
    async def update_project(project_id: str, data: UpdateProjectDTO) -> Project
    async def delete_project(project_id: str) -> bool

    async def create_api_key(project_id: str, name: str, permissions: List[str]) -> tuple[ApiKey, str]
    async def validate_api_key(raw_key: str) -> Optional[ApiKey]
    async def revoke_api_key(key_id: str) -> bool

    async def connect_sftp(project_id: str) -> SFTPFilesystem
    async def disconnect_sftp(project_id: str) -> None
```

### 5. MCP Tools

| Tool | Purpose |
|------|---------|
| `create_project` | Create new project with SFTP config |
| `get_project` | Get project details |
| `list_projects` | List user's projects |
| `update_project` | Update project configuration |
| `delete_project` | Deactivate project |
| `create_project_api_key` | Create API key for project |
| `revoke_project_api_key` | Revoke API key |
| `adapt_to_project` | Connect to project (enhanced) |

### 6. Session-to-Project Binding

Session state includes `project_id` for context:

```python
session = {
    "project_id": "proj_abc123",
    "client_info": {...},
    "state": {...}
}
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    K3s p9i SaaS Platform                            │
│                                                                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐            │
│  │  Client 1  │    │  Client 2  │    │  Client N  │            │
│  │  SFTP/CI   │    │  SFTP/CI   │    │  SFTP/CI   │            │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘            │
│         │                   │                   │                    │
│         └───────────────────┼───────────────────┘                    │
│                             │                                        │
│                    ┌────────┴────────┐                              │
│                    │   MCP Server    │                              │
│                    │  ProjectService │                              │
│                    └────────┬────────┘                              │
│                             │                                        │
│              ┌──────────────┼──────────────┐                         │
│              │              │              │                         │
│        ┌─────┴─────┐ ┌─────┴─────┐ ┌─────┴─────┐                  │
│        │PostgreSQL │ │   Redis   │ │  SFTP     │                  │
│        │ projects  │ │  cache    │ │  pools    │                  │
│        │  api_keys │ │  sessions │ │  per host │                  │
│        └───────────┘ └───────────┘ └───────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
```

## Consequences

### Positive
- Multi-tenant SaaS with project isolation
- Per-project API keys with rate limiting
- Remote project access via SFTP
- Project-scoped prompt overrides
- Unified project management

### Negative
- Database dependency for core operations
- More complex deployment
- SFTP connection management overhead

### Neutral
- Existing single-project mode still works
- API keys via env vars still supported (legacy)

## Alternatives Considered

### Option 1: API Key per Environment Variable
- **Pros**: Simple, no DB changes
- **Cons**: Not scalable, no per-project isolation, no SFTP
- **Decision**: Rejected - doesn't meet SaaS requirements

### Option 2: Git-based Project Access
- **Pros**: No SFTP needed, version control
- **Cons**: Requires git credentials, not real-time
- **Decision**: Deferred - future enhancement

### Option 3: NFS/EFS Volume Mounts
- **Pros**: Fast, persistent
- **Cons**: Complex networking, single region, cost
- **Decision**: Deferred - use SFTP for remote access

## Implementation Plan

| Phase | Component | Status |
|-------|-----------|--------|
| 1 | SQLAlchemy Models (Project, ApiKey) | ✅ |
| 2 | Repositories | ✅ |
| 3 | ProjectService | ✅ |
| 4 | MCP Tools | Pending |
| 5 | Session Binding | Pending |
| 6 | Project Pack Prompts | Pending |

## References

- [ADR-002: Tiered Prompt Architecture](./ADR-002-tiered-prompt-architecture-mpv-integration.md)
- [ADR-007: Multi-Agent Orchestrator](./ADR-007-multi-agent-orchestrator.md)
- [ADR-020: Coordinator Pattern](./ADR-020-coordinator-pattern-and-volume-mounts.md)

## Related ADRs

- Supersedes: None
- Related: ADR-002, ADR-007, ADR-020
