# Plugin Packs

**Version:** 1.0
**Date:** 2026-04-03

Plugin packs extend p9i with specialized prompts for different domains.

## Available Packs

| Pack | Description | Triggers |
|------|-------------|----------|
| `k8s-pack` | Kubernetes operations | deploy, k8s, pod, helm |
| `ci-cd-pack` | CI/CD pipelines | github, actions, ci, cd |
| `github-pack` | GitHub integration | issues, pr, repo |
| `uiux-pack` | Design System | tailwind, shadcn, colors |
| `browser-pack` | Browser automation | browser, playwright |
| `pinescript-v6` | TradingView scripts | pinescript, tradingview |
| `project-pack` | Project management | project, memory |

## Structure

```
prompts/packs/
├── pack.schema.json       # JSON Schema for validation
├── k8s-pack/
│   ├── pack.json
│   └── promt-k8s-*.md
├── ci-cd-pack/
│   ├── pack.json
│   └── promt-ci-*.md
├── github-pack/
│   ├── pack.json
│   └── promt-github-*.md
└── ...
```

## Pack Manifest

Each pack has `pack.json`:

```json
{
  "name": "k8s-pack",
  "version": "1.0.0",
  "tier": 3,
  "prompts": ["promt-k8s-deploy.md"],
  "triggers": {
    "deploy": "promt-k8s-deploy.md"
  }
}
```

## Usage

Packs are automatically loaded when triggers match user requests.
