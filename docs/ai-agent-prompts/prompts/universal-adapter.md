# Universal Adapter — AI Project Adaptation Prompt

**Version:** 1.0
**Date:** 2026-03-15
**Purpose:** Analyze any project and create a complete adaptation package with minimal input

---

## Quick Start

| Parameter | Value |
|-----------|-------|
| **Type** | Operational (Universal) |
| **Execution Time** | 15–30 min |
| **Domain** | Project adaptation & onboarding |

**Example Request:**

> "Using `universal-adapter.md`, adapt to this project. Context: [brief description or config file]"

**Expected Output:**
- Project analysis (stack, architecture, key components)
- Onboarding checklist
- Priority recommendations
- Next 3-5 actionable steps

---

## When to Use

- New project onboarding (AI agent or developer)
- Returning to project after hiatus
- Rapid understanding of unfamiliar codebase
- Creating project documentation from scratch
- Pre-flight check before major changes

---

## Mission

Create a **complete project adaptation package** that enables immediate productive work on ANY project type with minimal context.

**Key Principles:**
1. **Minimal Input** — Works with just a project path or config file
2. **Self-Contained** — No external dependencies or CodeShift-specific knowledge
3. **Actionable Output** — Concrete steps, not abstract suggestions
4. **Scenario-Aware** — Adapts output based on project type and state

---

## Input Requirements

### Minimum (Pick ONE)

1. **Project Path** — Directory to analyze
2. **Config File** — `project-config.yaml` with project metadata
3. **Git URL** — Repository to clone and analyze

### Optional Context

- Business goal or use case
- Team composition (if known)
- Timeline or constraints
- Specific areas of focus

---

## Output Artifacts

### Primary Outputs

1. **Project Analysis** (`ANALYSIS-[Project].md`)
   - Technology stack identification
   - Architecture overview
   - Key components and dependencies
   - Development workflow

2. **Onboarding Checklist** (`ONBOARDING-[Project].md`)
   - Setup steps (dependencies, environment)
   - Key files to understand
   - Common gotchas
   - Testing approach

3. **Quick Start Guide** (`QUICKSTART-[Project].md`)
   - How to run locally
   - How to test
   - How to deploy (if applicable)

### Optional Outputs

- **Gap Analysis** — What's missing vs. best practices
- **Tech Debt Notes** — Known issues and shortcuts
- **Contribution Guide** — How to submit changes

---

## Workflow (5 Steps)

### Step 1: Project Discovery

**Goal:** Understand what we're working with.

**Actions:**
1. List top-level directory structure
2. Identify language/framework markers:
   - `package.json` → Node.js
   - `pyproject.toml` / `requirements.txt` → Python
   - `go.mod` → Go
   - `Cargo.toml` → Rust
   - `pom.xml` / `build.gradle` → Java
   - `*.csproj` → C#/.NET
   - No markers → Clean/legacy project
3. Detect project type:
   - Web application
   - Library/SDK
   - CLI tool
   - API/Microservice
   - Mobile app
   - Infrastructure
   - Mixed/other

**Output:** Project type + technology stack (version if found)

---

### Step 2: Deep Dive

**Goal:** Understand architecture and key components.

**For Each Project Type:**

#### Web Application
- Entry point (`index.html`, `main.ts`, `app.py`, etc.)
- Routing mechanism
- State management
- API layer
- Database (if any)
- Authentication approach

#### Library/SDK
- Public API surface (`export`, `public`, `__init__.py`)
- Package structure
- Version (from config)
- Dependencies
- Testing approach

#### CLI Tool
- Entry point (main binary/script)
- Argument parsing
- Commands structure
- Configuration handling

#### API/Microservice
- Endpoint definitions
- Data models
- External integrations
- Deployment config

#### Mobile App
- Framework (React Native, Flutter, Swift, Kotlin)
- State management
- Navigation
- API client
- Platform-specific requirements

#### Infrastructure
- IaC tool (Terraform, Pulumi, CloudFormation)
- State management
- Modules structure
- Deployment target

**Output:** Component map with file locations

---

### Step 3: Development Workflow

**Goal:** Understand how to work with the project.

**Questions to Answer:**
- How to install dependencies?
- How to run in development?
- How to test?
- How to build?
- How to deploy?
- Any CI/CD pipelines?
- Environment variables needed?

**Output:** Commands and configuration needed

---

### Step 4: Risk & Gap Analysis

**Goal:** Identify potential issues.

**Check For:**
- Missing documentation
- Outdated dependencies
- Security concerns
- Missing tests
- Hardcoded values
- Technical debt indicators

**Output:** List of risks with severity

---

### Step 5: Package Creation

**Goal:** Create usable output artifacts.

**Combine Steps 1–4 into:**

```markdown
# Project Analysis: [PROJECT_NAME]

## Overview
[Brief description]

## Technology Stack
| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| Language | | | |
| Framework | | | |
| Database | | | |
| ... | | | |

## Architecture
[High-level diagram or description]

## Key Components
| Component | Path | Purpose |
|-----------|------|---------|
| | | |

## Development Setup
### Prerequisites
- [List]

### Installation
```bash
[Commands]
```

### Running
```bash
[Commands]
```

### Testing
```bash
[Commands]
```

## Risks & Gaps
| Issue | Severity | Recommendation |
|-------|----------|----------------|
| | | |

## Next Steps (First Session)
1. [Actionable step 1]
2. [Actionable step 2]
3. [Actionable step 3]
```

---

## Scenario Handling

### Scenario 1: New Project from Scratch

**Input:** Empty or minimal repository
**Approach:**
- Identify intended use case from README or context
- Suggest appropriate stack if not defined
- Create onboarding based on common patterns

**Output Emphasis:** Setup guide, first features recommendation

---

### Scenario 2: Existing Project Without Documentation

**Input:** Codebase only
**Approach:**
- Reverse-engineer architecture from code
- Identify entry points and flows
- Note missing pieces

**Output Emphasis:** Analysis, gap identification

---

### Scenario 3: Legacy Project with Documentation

**Input:** Code + old docs
**Approach:**
- Compare docs to reality
- Identify outdated information
- Prioritize what still applies

**Output Emphasis:** What's still valid, what's deprecated

---

### Scenario 4: Multilingual Project

**Input:** Multiple languages/frameworks
**Approach:**
- Identify each component
- Map integration points
- Understand deployment topology

**Output Emphasis:** Component map, integration points

---

### Scenario 5: Microservices Architecture

**Input:** Multiple services
**Approach:**
- Identify each service
- Map dependencies
- Find communication patterns (sync/async)
- Identify shared components

**Output Emphasis:** Service map, communication flows, deployment

---

### Scenario 6: AI/ML Project

**Input:** ML-focused codebase
**Approach:**
- Identify framework (PyTorch, TensorFlow, etc.)
- Find model files and training code
- Understand data pipeline
- Note infrastructure needs (GPU, etc.)

**Output Emphasis:** Model management, training workflow, inference

---

## Quality Checklist

Before finalizing output, verify:

- [ ] Technology stack identified (all major components)
- [ ] Entry point(s) located
- [ ] Dependencies listed
- [ ] How to run locally documented
- [ ] How to test documented
- [ ] Key components mapped
- [ ] At least 3 actionable next steps
- [ ] Risks identified (if any)
- [ ] Project type correctly classified

---

## Configuration File Template

Create `project-config.yaml` in project root:

```yaml
# Project Configuration
# Copy to your project and customize

project:
  name: "My Project"
  type: "web-app"  # web-app, api, library, cli, mobile, infrastructure, mixed
  description: "Brief description"

# Optional: override auto-detection
stack:
  language: "python"
  framework: "fastapi"
  database: "postgresql"
  # ...

# Optional: business context
context:
  team_size: 1
  timeline: "MVP in 2 weeks"
  goals:
    - "Ship MVP"
    - "Validate idea"

# Optional: focus areas
focus:
  - "API development"
  - "User authentication"
  - "Payment integration"

# Optional: known gaps
gaps:
  - "No tests yet"
  - "Documentation incomplete"
```

---

## Examples

See `examples/` directory for complete adaptation examples:

- [Python Web App](examples/python.md)
- [Node.js Project](examples/nodejs.md)
- [Go Microservice](examples/go.md)
- [Clean Project](examples/clean-project.md)
- [Microservices](examples/microservices.md)
- [AI/ML Project](examples/ai-ml.md)

---

## Integration

### Claude Code

```bash
# Run with project context
claude "Using universal-adapter.md, adapt to ./my-project"
```

### GitHub Copilot

```markdown
@workspace Using universal-adapter.md, analyze this project and create onboarding docs
```

### Custom Script

```bash
#!/bin/bash
# Run adaptation
claude -p "$(cat prompts/universal-adapter.md)" --context "$(cat project-config.yaml)"
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-15 | Initial release |

---

**End of Universal Adapter Prompt**
