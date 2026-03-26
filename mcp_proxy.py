#!/usr/bin/env python3
"""
MCP HTTP-to-STDIO Proxy for Claude Code

Bridges HTTP MCP server to STDIO for Claude Code integration.
Uses FastMCP's create_proxy when available, falls back to manual implementation.

Usage:
    # Development (local docker-compose):
    MCP_PROXY_URL=http://localhost:8000/mcp python mcp_proxy.py

    # Production (K8s):
    MCP_PROXY_URL=http://mcp.coderweb.ru/mcp python mcp_proxy.py

Environment:
    MCP_PROXY_URL - HTTP MCP server URL (default: http://localhost:8000/mcp)
    MCP_PROXY_AUTH - API key for auth (X-API-Key header)
    P9I_API_KEY - Alternative way to set auth
"""

import os
import sys
import json
import asyncio
import logging
from typing import Any, Dict

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def get_proxy_url() -> str:
    """Get MCP server URL from environment."""
    return os.getenv("MCP_PROXY_URL", "http://localhost:8000/mcp")


def get_auth() -> str:
    """Get API key from environment."""
    return os.getenv("MCP_PROXY_AUTH", os.getenv("P9I_API_KEY", ""))


async def run_proxy():
    """Run the HTTP-to-STDIO proxy."""
    url = get_proxy_url()
    auth = get_auth()

    print(f"Starting MCP proxy: {url}", file=sys.stderr)
    if auth:
        print("Using API key auth", file=sys.stderr)

    # Try FastMCP create_proxy - best option when available
    try:
        from fastmcp.server import create_proxy
        print("Using FastMCP create_proxy...", file=sys.stderr)

        proxy = create_proxy(url, name="p9i-proxy")

        # Set auth if provided
        if auth:
            os.environ["P9I_API_KEY"] = auth

        # Run as stdio - exposes remote MCP via stdin/stdout
        proxy.run()
        return

    except ImportError:
        print("FastMCP not available in current environment", file=sys.stderr)
    except Exception as e:
        print(f"FastMCP proxy error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

    # Fallback: manual HTTP client implementation
    print("Using manual HTTP-to-STDIO proxy...", file=sys.stderr)
    await manual_proxy(url, auth)


async def manual_proxy(url: str, auth: str):
    """Manual HTTP-to-STDIO proxy using MCP SDK."""
    from mcp.client.sse import sse_client
    from mcp.client.session import ClientSession

    headers = {
        "Accept": "application/json, text/event-stream"
    }
    if auth:
        headers["X-API-Key"] = auth

    print(f"Connecting to {url}...", file=sys.stderr)

    try:
        async with sse_client(url, headers=headers) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as client:
                # Initialize the session
                init_result = await client.initialize()
                print(f"Connected: {init_result.serverInfo.name} v{init_result.serverInfo.version}", file=sys.stderr)

                # Get tools
                tools_result = await client.list_tools()
                print(f"Tools available: {len(tools_result.tools)}", file=sys.stderr)

                # Main loop - read JSON-RPC from stdin, call MCP, write response
                while True:
                    line = sys.stdin.readline()
                    if not line:
                        break

                    line = line.strip()
                    if not line:
                        continue

                    try:
                        request = json.loads(line)
                        method = request.get("method", "")
                        req_id = request.get("id")
                        params = request.get("params", {})

                        # Handle MCP methods
                        if method == "initialize":
                            result = await client.initialize(
                                protocolVersion=params.get("protocolVersion", "2024-11-05"),
                                capabilities=params.get("capabilities", {}),
                                clientInfo=params.get("clientInfo", {})
                            )
                            response = {"jsonrpc": "2.0", "id": req_id, "result": {
                                "protocolVersion": result.protocolVersion,
                                "capabilities": result.capabilities,
                                "serverInfo": {"name": result.serverInfo.name, "version": result.serverInfo.version}
                            }}

                        elif method == "tools/list":
                            tools = await client.list_tools()
                            response = {"jsonrpc": "2.0", "id": req_id, "result": {
                                "tools": [{"name": t.name, "description": t.description, "inputSchema": t.inputSchema}
                                         for t in tools.tools]
                            }}

                        elif method == "tools/call":
                            tool_name = params.get("name")
                            tool_args = params.get("arguments", {})
                            result = await client.call_tool(tool_name, tool_args)
                            # Format result for MCP
                            content = []
                            for item in result:
                                if hasattr(item, 'text'):
                                    content.append({"type": "text", "text": item.text})
                                elif isinstance(item, dict):
                                    content.append(item)
                                else:
                                    content.append({"type": "text", "text": str(item)})
                            response = {"jsonrpc": "2.0", "id": req_id, "result": {"content": content}}

                        elif method == "resources/list":
                            resources = await client.list_resources()
                            response = {"jsonrpc": "2.0", "id": req_id, "result": {
                                "resources": [{"uri": r.uri, "name": r.name, "description": r.description}
                                            for r in resources.resources] if resources.resources else []
                            }}

                        elif method == "prompts/list":
                            prompts = await client.list_prompts()
                            response = {"jsonrpc": "2.0", "id": req_id, "result": {
                                "prompts": [{"name": p.name, "description": p.description}
                                          for p in prompts.prompts] if prompts.prompts else []
                            }}

                        else:
                            response = {"jsonrpc": "2.0", "id": req_id,
                                      "error": {"code": -32601, "message": f"Method not supported: {method}"}}

                        print(json.dumps(response), flush=True)

                    except json.JSONDecodeError as e:
                        error = {"jsonrpc": "2.0", "id": None,
                                "error": {"code": -32700, "message": f"Parse error: {e}"}}
                        print(json.dumps(error), flush=True)
                    except Exception as e:
                        error = {"jsonrpc": "2.0", "id": None,
                                "error": {"code": -32603, "message": f"Internal error: {e}"}}
                        print(json.dumps(error), flush=True)

    except Exception as e:
        print(f"Proxy error: {e}", file=sys.stderr)
        raise


def main():
    try:
        asyncio.run(run_proxy())
    except KeyboardInterrupt:
        print("Proxy stopped", file=sys.stderr)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()