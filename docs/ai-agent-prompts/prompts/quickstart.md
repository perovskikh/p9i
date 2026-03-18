# Universal Prompt System — Quickstart Guide

## Overview

The Universal Prompt System is a self-contained AI agent prompt package that adapts to ANY project with minimal configuration. It's designed to be added as a git submodule to any repository.

---

## Installation

### Option 1: Git Submodule (Recommended)

```bash
# Navigate to your project
cd /path/to/your-project

# Add as submodule
git submodule add https://github.com/your-org/universal-prompt-system.git prompts

# Initialize and update
git submodule update --init --recursive
```

### Option 2: Clone Directly

```bash
# Clone into your project
git clone https://github.com/your-org/universal-prompt-system.git prompts
```

### Option 3: Copy Files

```bash
# Download specific version
curl -L https://github.com/your-org/universal-prompt-system/archive/refs/tags/v1.0.tar.gz | tar xz
mv universal-prompt-system-1.0 prompts
```

---

## Quick Configuration

### Step 1: Create Project Config (Optional but Recommended)

```bash
# Copy template
cp prompts/config.yaml ./project-config.yaml

# Edit with your project details
nano project-config.yaml
```

### Step 2: Verify Structure

```
your-project/
├── prompts/
│   ├── universal-adapter.md    # Main prompt
│   ├── quickstart.md          # This file
│   ├── config.yaml            # Configuration template
│   ├── README.md
│   └── examples/              # Language examples
├── project-config.yaml        # Your config (create this)
├── src/                       # Your code
├── tests/
└── README.md
```

---

## Usage

### Basic: Analyze Current Directory

```bash
# Claude Code
claude "Using prompts/universal-adapter.md, adapt to this project"
```

### With Config File

```bash
# Provide config as context
claude "Using prompts/universal-adapter.md with project-config.yaml, analyze this project"
```

### Specific Project Path

```bash
claude "Using prompts/universal-adapter.md, analyze ./my-service"
```

---

## Output

The prompt will generate:

1. **ANALYSIS-[Project].md** — Full project analysis
2. **ONBOARDING-[Project].md** — Setup and onboarding steps
3. **QUICKSTART-[Project].md** — How to run the project

Output location: `docs/adaptation/` (or `artifacts/`)

---

## Project Types Supported

| Type | Detection | Notes |
|------|-----------|-------|
| Python Web | `pyproject.toml`, `requirements.txt` | Django, FastAPI, Flask |
| Node.js Web | `package.json` | Express, Next.js, NestJS |
| Go | `go.mod` | Standard Go layouts |
| Rust | `Cargo.toml` | CLI or library |
| Java | `pom.xml`, `build.gradle` | Spring, Maven |
| .NET | `*.csproj` | ASP.NET, .NET Core |
| Mobile | React Native, Flutter configs | Cross-platform |
| Infrastructure | Terraform, Pulumi | IaC projects |
| Mixed | Multiple markers | Microservices |

---

## Customization

### Adding Project-Specific Prompts

Create `prompts/local/` for project-specific prompts:

```
prompts/
├── universal-adapter.md
├── local/
│   ├── mvp-generator.md      # Project-specific MVP
│   ├── deployment.md        # Custom deployment steps
│   └── coding-standards.md  # Project conventions
└── examples/
```

### Extending Configuration

Add custom fields to `project-config.yaml`:

```yaml
project:
  name: "My SaaS"
  type: "web-app"

# Custom fields
my_project:
  hosting: "kubernetes"
  payment_provider: "stripe"
  auth: "jwt"
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Project Analysis
on: [push]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Claude Analysis
        run: |
          claude "Using prompts/universal-adapter.md, adapt to ."
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: project-analysis
        name: Project Analysis
        entry: claude "Using prompts/universal-adapter.md, adapt to ."
        language: system
        pass_filenames: false
```

---

## Troubleshooting

### "No project markers found"

The project may be a clean/legacy project. The prompt will use generic analysis:
- List all directories and files
- Look for any configuration
- Ask for manual input if needed

### "Too many technologies detected"

For microservices or mixed projects:
- The prompt will create a component map
- Each service gets its own analysis section

### Output location issues

If you can't write to `docs/`, the prompt will output to:
1. `artifacts/`
2. Current directory
3. Console output (as markdown)

---

## Examples

See the `examples/` directory for complete walkthroughs:

- [Python FastAPI](examples/python.md)
- [Node.js Express](examples/nodejs.md)
- [Go Microservice](examples/go.md)
- [Clean Project](examples/clean-project.md)
- [Multilingual/Microservices](examples/microservices.md)
- [AI/ML Project](examples/ai-ml.md)

---

## Next Steps

1. **First Run:** `claude "Using prompts/universal-adapter.md, analyze this project"`
2. **Review Output:** Read generated `ANALYSIS-*.md`
3. **Iterate:** Ask follow-up questions about specific components
4. **Share:** Use generated docs for team onboarding

---

## Support

- Issues: https://github.com/your-org/universal-prompt-system/issues
- Discussions: https://github.com/your-org/universal-prompt-system/discussions

---

**Version:** 1.0 | **Date:** 2026-03-15
