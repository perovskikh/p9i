"""
p9i MCP Integration - Claude Cookbooks Pattern

Following patterns from:
- tool_use/mcp_integration.py
- advanced_techniques/mcp_config.py

Usage:
    python examples/p9i_mcp_integration.py
"""

import asyncio
import os
from pathlib import Path
from typing import Optional

# Claude Cookbooks MCP pattern imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic


class P9iMCPIntegration:
    """MCP Integration for p9i server following Claude Cookbooks patterns."""

    def __init__(self):
        self.client: Optional[Anthropic] = None
        self.mcp_session: Optional[ClientSession] = None
        self.mcp_tools: list = []
        self._initialized = False

    async def initialize(self):
        """Initialize MCP connection and Anthropic client."""
        # Load environment
        from dotenv import load_dotenv
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)

        # Claude Cookbooks pattern: StdioServerParameters
        server_params = StdioServerParameters(
            command="docker",
            args=[
                "run", "--rm", "-i",
                "-v", str(env_path) + ":/app/.env",
                "-v", str(Path.cwd()) + ":/project",
                "-v", str(Path.cwd() / "memory") + ":/app/memory",
                "p9i"
            ],
            env={
                "MCP_TRANSPORT": "stdio",
                "JWT_ENABLED": os.getenv("JWT_ENABLED", "false")
            }
        )

        # Claude Cookbooks pattern: stdio_client with ClientSession
        async with stdio_client(server_params) as (read, write):
            self.mcp_session = ClientSession(read, write)
            await self.mcp_session.initialize()

            # Claude Cookbooks pattern: list_tools()
            tools_response = await self.mcp_session.list_tools()
            self.mcp_tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                for tool in tools_response.tools
            ]

            print(f"Connected to p9i MCP server")
            print(f"Available tools: {len(self.mcp_tools)}")
            for tool in self.mcp_tools:
                print(f"  - {tool['name']}: {tool['description'][:50]}...")

        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("ZAI_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY or ZAI_API_KEY required")

        self.client = Anthropic(api_key=api_key)
        self._initialized = True

    async def execute_tool(self, tool_name: str, arguments: dict) -> dict:
        """Execute MCP tool - Claude Cookbooks pattern: call_tool()"""
        if not self.mcp_session:
            raise RuntimeError("MCP session not initialized")

        result = await self.mcp_session.call_tool(tool_name, arguments)
        return {"status": "success", "result": result}

    async def chat_with_p9i(self, user_message: str) -> str:
        """Chat with Claude using p9i MCP tools - Claude Cookbooks pattern"""
        if not self.client or not self.mcp_session:
            raise RuntimeError("Not initialized")

        # Claude Cookbooks pattern: tools parameter
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": user_message}],
            tools=self.mcp_tools
        )

        # Handle tool use blocks - Claude Cookbooks pattern
        for content in response.content:
            if content.type == "tool_use":
                tool_name = content.name
                tool_args = content.input

                # Execute tool via MCP
                result = await self.execute_tool(tool_name, tool_args)

                # Continue conversation with result
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4096,
                    messages=[
                        {"role": "user", "content": user_message},
                        {
                            "role": "assistant",
                            "content": [content.model_dump()],
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": content.id,
                                    "content": str(result),
                                }
                            ],
                        },
                    ],
                    tools=self.mcp_tools,
                )

        return response.content[0].text

    async def close(self):
        """Close MCP session - Claude Cookbooks pattern"""
        if self.mcp_session:
            await self.mcp_session.close()


async def main():
    """Example usage following Claude Cookbooks patterns"""
    mcp_integration = P9iMCPIntegration()

    try:
        # Claude Cookbooks pattern: initialize
        await mcp_integration.initialize()

        # Example: Use p9i tools
        result = await mcp_integration.execute_tool(
            "list_prompts",
            {}
        )
        print(f"\nList prompts result: {result}")

        # Example: Chat with p9i
        # response = await mcp_integration.chat_with_p9i(
        #     "Создай эндпоинт для пользователей. p9i"
        # )
        # print(f"\nChat response: {response}")

    finally:
        # Claude Cookbooks pattern: close session
        await mcp_integration.close()


if __name__ == "__main__":
    asyncio.run(main())
