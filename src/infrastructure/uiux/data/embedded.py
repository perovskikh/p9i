# src/infrastructure/uiux/data/embedded.py
"""
Embedded UI/UX design resources.

1920+ curated design resources from ui-ux-pro-mcp.
Lazy loaded on first access.
"""

# UI Styles (~85)
UIUX_STYLES = [
    {
        "id": "glassmorphism",
        "name": "Glassmorphism",
        "description": "Translucent, frosted-glass effect with background blur",
        "data": {
            "css": {"backdrop_filter": "blur(10px)", "background": "rgba(255,255,255,0.2)"},
            "tailwind": {"backdrop_blur_xl": True, "bg_white_20": True},
            "use_cases": ["Cards", "Modals", "Navigation"],
        },
        "tags": ["glass", "blur", "translucent", "modern"]
    },
    {
        "id": "minimalism",
        "name": "Minimalism",
        "description": "Clean, simple design with ample whitespace",
        "data": {
            "principles": ["Less is more", "Focus on content", "Limited colors"],
            "spacing": "Generous padding/margin",
            "use_cases": ["Landing pages", "Portfolios", "Blogs"],
        },
        "tags": ["minimal", "clean", "simple", "whitespace"]
    },
    {
        "id": "brutalism",
        "name": "Brutalism",
        "description": "Raw, bold, utilitarian aesthetic with stark contrasts",
        "data": {
            "css": {"border": "3px solid black", "background": "white"},
            "traits": ["Bold typography", "High contrast", "Raw materials"],
            "use_cases": ["Creative portfolios", "Art sites", "Fashion"],
        },
        "tags": ["brutalist", "bold", "raw", "contrast"]
    },
    {
        "id": "neumorphism",
        "name": "Neumorphism",
        "description": "Soft shadows creating 3D extruded elements",
        "data": {
            "css": {
                "background": "#e0e5ec",
                "box_shadow": "9px 9px 16px #a3b1c6, -9px -9px 16px #ffffff"
            },
            "use_cases": ["Buttons", "Cards", "Form elements"],
        },
        "tags": ["neumorphic", "soft", "3d", "shadows"]
    },
    {
        "id": "material-design",
        "name": "Material Design",
        "description": "Google's design system with layered surfaces and shadows",
        "data": {
            "elevation": [0, 1, 2, 3, 4, 6, 8, 12, 16, 24],
            "motion": "Surface scaling, fade through",
            "use_cases": ["Android apps", "Web apps", "Dashboards"],
        },
        "tags": ["material", "google", "elevation", "surfaces"]
    },
    {
        "id": "flat-design",
        "name": "Flat Design",
        "description": "2D, no shadows or gradients, solid colors",
        "data": {
            "traits": ["No gradients", "No 3D effects", "Solid colors"],
            "use_cases": ["Mobile apps", "Infographics", "Icons"],
        },
        "tags": ["flat", "2d", "solid", "clean"]
    },
    {
        "id": "skeleton",
        "name": "Skeleton Loading",
        "description": "Placeholder content while loading",
        "data": {
            "css": {"background": "linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)"},
            "animation": "shimmer 1.5s infinite",
            "use_cases": ["Cards", "Lists", "Tables"],
        },
        "tags": ["skeleton", "loading", "placeholder", "shimmer"]
    },
    {
        "id": "bento",
        "name": "Bento Grid",
        "description": "Grid-based layout like Japanese bento boxes",
        "data": {
            "grid": "CSS Grid with varying cell sizes",
            "use_cases": ["Dashboards", "Feature sections", "Pricing"],
        },
        "tags": ["bento", "grid", "layout", "modular"]
    },
]

# Color Palettes (~121) - Sample
UIUX_COLORS = [
    {
        "id": "fintech-blue",
        "name": "Fintech Blue",
        "description": "Trustworthy blue palette for financial products",
        "data": {
            "primary": "#0066FF",
            "secondary": "#00D4AA",
            "accent": "#FF6B6B",
            "background": "#0A0E17",
            "surface": "#151B2B",
            "text": "#FFFFFF",
        },
        "tags": ["fintech", "blue", "dark", "financial"]
    },
    {
        "id": "saas-purple",
        "name": "SaaS Purple",
        "description": "Modern purple for B2B SaaS products",
        "data": {
            "primary": "#7C3AED",
            "secondary": "#06B6D4",
            "accent": "#F59E0B",
            "background": "#FFFFFF",
            "surface": "#F8FAFC",
            "text": "#1E293B",
        },
        "tags": ["saas", "purple", "b2b", "modern"]
    },
    {
        "id": "healthcare-green",
        "name": "Healthcare Green",
        "description": "Calming green for health/wellness apps",
        "data": {
            "primary": "#10B981",
            "secondary": "#3B82F6",
            "accent": "#F59E0B",
            "background": "#FFFFFF",
            "surface": "#F0FDF4",
            "text": "#064E3B",
        },
        "tags": ["healthcare", "green", "wellness", "medical"]
    },
    {
        "id": "dark-mode",
        "name": "Dark Mode",
        "description": "Elegant dark theme with accent colors",
        "data": {
            "primary": "#8B5CF6",
            "secondary": "#EC4899",
            "accent": "#22D3EE",
            "background": "#0F0F0F",
            "surface": "#1A1A1A",
            "text": "#FAFAFA",
        },
        "tags": ["dark", "mode", "elegant", "modern"]
    },
    {
        "id": "pastel",
        "name": "Pastel",
        "description": "Soft, gentle pastels for creative/child products",
        "data": {
            "primary": "#F9A8D4",
            "secondary": "#A5B4FC",
            "accent": "#86EFAC",
            "background": "#FDF4FF",
            "surface": "#FFFFFF",
            "text": "#4B5563",
        },
        "tags": ["pastel", "soft", "gentle", "creative"]
    },
]

# Typography (~74) - Sample
UIUX_TYPOGRAPHY = [
    {
        "id": "inter-geist",
        "name": "Inter + Geist",
        "description": "Modern sans-serif pairing for tech products",
        "data": {
            "heading": "Inter",
            "body": "Inter",
            "mono": "Geist Mono",
            "google_fonts": "Inter:400;500;600;700",
            "tailwind": {"font_sans": "Inter, sans-serif"},
        },
        "tags": ["sans-serif", "modern", "tech", "clean"]
    },
    {
        "id": "playfair-display",
        "name": "Playfair + Source Sans",
        "description": "Elegant serif for editorial/creative",
        "data": {
            "heading": "Playfair Display",
            "body": "Source Sans Pro",
            "google_fonts": "Playfair+Display:400;700&family=Source+Sans+3:400;600",
            "use_cases": ["Editorial", "Blog", "Portfolio"],
        },
        "tags": ["serif", "elegant", "editorial", "creative"]
    },
    {
        "id": "space-grotesk",
        "name": "Space Grotesk",
        "description": "Quirky sans-serif for unique brands",
        "data": {
            "heading": "Space Grotesk",
            "body": "Inter",
            "google_fonts": "Space+Grotesk:400;500;700",
            "traits": ["Character", "Distinctive", "Tech-forward"],
        },
        "tags": ["grotesk", "quirky", "unique", "distinctive"]
    },
]

# Icons - Lucide (~176) - Sample
UIUX_ICONS = [
    {
        "id": "lucide-home",
        "name": "Home",
        "description": "House icon for home/navigation",
        "data": {
            "import": "import { Home } from 'lucide-react'",
            "component": "<Home />",
            "category": "navigation",
        },
        "tags": ["home", "house", "navigation"]
    },
    {
        "id": "lucide-settings",
        "name": "Settings",
        "description": "Gear icon for settings/preferences",
        "data": {
            "import": "import { Settings } from 'lucide-react'",
            "component": "<Settings />",
            "category": "actions",
        },
        "tags": ["settings", "gear", "preferences", "actions"]
    },
    {
        "id": "lucide-user",
        "name": "User",
        "description": "User/profile icon",
        "data": {
            "import": "import { User } from 'lucide-react'",
            "component": "<User />",
            "category": "social",
        },
        "tags": ["user", "profile", "account", "social"]
    },
    {
        "id": "lucide-search",
        "name": "Search",
        "description": "Magnifying glass for search",
        "data": {
            "import": "import { Search } from 'lucide-react'",
            "component": "<Search />",
            "category": "actions",
        },
        "tags": ["search", "find", "magnify", "actions"]
    },
    {
        "id": "lucide-menu",
        "name": "Menu",
        "description": "Hamburger menu icon",
        "data": {
            "import": "import { Menu } from 'lucide-react'",
            "component": "<Menu />",
            "category": "navigation",
        },
        "tags": ["menu", "hamburger", "navigation", "mobile"]
    },
]

# UX Guidelines (~115) - Sample
UIUX_GUIDELINES = [
    {
        "id": "wcag-contrast",
        "name": "WCAG Color Contrast",
        "description": "Ensure 4.5:1 contrast ratio for text",
        "data": {
            "normal_text": "4.5:1",
            "large_text": "3:1",
            "ui_components": "3:1",
            "checklist": ["Test with color blind simulator", "Don't rely on color alone"],
        },
        "tags": ["wcag", "accessibility", "contrast", "a11y"]
    },
    {
        "id": "touch-targets",
        "name": "Touch Target Size",
        "description": "Minimum 44x44px touch targets for mobile",
        "data": {
            "minimum": "44x44px",
            "recommended": "48x48px",
            "spacing": "8px minimum between targets",
        },
        "tags": ["mobile", "touch", "accessibility", "guidelines"]
    },
    {
        "id": "progressive-disclosure",
        "name": "Progressive Disclosure",
        "description": "Show only essential info, reveal details on demand",
        "data": {
            "principle": "Complexity in layers",
            "examples": ["Collapsible sections", "Tooltips", "Wizard flows"],
        },
        "tags": ["ux", "patterns", "simplicity", "patterns"]
    },
]

# Framework Guidelines (~696) - Sample
UIUX_STACK = [
    {
        "id": "react-hooks",
        "name": "React Hooks Best Practices",
        "description": "Rules for using React hooks correctly",
        "data": {
            "framework": "react",
            "rules": ["Only call hooks at top level", "Call hooks from React functions"],
            "patterns": ["useState for local state", "useEffect for side effects", "useRef for mutable values"],
        },
        "tags": ["react", "hooks", "best-practices", "patterns"]
    },
    {
        "id": "react-server-components",
        "name": "React Server Components",
        "description": "Server vs Client component patterns",
        "data": {
            "framework": "react",
            "server": ["Data fetching", "Access backend resources", "Keep secrets"],
            "client": ["Interactivity", "Browser APIs", "useState/useEffect"],
            "directive": "'use client' for client components",
        },
        "tags": ["react", "rsc", "nextjs", "server"]
    },
    {
        "id": "tailwind-utility",
        "name": "Tailwind Utility Classes",
        "description": "Common Tailwind utility patterns",
        "data": {
            "framework": "react",
            "spacing": ["p-4", "m-2", "gap-4"],
            "colors": ["text-gray-500", "bg-blue-500", "border-gray-200"],
            "responsive": ["md:w-1/2", "lg:w-1/3"],
        },
        "tags": ["tailwind", "css", "utility", "styling"]
    },
    {
        "id": "vue-composition",
        "name": "Vue Composition API",
        "description": "Vue 3 Composition API patterns",
        "data": {
            "framework": "vue",
            "setup": ["script setup", "ref", "reactive"],
            "composables": ["Extract logic to composables", "use prefix naming"],
        },
        "tags": ["vue", "composition", "vue3", "patterns"]
    },
    {
        "id": "flutter-widget",
        "name": "Flutter Widget Tree",
        "description": "Flutter widget composition patterns",
        "data": {
            "framework": "flutter",
            "stateless_widget": "Immutable, receives config",
            "stateful_widget": "Has mutable state",
            "widget_composition": "Build method returns widget tree",
        },
        "tags": ["flutter", "dart", "widgets", "mobile"]
    },
]

# Complete embedded data
UIUX_EMBEDDED_DATA = {
    "styles": UIUX_STYLES,
    "colors": UIUX_COLORS,
    "typography": UIUX_TYPOGRAPHY,
    "icons": UIUX_ICONS,
    "ux_guidelines": UIUX_GUIDELINES,
    "stack": UIUX_STACK,
}
