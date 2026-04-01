# Pack Loader for AI Prompt System

**Version:** 1.0
**Date:** 2026-03-31
**Purpose:** Plugin pack management for AI Prompt System.

The PackLoader manages plugin packs in the AI Prompt System.

## Structure

```
prompts/packs/
├── pack.schema.json      # JSON Schema for pack validation
├── k8s-pack/
│   ├── pack.json        # Pack manifest
│   └── *.md             # Pack prompts
└── ci-cd-pack/
    ├── pack.json
    └── *.md
```

## Usage

```python
from src.storage.packs import PackLoader

loader = PackLoader()

# List all packs
packs = loader.list_packs()

# Load pack by name
k8s_pack = loader.load_pack("k8s-pack")

# Find prompt by trigger
prompt = loader.find_by_trigger("deploy to k8s")
```

## Pack Manifest

Each pack must have `pack.json`:

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
