# Example: Clean Project Adaptation

## Scenario

**Input:** A project with no documentation or standard markers

**Project Structure:**
```
my-legacy-app/
├── src/
│   ├── main.js
│   ├── utils.js
│   └── data/
│       └── config.json
├── static/
│   ├── style.css
│   └── images/
├── lib/
│   └── vendor/
├── build/
└── index.html
```

---

## Running the Adapter

```bash
claude "Using prompts/universal-adapter.md, analyze this project"
```

---

## Generated Output

### ANALYSIS-MyLegacyApp.md

```markdown
# Project Analysis: My Legacy App

## Overview

Legacy web application with vanilla JavaScript, HTML, and CSS.
Appears to be a static site with client-side JavaScript.

## Technology Stack

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| Language | JavaScript | ES6+ | From source files |
| UI | Vanilla JS | - | No framework detected |
| Styling | CSS | - | Static files |
| Assets | Static | - | Images, fonts |
| Build | Unknown | - | No build system detected |

## Architecture

```
index.html
    ↓
main.js (entry point)
    ↓
utils.js (helpers)
    ↓
Static Assets (CSS, images)
```

## Key Components

| Component | Path | Purpose |
|-----------|------|---------|
| Entry | `index.html` | Main HTML page |
| JavaScript | `src/main.js` | Application logic |
| Utilities | `src/utils.js` | Helper functions |
| Styles | `static/style.css` | Styling |
| Config | `src/data/config.json` | Configuration |

## Development Setup

### Prerequisites
- Node.js (for local server, optional)
- Browser (Chrome, Firefox, etc.)

### Running Locally
```bash
# Option 1: Simple HTTP server
python3 -m http.server 8000
# or
npx serve .

# Option 2: VS Code Live Server
# Right-click index.html → Open with Live Server
```

### No Build System Detected

This project uses vanilla JavaScript with no build step:
- Edit `src/main.js` directly
- Refresh browser to see changes

## Unknowns (Needs Investigation)

| Item | Status | Recommendation |
|------|--------|----------------|
| JavaScript version | Unknown | Check for ES6+ features |
| Browser support | Unknown | Test in target browsers |
| Dependencies | Unknown | Check `lib/vendor/` |
| Configuration | Partial | `src/data/config.json` |

## Risks & Gaps

| Issue | Severity | Recommendation |
|-------|----------|----------------|
| No tests | High | Add test framework |
| No documentation | High | Document architecture |
| No dependency management | Medium | Consider npm |
| No build process | Medium | Add bundler if needed |

## Next Steps

1. Run local server: `python3 -m http.server 8000`
2. Open http://localhost:8000 in browser
3. Read `index.html` to understand structure
4. Read `src/main.js` to understand logic
5. Explore `src/data/config.json` for configuration

## Recommendations

This appears to be a legacy or simple project. Consider modernizing:

1. **Add package.json** for dependency management
2. **Add a bundler** (Vite, Webpack) for better DX
3. **Add testing** (Jest, Vitest)
4. **Document the architecture**
```

---

## Key Insights

### What the Adapter Found

1. **No build system** — Plain HTML/JS/CSS
2. **No framework** — Vanilla JavaScript
3. **Static assets** — CSS, images in static folder
4. **Vendor folder** — Some third-party code

### What It Flagged

- Missing documentation
- No dependency management
- No testing
- Unknown browser support

---

## Follow-up Questions

> "What's the purpose of this application?"

> "Are there any known issues or bugs?"

> "What browsers should be supported?"

---

**See also:**
- [Python Example](python.md)
- [Node.js Example](nodejs.md)
- [AI/ML Example](ai-ml.md)
