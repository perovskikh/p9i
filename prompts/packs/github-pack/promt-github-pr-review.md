# GitHub PR Review Automation

## Role
GitHub PR specialist. Automates PR reviews, checks, and management.

## Context
- Project: {project_path}
- PR: {pr_url}

## Instructions

Create or update `.github/workflows/pr-review.yml` that:

1. **Auto-assign reviewers** based on CODEOWNERS
2. **Check PR requirements**:
   - PR has description
   - PR size (no single files > 500 lines)
   - No merge commits in diff
   - Labels applied
3. **Run automated checks**:
   - Lint
   - Type check
   - Security scan (if applicable)

## PR Comment Actions

Support bot commands via comments:
- `/lgtm` - Approve
- `/request-review @user` - Request specific reviewer
- `/label bug` - Apply label
- `/close` - Close without merge

## Auto Merge

Enable auto-merge for:
- PRs passing all checks
- PRs with 2+ approvals
- Non-breaking changes

## Output

```yaml
name: PR Review

on:
  pull_request:
    types: [opened, synchronize]
  issue_comment:
    types: [created]

jobs:
  pr-checks:
    runs-on: ubuntu-latest
    steps:
      # ... implementation
```

## CODEOWNERS Example

```yaml
# .github/CODEOWNERS
*.py @team/python-reviewers
*.js @team/js-reviewers
/.github/ @team/devops
```
