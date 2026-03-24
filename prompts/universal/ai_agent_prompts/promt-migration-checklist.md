# promt-migration-checklist.md
"""
Migration Checklist Prompt - for verifying migration completeness.

Use this prompt to check if migration is complete.
"""

## Context
You are verifying a code migration from old patterns (Legacy Pydantic models) to new patterns (Domain Entities).

## Task
Check these items:

### 1. Architecture Check
- [ ] Domain entities created in src/domain/entities/
- [ ] Domain exceptions created in src/domain/exceptions.py
- [ ] Storage updated to use entities

### 2. Import Check
- [ ] No circular dependencies
- [ ] All imports resolve correctly
- [ ] Backward compatibility maintained

### 3. Test Check
- [ ] Existing tests pass
- [ ] Backward compat tests pass
- [ ] Entity methods work correctly

### 4. Code Quality
- [ ] No duplicate code
- [ ] Old code marked as deprecated or removed
- [ ] Documentation updated

## Output Format
Return a JSON:
```json
{
  "status": "PASS|FAIL|WARNING",
  "checks": [...],
  "issues": [...]
}
```