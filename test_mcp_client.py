#!/usr/bin/env python3
"""Test MCP server via SSE transport"""
import asyncio
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
import json
import time

async def main():
    url = "http://localhost:8000/sse"
    print(f"Connecting to MCP server at {url}...")

    # Wait for server to be ready
    print("Waiting for server to be ready...")
    await asyncio.sleep(2)

    async with sse_client(url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as client:
            # MUST initialize before any other method
            print("Initializing...")
            init_result = await client.initialize()
            print(f"Server: {init_result.serverInfo.name} v{init_result.serverInfo.version}")

            # List available tools
            print("\n=== Listing tools ===")
            tools_result = await client.list_tools()
            tools = tools_result.tools
            print(f"Found {len(tools)} tools:")
            for tool in tools[:5]:
                print(f"  - {tool.name}: {tool.description[:50]}...")

            # Try calling a simple tool
            print("\n=== Calling list_prompts tool ===")
            try:
                result = await client.call_tool("list_prompts", {})
                print(f"Result: {result}")
            except Exception as e:
                print(f"Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())