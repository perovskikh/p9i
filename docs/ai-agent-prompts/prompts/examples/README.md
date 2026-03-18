# Universal Prompt System — Examples

This directory contains complete examples of project adaptation for different scenarios.

## Examples Overview

| Example | Project Type | Languages/Frameworks | When to Use |
|---------|-------------|---------------------|-------------|
| [python.md](python.md) | Web Application | Python, FastAPI, PostgreSQL | Django/FastAPI/Flask projects |
| [nodejs.md](nodejs.md) | Web Application | Node.js, Express, MongoDB | Express, NestJS, Next.js |
| [go.md](go.md) | Microservice | Go, Chi, PostgreSQL | Go services, CLI tools |
| [clean-project.md](clean-project.md) | Legacy/Simple | Vanilla JS, HTML, CSS | Projects without build system |
| [microservices.md](microservices.md) | Distributed System | Multiple | Multi-service architectures |
| [ai-ml.md](ai-ml.md) | ML/AI | Python, PyTorch, TF | Machine learning projects |

---

## Quick Reference

### New Project with Standard Stack

**Python web app** → [python.md](python.md)
**Node.js web app** → [nodejs.md](nodejs.md)
**Go service** → [go.md](go.md)

### Special Cases

**No documentation** → [clean-project.md](clean-project.md)
**Multiple services** → [microservices.md](microservices.md)
**Machine learning** → [ai-ml.md](ai-ml.md)

---

## What Each Example Shows

Each example demonstrates:

1. **Input** — What the project looks like
2. **Command** — How to run the adapter
3. **Output** — Generated analysis document
4. **Key Insights** — What the adapter detected
5. **Follow-up Questions** — What to ask next

---

## Adding New Examples

To add a new example:

1. Copy the template below
2. Fill in your project details
3. Add to this index

```markdown
# Example: [Project Type]

## Scenario

**Input:** [Brief project description]

## Running the Adapter

\`\`\`bash
claude "Using prompts/universal-adapter.md, analyze this [project type] project"
\`\`\`

## Generated Output

[Your generated analysis]

---

## Follow-up Questions

> "Your follow-up questions"

---

**See also:**
- [python.md](python.md)
- [nodejs.md](nodejs.md)
```

---

## Version

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-15 | Initial examples |

---

[Back to parent directory](../README.md)
