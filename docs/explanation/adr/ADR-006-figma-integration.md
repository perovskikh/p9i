# ADR-006: Figma Integration Strategy

## Status
**Implemented** | 2026-03-22

## Context

Need to integrate with Figma API to enable design-to-code workflow. This allows reading Figma files directly and converting designs to TailwindCSS/shadcn/ui code.

## Decision

We will integrate with Figma REST API to provide:

1. **File Reading** - Get file structure, pages, frames
2. **Component Extraction** - Extract all components from file
3. **Design Tokens** - Extract colors, typography, effects
4. **Image Export** - Export nodes as PNG/SVG
5. **AI Conversion** - Convert Figma design to code via LLM

## Implementation

### Environment Variables

```bash
# .env
FIGMA_TOKEN=figd_xxxxxxxxxxxx  # Required for API access
```

Get token from: Figma → Settings → Account → Personal access tokens

### MCP Tools (5 new)

| Tool | Description |
|------|-------------|
| `get_figma_file` | Get file structure and metadata |
| `get_figma_components` | Get all components from file |
| `get_figma_styles` | Get design tokens (colors, typography) |
| `export_figma_nodes` | Export nodes as images (PNG/SVG) |
| `figma_to_code` | Convert Figma to TailwindCSS/shadcn via AI |

### Architecture

```
Figma File → Figma API → p9i Tools → TailwindCSS/shadcn Code
                    ↓
              LLM (MiniMax)
                    ↓
              Design Tokens → Generated Code
```

### Usage Examples

```python
# Get file structure
get_figma_file("abc123xyz")
# Returns: {pages: [...], name: "Design", lastModified: "..."}

# Get components
get_figma_components("abc123xyz")
# Returns: {components: [...], total: 25}

# Get design tokens
get_figma_styles("abc123xyz")
# Returns: {colors: [{hex: "#000000", name: "Primary"}], ...}

# Export images
export_figma_nodes("abc123xyz", ["1:2", "1:3"], format="png")
# Returns: {images: {"1:2": "https://..."}}

# Convert to code
figma_to_code("abc123xyz", target="tailwind")
# Returns: {code: "<button class=\"bg-blue-500..."}
```

### Claude Code Integration

```bash
"Получи структуру Figma файла abc123xyz. use p9i"
"Вытащи цвета из дизайна в Figma. use p9i"
"Конвертируй Figma макет в TailwindCSS. use p9i"
```

## Consequences

- **Positive**: Direct integration with design workflow
- **Positive**: Automatic design token extraction
- **Positive**: AI-powered code generation from designs
- **Negative**: Requires FIGMA_TOKEN
- **Negative**: API rate limits apply

## Alternatives Considered

- Use Figma Webhooks for real-time sync (deferred - need web server)
- Use Figma Plugin (deferred - needs separate plugin)
- Manual design token copy-paste (rejected - not scalable)

## Future Enhancements

- Webhook support for real-time updates
- Component variant extraction
- Auto-layout to Flexbox conversion
- Design system documentation generation
