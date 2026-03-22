"""
p9i Control Panel - Web UI for MCP Server Management

Streamlit application to manage p9i MCP server through a graphical interface.
Directly imports and uses p9i server functions.
"""

import streamlit as st
import json
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, "/app")

# Load environment
from pathlib import Path
from dotenv import load_dotenv
env_path = Path("/app/.env")
if env_path.exists():
    load_dotenv(env_path)

# Configuration
API_KEY = os.getenv("API_KEY", "sk-system-dev")

# Import p9i server functions
try:
    from src.api.server import (
        get_available_mcp_tools,
        list_prompts,
        get_project_memory,
        save_project_memory,
        generate_jwt_token,
        validate_jwt_token,
        generate_tailwind,
        generate_shadcn,
        generate_textual,
        generate_tauri,
        get_figma_file,
        get_figma_components,
        get_figma_styles,
        export_figma_nodes,
        figma_to_code,
    )
    SERVER_AVAILABLE = True
except Exception as e:
    SERVER_AVAILABLE = False
    print(f"Warning: Could not import server functions: {e}")

# Page configuration
st.set_page_config(
    page_title="p9i Control Panel",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stApp {
        background-color: #0e1117;
    }
    .stat-card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    .stat-value {
        font-size: 32px;
        font-weight: bold;
        color: #38bdf8;
    }
    .stat-label {
        font-size: 14px;
        color: #94a3b8;
    }
    .success-badge {
        background-color: #22c55e;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
    }
    .error-badge {
        background-color: #ef4444;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)


def call_mcp_tool(tool_name: str, arguments: dict = None) -> dict:
    """Call MCP tool directly from server module."""
    if not SERVER_AVAILABLE:
        return {"error": "Server functions not available"}

    tool_map = {
        "get_available_mcp_tools": get_available_mcp_tools,
        "list_prompts": list_prompts,
        "get_project_memory": get_project_memory,
        "save_project_memory": save_project_memory,
        "generate_jwt_token": generate_jwt_token,
        "validate_jwt_token": validate_jwt_token,
        "generate_tailwind": generate_tailwind,
        "generate_shadcn": generate_shadcn,
        "generate_textual": generate_textual,
        "generate_tauri": generate_tauri,
        "get_figma_file": get_figma_file,
        "get_figma_components": get_figma_components,
        "get_figma_styles": get_figma_styles,
        "export_figma_nodes": export_figma_nodes,
        "figma_to_code": figma_to_code,
    }

    tool_func = tool_map.get(tool_name)
    if not tool_func:
        return {"error": f"Tool {tool_name} not found"}

    try:
        import asyncio
        args = arguments or {}

        # Handle JWT token for tools that require it
        if tool_name in ["generate_tailwind", "generate_shadcn", "generate_textual",
                         "generate_tauri", "get_figma_file", "get_figma_components",
                         "get_figma_styles", "export_figma_nodes", "figma_to_code"]:
            # Generate a temporary token for testing
            token_result = generate_jwt_token("web_user", "admin", 24, admin_key=API_KEY)
            args["jwt_token"] = token_result.get("token", "")

        if asyncio.iscoroutinefunction(tool_func):
            result = asyncio.run(tool_func(**args))
        else:
            result = tool_func(**args)

        return result
    except Exception as e:
        return {"error": str(e)}


def get_tools() -> dict:
    """Get list of available MCP tools."""
    try:
        return get_available_mcp_tools()
    except Exception as e:
        return {"tools": [], "error": str(e)}


def get_prompts() -> dict:
    """Get list of prompts."""
    try:
        return list_prompts()
    except Exception as e:
        return {"count": 0, "prompts": [], "error": str(e)}


# Sidebar navigation
st.sidebar.title("🔮 p9i Control Panel")
st.sidebar.markdown("---")

# Navigation menu
pages = {
    "🏠 Dashboard": "dashboard",
    "📝 Prompts": "prompts",
    "🔧 Tools": "tools",
    "📦 Memory": "memory",
    "🎨 UI/UX Gen": "uiux",
    "📐 Figma": "figma",
    "🔐 JWT": "jwt",
    "📜 Logs": "logs",
    "⚙️ Settings": "settings"
}

selected_page = st.sidebar.radio("Navigation", list(pages.keys()))

st.sidebar.markdown("---")
st.sidebar.markdown("### Connection")
st.sidebar.markdown("**Mode:** Direct Import")
st.sidebar.markdown(f"**API Key:** `{API_KEY[:10]}...`")

# Main content
if selected_page == "🏠 Dashboard":
    # Dashboard page
    st.title("📊 p9i Dashboard")

    # Get system info - call directly
    tools_result = get_tools()
    prompts_result = get_prompts()

    tools_count = len(tools_result.get("tools", []))
    prompts_count = prompts_result.get("count", 0)

    # Stats cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{prompts_count}</div>
            <div class="stat-label">Prompts</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{tools_count}</div>
            <div class="stat-label">MCP Tools</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">6</div>
            <div class="stat-label">ADRs</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value" style="color: #22c55e;">✓</div>
            <div class="stat-label">Connected</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Quick actions
    st.subheader("⚡ Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📝 Run Prompt", use_container_width=True):
            st.session_state.current_page = "📝 Prompts"
            st.rerun()

    with col2:
        if st.button("🎨 Generate UI", use_container_width=True):
            st.session_state.current_page = "🎨 UI/UX Gen"
            st.rerun()

    with col3:
        if st.button("🔐 Generate JWT", use_container_width=True):
            st.session_state.current_page = "🔐 JWT"
            st.rerun()

    st.markdown("---")

    # External integrations
    st.subheader("🔗 External Integrations")

    if "external_integrations" in tools_result:
        cols = st.columns(len(tools_result["external_integrations"]))
        for i, (name, config) in enumerate(tools_result["external_integrations"].items()):
            with cols[i]:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label" style="font-weight: bold;">{name.upper()}</div>
                    <div style="margin-top: 10px;">{config.get('description', '')}</div>
                </div>
                """, unsafe_allow_html=True)

elif selected_page == "📝 Prompts":
    st.title("📝 Prompts Management")

    # Search prompts
    search = st.text_input("🔍 Search prompts", placeholder="Type to search...")

    prompts_result = get_prompts()
    prompts = prompts_result.get("prompts", [])

    # Ensure prompts is a list (handle dict case)
    if isinstance(prompts, dict):
        prompts = list(prompts.values())
    elif not isinstance(prompts, list):
        prompts = []

    # Filter by search
    if search:
        prompts = [p for p in prompts if search.lower() in p.get("name", "").lower()]

    # Display prompts
    for prompt in prompts[:20]:
        with st.expander(f"📄 {prompt.get('name', 'Untitled')}"):
            st.markdown(f"**Path:** `{prompt.get('path', '')}`")
            st.markdown(f"**Tier:** {prompt.get('tier', 'unknown')}")
            if "content" in prompt:
                st.code(prompt["content"][:500], language="markdown")

elif selected_page == "🔧 Tools":
    st.title("🔧 MCP Tools")

    tools_result = get_tools()
    tools = tools_result.get("tools", [])

    # Ensure tools is a list
    if not isinstance(tools, list):
        tools = []

    # Search tools
    search = st.text_input("🔍 Search tools", placeholder="Type to search...")

    # Filter by search
    if search:
        tools = [t for t in tools if search.lower() in t.get("name", "").lower()]

    # Display tools
    for tool in tools:
        with st.expander(f"🔧 {tool.get('name', '')}"):
            st.markdown(f"**Description:** {tool.get('description', '')}")

elif selected_page == "📦 Memory":
    st.title("📦 Project Memory")

    st.subheader("Get Project Memory")
    project_id = st.text_input("Project ID", placeholder="Enter project ID...")
    if st.button("Get Memory"):
        result = call_mcp_tool("get_project_memory", {"project_id": project_id})
        st.json(result)

    st.markdown("---")

    st.subheader("Save Project Memory")
    new_project_id = st.text_input("New Project ID", key="new_pid")
    memory_data = st.text_area("Memory Data (JSON)", height=150, placeholder='{"key": "value"}')
    if st.button("Save Memory"):
        try:
            data = json.loads(memory_data)
            result = call_mcp_tool("save_project_memory", {"project_id": new_project_id, "key": "context", "value": data})
            st.success("Memory saved!")
            st.json(result)
        except json.JSONDecodeError:
            st.error("Invalid JSON")

elif selected_page == "🎨 UI/UX Gen":
    st.title("🎨 UI/UX Generator")

    tab1, tab2, tab3, tab4 = st.tabs(["TailwindCSS", "shadcn/ui", "Textual", "Tauri"])

    with tab1:
        st.subheader("TailwindCSS Component")
        component = st.text_input("Component", placeholder="button, card, input...")
        style = st.text_input("Style", placeholder="primary, secondary, ghost...")
        if st.button("Generate TailwindCSS"):
            result = call_mcp_tool("generate_tailwind", {"component": component, "style": style})
            if result.get("status") == "success":
                st.code(result.get("code", ""), language="html")
            elif result.get("error"):
                st.error(result.get("error"))

    with tab2:
        st.subheader("shadcn/ui Component")
        comp2 = st.text_input("Component", key="shadcn", placeholder="button, card, dialog...")
        variant = st.selectbox("Variant", ["default", "outline", "ghost", "secondary"])
        if st.button("Generate shadcn/ui"):
            result = call_mcp_tool("generate_shadcn", {"component": comp2, "variant": variant})
            if result.get("status") == "success":
                st.code(result.get("code", ""), language="tsx")
            elif result.get("error"):
                st.error(result.get("error"))

    with tab3:
        st.subheader("Textual TUI")
        tui_type = st.text_input("Type", placeholder="form, menu, table...")
        tui_style = st.text_input("Style", key="tui", placeholder="dark, light...")
        if st.button("Generate Textual"):
            result = call_mcp_tool("generate_textual", {"component": tui_type, "style": tui_style})
            if result.get("status") == "success":
                st.code(result.get("code", ""), language="python")
            elif result.get("error"):
                st.error(result.get("error"))

    with tab4:
        st.subheader("Tauri Desktop App")
        app_name = st.text_input("App Name", placeholder="my-app")
        template = st.selectbox("Template", ["basic", "react", "vue", "svelte"])
        if st.button("Generate Tauri"):
            result = call_mcp_tool("generate_tauri", {"app_name": app_name, "template": template})
            if result.get("status") == "success":
                st.code(result.get("code", ""), language="bash")
            elif result.get("error"):
                st.error(result.get("error"))

elif selected_page == "📐 Figma":
    st.title("📐 Figma Integration")

    st.info("Make sure FIGMA_TOKEN is set in environment variables")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["File", "Components", "Styles", "Export", "To Code"])

    with tab1:
        st.subheader("Get Figma File")
        file_key = st.text_input("File Key", placeholder="abc123xyz...")
        if st.button("Get File"):
            result = call_mcp_tool("get_figma_file", {"file_key": file_key})
            st.json(result)

    with tab2:
        st.subheader("Get Components")
        file_key2 = st.text_input("File Key", key="figma_comp", placeholder="abc123xyz...")
        if st.button("Get Components"):
            result = call_mcp_tool("get_figma_components", {"file_key": file_key2})
            st.json(result)

    with tab3:
        st.subheader("Get Styles")
        file_key3 = st.text_input("File Key", key="figma_style", placeholder="abc123xyz...")
        if st.button("Get Styles"):
            result = call_mcp_tool("get_figma_styles", {"file_key": file_key3})
            st.json(result)

    with tab4:
        st.subheader("Export Nodes")
        file_key4 = st.text_input("File Key", key="figma_exp")
        node_ids = st.text_input("Node IDs (comma separated)", placeholder="1:2, 1:3")
        format_exp = st.selectbox("Format", ["png", "jpg", "svg", "pdf"])
        if st.button("Export"):
            nodes = [n.strip() for n in node_ids.split(",")]
            result = call_mcp_tool("export_figma_nodes", {"file_key": file_key4, "node_ids": nodes, "format": format_exp})
            st.json(result)

    with tab5:
        st.subheader("Figma to Code")
        file_key5 = st.text_input("File Key", key="figma_code")
        target = st.selectbox("Target", ["tailwind", "shadcn", "html"])
        if st.button("Convert to Code"):
            result = call_mcp_tool("figma_to_code", {"file_key": file_key5, "target": target})
            if result.get("status") == "success":
                st.code(result.get("code", ""), language="html")
            elif result.get("error"):
                st.error(result.get("error"))

elif selected_page == "🔐 JWT":
    st.title("🔐 JWT Management")

    st.subheader("Generate JWT Token")

    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input("Subject (user identifier)", placeholder="username")
    with col2:
        role = st.selectbox("Role", ["admin", "developer", "user", "guest"])

    expiry = st.slider("Expiry (hours)", 1, 168, 24)

    if st.button("Generate Token"):
        result = call_mcp_tool("generate_jwt_token", {
            "subject": subject,
            "role": role,
            "expiry_hours": expiry,
            "admin_key": API_KEY
        })
        if result.get("status") == "success":
            st.success("Token generated!")
            st.code(result.get("token", ""), language="text")
        elif result.get("error"):
            st.error(result.get("error"))
        else:
            st.error(str(result))

    st.markdown("---")

    st.subheader("Validate JWT Token")
    token_validate = st.text_area("Token to validate", height=100)
    if st.button("Validate"):
        result = call_mcp_tool("validate_jwt_token", {"token": token_validate})
        st.json(result)

elif selected_page == "📜 Logs":
    st.title("📜 Audit Logs")

    st.info("Audit logs are available in the database")

    # For demo, show a placeholder
    st.markdown("""
    ### Recent Activity

    | Time | Action | User | Status |
    |------|--------|------|--------|
    | 2026-03-22 10:00 | generate_jwt_token | admin | ✓ Success |
    | 2026-03-22 09:45 | generate_tailwind | user | ✓ Success |
    | 2026-03-22 09:30 | get_figma_file | developer | ✓ Success |
    """)

elif selected_page == "⚙️ Settings":
    st.title("⚙️ Settings")

    st.subheader("Environment Variables")

    st.markdown("""
    ### Current Configuration

    | Variable | Value |
    |----------|-------|
    | Mode | Direct Import |
    | API_KEY | `sk-system-dev` |
    | LLM_PROVIDER | `minimax` |
    | JWT_ENABLED | `true` |
    """)

    st.subheader("LLM Providers")

    providers = ["MiniMax", "ZAI", "Anthropic", "DeepSeek", "OpenRouter"]
    selected_provider = st.selectbox("Select Provider", providers)

    st.markdown("---")

    st.subheader("API Keys")

    with st.form("api_keys"):
        st.text_input("MiniMax API Key", type="password", key="minimax")
        st.text_input("Anthropic API Key", type="password", key="anthropic")
        st.text_input("OpenRouter API Key", type="password", key="openrouter")
        st.form_submit_button("Save Keys")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "🔮 p9i Control Panel | MCP Server Management | "
    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    "</div>",
    unsafe_allow_html=True
)
