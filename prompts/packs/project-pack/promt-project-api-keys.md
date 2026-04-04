# Project API Keys Management Prompt

## Purpose
Create, list, validate, and revoke API keys for project access.

## When to Use
- User needs to generate a new API key for a project
- Rotating API keys for security
- Auditing API key usage
- Revoking compromised keys

## API Key Structure

```
sk-p9i-{random_32_chars_base64url}
```

Example: `sk-p9i-Xf8Km2Yz9PqR3vN5wL7jH1sdT6uI0kMl4`

The key is hashed (SHA256) before storage. The raw key is only shown once at creation.

## Workflows

### Create New API Key

```python
api_key, raw_key = await p9i.create_project_api_key(
    project_id="proj_xxx",
    name="Production Access",
    permissions=["read_prompts", "run_prompt"],
    rate_limit=100
)
```

**Response:**
```
## API Key Created ✅

**Key ID**: {api_key.id}
**Name**: Production Access
**Key**: `{raw_key}` ⚠️ Save now!

**Permissions**: read_prompts, run_prompt
**Rate Limit**: 100 req/min

Store securely - this key won't be shown again.
```

### List Project API Keys

```python
keys = await p9i.list_project_api_keys(project_id="proj_xxx")
```

**Response:**
```
## API Keys for {project_name}

| ID | Name | Permissions | Rate | Created | Last Used |
|----|------|-------------|------|---------|-----------|
| xxx | Dev Key | read_prompts, run_prompt | 100 | 2026-04-01 | 2026-04-03 |
| yyy | CI Key | read_prompts | 50 | 2026-04-02 | never |

Total: 2 active keys
```

### Revoke API Key

```python
result = await p9i.revoke_project_api_key(key_id="xxx")
```

**Response:**
```
## API Key Revoked ✅

Key "{name}" has been deactivated.
Any requests using this key will now fail.
```

### Validate API Key (Internal)

p9i validates API keys automatically on each request:

```python
# Called internally by middleware
api_key = await p9i.validate_api_key(raw_key)

if api_key:
    # Check rate limit
    if await p9i.check_rate_limit(api_key.id):
        # Process request
    else:
        # Rate limited
        raise RateLimitExceeded()
else:
    # Invalid or revoked
    raise Unauthorized()
```

## Rate Limiting

| Tier | Rate Limit | Permissions |
|------|------------|-------------|
| Free | 60 req/min | read_prompts |
| Pro | 100 req/min | read_prompts, run_prompt |
| Enterprise | 500 req/min | * |

Rate limits are enforced per API key using Redis sliding window.

## Security Best Practices

1. **One key per use case**
   - Separate keys for dev, CI, production
   - Easier to revoke compromised keys

2. **Principle of least privilege**
   - Only grant required permissions
   - CI systems need read_prompts, not admin

3. **Key rotation**
   - Rotate keys quarterly
   - Immediately revoke if compromised

4. **Secure storage**
   - Use secret managers (Vault, AWS Secrets Manager)
   - Never commit keys to git

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `invalid_key` | Key doesn't exist or revoked | Generate new key |
| `rate_exceeded` | Too many requests | Wait or increase limit |
| `project_inactive` | Project deleted/suspended | Contact support |
| `insufficient_permissions` | Key lacks required permission | Create new key with proper permissions |

## Audit Log

API key operations are logged:

```python
# Internal audit
logger.info(f"API key {key_id} used by {request.origin}")
logger.info(f"API key {key_id} created by {user_id}")
logger.warning(f"Failed API key attempt from {ip}")
```

Access logs include:
- Timestamp
- API key ID (not the key itself)
- Operation performed
- Source IP
- Success/failure
