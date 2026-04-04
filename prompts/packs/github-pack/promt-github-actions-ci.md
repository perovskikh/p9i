# GitHub Actions CI Pipeline

## Role
GitHub Actions CI specialist. Creates and optimizes GitHub Actions workflows for continuous integration.

## Context
- Project: {project_path}
- Language: {language}
- Framework: {framework}
- Test runner: {test_runner}

## Instructions

Create a GitHub Actions workflow file at `.github/workflows/ci.yml` that:

1. **Triggers**: On push to `main` and on PRs to `main`
2. **Jobs**: Build → Test → Lint (sequential)
3. **Steps**:
   - Checkout code
   - Set up language/runtime (Python, Node, etc.)
   - Install dependencies
   - Run linter (if applicable)
   - Run tests with coverage
   - Upload coverage to Codecov/COVERALLS (if applicable)

4. **Matrix strategy**: Test on multiple Python/Node versions if specified

## Output Format

Return the complete YAML content:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      # ... full workflow
```

## Requirements

- Use `ubuntu-latest` runner
- Cache dependencies where applicable
- Fail fast: stop other matrix jobs if one fails
- Report coverage percentage
