#!/usr/bin/env python3
"""
p9i Client CLI - Global MCP client for Claude Code

Usage:
    p9i init                      # Initialize configuration
    p9i connect [remote|local]    # Connect to MCP server
    p9i disconnect               # Disconnect (remove MCP settings)
    p9i status                  # Show connection status
    p9i profile list            # List available profiles
    p9i profile add <name>      # Add a new profile
    p9i profile use <name>      # Switch to profile
    p9i profile remove <name>   # Remove a profile

Configuration is stored in ~/.config/p9i/
"""

import os
import sys
import json
import argparse
import getpass
import configparser
from pathlib import Path
from typing import Optional, Dict, Any

# Constants
CONFIG_DIR = Path.home() / ".config" / "p9i"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
PROFILES_DIR = CONFIG_DIR / "profiles"
CLAUDE_SETTINGS = Path.home() / ".claude" / "settings.json"

# Colors
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
RED = "\033[0;31m"
NC = "\033[0m"


def color(text: str, color: str) -> str:
    """Colorize text."""
    return f"{color}{text}{NC}"


def ensure_config_dir():
    """Ensure configuration directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    """Load main configuration."""
    ensure_config_dir()

    config = {
        "active_profile": "default",
        "bridge_path": str(CONFIG_DIR / "bridge.conf"),
    }

    if CONFIG_FILE.exists():
        parser = configparser.ConfigParser()
        parser.read(CONFIG_FILE)
        if parser.has_section("main"):
            config.update(dict(parser.items("main")))

    return config


def save_config(config: Dict[str, Any]):
    """Save main configuration."""
    ensure_config_dir()

    parser = configparser.ConfigParser()
    parser.add_section("main")
    for key, value in config.items():
        parser.set("main", key, str(value))

    with open(CONFIG_FILE, "w") as f:
        parser.write(f)


def load_profile(name: str) -> Optional[Dict[str, str]]:
    """Load a profile by name."""
    profile_file = PROFILES_DIR / f"{name}.conf"
    if not profile_file.exists():
        return None

    parser = configparser.ConfigParser()
    parser.read(profile_file)

    profile = {"name": name}
    if parser.has_section("profile"):
        profile.update(dict(parser.items("profile")))

    return profile


def save_profile(name: str, profile: Dict[str, str]):
    """Save a profile."""
    ensure_config_dir()

    parser = configparser.ConfigParser()
    parser.add_section("profile")
    for key, value in profile.items():
        if key != "name":
            parser.set("profile", key, str(value))

    profile_file = PROFILES_DIR / f"{name}.conf"
    with open(profile_file, "w") as f:
        parser.write(f)


def list_profiles() -> list:
    """List all available profiles."""
    ensure_config_dir()
    profiles = []
    for f in PROFILES_DIR.glob("*.conf"):
        profiles.append(f.stem)
    return profiles


def get_active_profile() -> Optional[str]:
    """Get the name of the active profile."""
    config = load_config()
    return config.get("active_profile", "default")


def get_claude_settings() -> Dict[str, Any]:
    """Load Claude Code settings."""
    if not CLAUDE_SETTINGS.exists():
        return {}

    try:
        with open(CLAUDE_SETTINGS) as f:
            return json.load(f)
    except:
        return {}


def save_claude_settings(settings: Dict[str, Any]):
    """Save Claude Code settings."""
    CLAUDE_SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    with open(CLAUDE_SETTINGS, "w") as f:
        json.dump(settings, f, indent=2)


def update_claude_settings_remote(profile: Dict[str, str]):
    """Update Claude settings for remote (HTTP) connection."""
    settings = get_claude_settings()

    mcp_servers = settings.get("mcpServers", {})

    mcp_servers["p9i"] = {
        "type": "http",
        "url": profile.get("url", "https://p9i.ru/mcp"),
    }

    # Add API key header if configured
    if profile.get("api_key"):
        mcp_servers["p9i"]["headers"] = {
            "X-API-Key": profile["api_key"]
        }

    settings["mcpServers"] = mcp_servers
    save_claude_settings(settings)


def update_claude_settings_local(profile: Dict[str, str]):
    """Update Claude settings for local (stdio bridge) connection."""
    settings = get_claude_settings()

    bridge_path = profile.get("bridge_path", str(CONFIG_DIR / "bridge.py"))
    bridge_url = profile.get("url", "http://localhost:8000/mcp")

    mcp_servers = settings.get("mcpServers", {})

    mcp_servers["p9i"] = {
        "command": "python3",
        "args": [bridge_path, "--url", bridge_url],
    }

    # Add API key if configured
    if profile.get("api_key"):
        mcp_servers["p9i"]["env"] = {
            "P9I_API_KEY": profile["api_key"]
        }

    settings["mcpServers"] = mcp_servers
    save_claude_settings(settings)


def remove_claude_settings():
    """Remove p9i from Claude settings."""
    settings = get_claude_settings()
    mcp_servers = settings.get("mcpServers", {})

    if "p9i" in mcp_servers:
        del mcp_servers["p9i"]
        settings["mcpServers"] = mcp_servers
        save_claude_settings(settings)


def cmd_init(args):
    """Initialize p9i configuration."""
    ensure_config_dir()

    print(color("Initializing p9i client configuration...", BLUE))
    print()

    # Get server URL
    default_url = getattr(args, "url", None) or "https://p9i.ru/mcp"
    url = input(f"Server URL [{color(default_url, YELLOW)}]: ").strip() or default_url

    # Get API key (will be stored securely)
    api_key = getattr(args, "api_key", None) or os.getenv("P9I_API_KEY", "")
    if not api_key:
        api_key = getpass.getpass("API Key: ").strip()

    # Get email for certificates
    email = getattr(args, "email", None) or f"admin@{url.split('//')[1].split('/')[0] if '//' in url else 'p9i.ru'}"
    email = input(f"Email for SSL certificates [{color(email, YELLOW)}]: ").strip() or email

    # Save default profile
    profile = {
        "name": "default",
        "url": url,
        "api_key": api_key,
        "mode": "remote",
    }
    save_profile("default", profile)

    # Update main config
    config = load_config()
    config["active_profile"] = "default"
    save_config(config)

    # Update Claude settings
    update_claude_settings_remote(profile)

    print()
    print(color("✓ Configuration saved to", GREEN), CONFIG_DIR)
    print(color("✓ Profile 'default' created", GREEN))
    print(color("✓ Claude Code settings updated", GREEN))
    print()
    print(color("Run 'p9i status' to verify connection", YELLOW))


def cmd_connect(args):
    """Connect to MCP server."""
    config = load_config()
    profile_name = args.profile or config.get("active_profile", "default")
    mode = args.mode or "remote"

    profile = load_profile(profile_name)
    if not profile:
        print(color(f"Profile '{profile_name}' not found. Run 'p9i init' first.", RED))
        sys.exit(1)

    if mode == "remote":
        update_claude_settings_remote(profile)
        print(color(f"✓ Connected to {profile.get('url', 'p9i.ru')} (remote mode)", GREEN))
    else:
        update_claude_settings_local(profile)
        print(color(f"✓ Connected to {profile.get('url', 'localhost:8000')} (local mode)", GREEN))

    print(color("Restart Claude Code to use the new connection.", YELLOW))


def cmd_disconnect(args):
    """Disconnect (remove MCP settings)."""
    remove_claude_settings()
    print(color("✓ Disconnected. MCP settings removed from Claude Code.", GREEN))
    print(color("Restart Claude Code to apply changes.", YELLOW))


def cmd_status(args):
    """Show connection status."""
    config = load_config()
    active_profile = config.get("active_profile", "default")
    profile = load_profile(active_profile)

    print(color("=== p9i Client Status ===", BLUE))
    print()

    print(color("Configuration:", YELLOW))
    print(f"  Config dir: {CONFIG_DIR}")
    print(f"  Active profile: {active_profile}")
    print()

    if profile:
        print(color("Active Profile:", YELLOW))
        print(f"  Name: {profile.get('name', active_profile)}")
        print(f"  URL: {profile.get('url', 'N/A')}")
        print(f"  API Key: {'***' + profile.get('api_key', '')[-4:] if profile.get('api_key') else 'Not set'}")
        print(f"  Mode: {profile.get('mode', 'remote')}")
        print()
    else:
        print(color("No active profile found. Run 'p9i init' to configure.", RED))
        print()

    print(color("Claude Code Settings:", YELLOW))
    settings = get_claude_settings()
    mcp_servers = settings.get("mcpServers", {})

    if "p9i" in mcp_servers:
        print(color("  ✓ p9i is configured", GREEN))
        srv = mcp_servers["p9i"]
        print(f"  Type: {srv.get('type', 'command' if 'command' in srv else 'unknown')}")
        if "url" in srv:
            print(f"  URL: {srv['url']}")
        if "command" in srv:
            print(f"  Command: {srv['command']} {' '.join(srv.get('args', []))}")
    else:
        print(color("  ✗ p9i not configured", RED))

    print()
    print(color("Available Profiles:", YELLOW))
    profiles = list_profiles()
    if profiles:
        for p in sorted(profiles):
            marker = color(" (*)", GREEN) if p == active_profile else ""
            print(f"  - {p}{marker}")
    else:
        print(color("  No profiles found", RED))


def cmd_profile_list(args):
    """List all profiles."""
    profiles = list_profiles()
    active = get_active_profile()

    print(color("Available Profiles:", BLUE))
    print()
    for p in sorted(profiles):
        marker = color(" (active)", GREEN) if p == active else ""
        print(f"  {p}{marker}")

    if not profiles:
        print(color("No profiles found. Run 'p9i init' to create one.", YELLOW))


def cmd_profile_add(args):
    """Add a new profile."""
    name = args.name

    if load_profile(name):
        print(color(f"Profile '{name}' already exists. Use 'p9i profile use {name}' to switch.", YELLOW))
        sys.exit(1)

    print(color(f"Creating profile '{name}'...", BLUE))
    print()

    url = input(f"Server URL [{color('https://p9i.ru/mcp', YELLOW)}]: ").strip() or "https://p9i.ru/mcp"
    api_key = getpass.getpass("API Key: ").strip()

    profile = {
        "name": name,
        "url": url,
        "api_key": api_key,
        "mode": "remote",
    }

    save_profile(name, profile)
    print(color(f"✓ Profile '{name}' created", GREEN))


def cmd_profile_use(args):
    """Switch to a profile."""
    name = args.name
    profile = load_profile(name)

    if not profile:
        print(color(f"Profile '{name}' not found.", RED))
        sys.exit(1)

    config = load_config()
    config["active_profile"] = name
    save_config(config)

    print(color(f"✓ Switched to profile '{name}'", GREEN))

    # Update Claude settings based on profile mode
    mode = profile.get("mode", "remote")
    if mode == "remote":
        update_claude_settings_remote(profile)
    else:
        update_claude_settings_local(profile)

    print(color("Claude Code settings updated. Restart Claude Code to use.", YELLOW))


def cmd_profile_remove(args):
    """Remove a profile."""
    name = args.name

    if name == "default":
        print(color("Cannot remove 'default' profile.", RED))
        sys.exit(1)

    profile_file = PROFILES_DIR / f"{name}.conf"
    if profile_file.exists():
        profile_file.unlink()
        print(color(f"✓ Profile '{name}' removed", GREEN))
    else:
        print(color(f"Profile '{name}' not found.", RED))
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="p9i Client CLI - Global MCP client for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize configuration")
    init_parser.add_argument("--url", "-u", help="Server URL")
    init_parser.add_argument("--api-key", "-k", help="API key")
    init_parser.add_argument("--email", "-e", help="Email for SSL certificates")

    # connect command
    connect_parser = subparsers.add_parser("connect", help="Connect to MCP server")
    connect_parser.add_argument("mode", nargs="?", choices=["remote", "local"], default="remote",
                               help="Connection mode (default: remote)")
    connect_parser.add_argument("--profile", "-p", help="Profile name")

    # disconnect command
    subparsers.add_parser("disconnect", help="Disconnect (remove MCP settings)")

    # status command
    subparsers.add_parser("status", help="Show connection status")

    # profile subcommands
    profile_parser = subparsers.add_parser("profile", help="Manage profiles")
    profile_subparsers = profile_parser.add_subparsers(dest="profile_command")

    profile_list = profile_subparsers.add_parser("list", help="List all profiles")
    profile_add = profile_subparsers.add_parser("add", help="Add a new profile")
    profile_add.add_argument("name", help="Profile name")
    profile_use = profile_subparsers.add_parser("use", help="Switch to a profile")
    profile_use.add_argument("name", help="Profile name")
    profile_remove = profile_subparsers.add_parser("remove", help="Remove a profile")
    profile_remove.add_argument("name", help="Profile name")

    args = parser.parse_args()

    # Dispatch
    if args.command == "init":
        cmd_init(args)
    elif args.command == "connect":
        cmd_connect(args)
    elif args.command == "disconnect":
        cmd_disconnect(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "profile":
        if args.profile_command == "list":
            cmd_profile_list(args)
        elif args.profile_command == "add":
            cmd_profile_add(args)
        elif args.profile_command == "use":
            cmd_profile_use(args)
        elif args.profile_command == "remove":
            cmd_profile_remove(args)
        else:
            profile_parser.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
