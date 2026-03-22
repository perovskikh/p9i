# ADR-005: UI/UX Integration Strategy

## Status
**Implemented** | 2026-03-22

## Context

Need to support beautiful UI/UX generation for web apps, CLI tools, and mobile applications through p9i MCP server.

## Decision

We will integrate with modern UI/UX frameworks and tools to enable prompt-driven UI generation.

### Web UI Integration

| Framework | Purpose | Env Variable |
|-----------|---------|--------------|
| TailwindCSS | Utility-first CSS generation | `TAILWIND_API_KEY` |
| shadcn/ui | Component library | - |
| Radix UI | Headless primitives | - |
| Figma API | Design imports | `FIGMA_TOKEN` |

### CLI UI Integration

| Framework | Purpose | Language |
|-----------|---------|----------|
| Textual | Rich CLI interfaces | Python |
| Bubble Tea | TUI framework | Go |
| Blinks | Modern TUI | Rust |

### Desktop/Mobile Integration

| Framework | Purpose | Env Variable |
|-----------|---------|--------------|
| Tauri | Lightweight desktop apps | `TAURI_TOKEN` |
| Electron | Cross-platform desktop | - |
| Flutter | Mobile apps | `FLUTTER_TOKEN` |

## Consequences

- New prompts for UI/UX generation
- Support for multiple frameworks
- Design token integration
- Theme customization

## Required Environment Variables

```bash
# UI/UX
TAILwind_API_KEY=your_key      # Optional: Tailwind AI
FIGMA_TOKEN=your_token         # Figma API for design import
TUI_THEME=dark                 # CLI theme (dark/light)

# Desktop
TAURI_TOKEN=your_token         # Tauri authentication

# Mobile
FLUTTER_TOKEN=your_token       # Flutter/Expo authentication
```

## Implementation

### MCP Tools (4 new)

| Tool | Description |
|------|-------------|
| `generate_tailwind` | Generate TailwindCSS component |
| `generate_shadcn` | Generate shadcn/ui component |
| `generate_textual` | Generate Textual TUI component |
| `generate_tauri` | Generate Tauri desktop app scaffold |

### Architecture

- Uses LLM to generate code based on component description
- Integrated with prompt executor for consistent output
- Added to `get_available_mcp_tools` list (total 28 tools)
- Added to external_integrations section

### Testing

```bash
# Test Tailwind generation
generate_tailwind('button', 'primary button with hover effect')
# Returns: HTML with TailwindCSS classes
```

## Alternatives Considered

- Use only TailwindCSS (rejected - need component libraries)
- Generate raw HTML/CSS (rejected - need modern frameworks)
- Skip CLI support (rejected - CLI is important use case)
