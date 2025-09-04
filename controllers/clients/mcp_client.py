from typing import List, Dict, Any, Optional
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import Tool, TextContent

from utils.config import MCP_SERVER_URL


class SimpleMCPClient:
    def __init__(self):
        self.server_url = MCP_SERVER_URL
        self.session: Optional[ClientSession] = None
        self._exit_stack: Optional[AsyncExitStack] = None

    async def connect(self) -> bool:
        if self._exit_stack:
            await self.disconnect()

        try:
            async with AsyncExitStack() as stack:
                try:
                    client_streams = await stack.enter_async_context(
                        streamablehttp_client(self.server_url)
                    )
                except ConnectionRefusedError as e:
                    print(f"MCP connection failed: {e}")
                    return False

                read_stream, write_stream, _ = client_streams

                session = await stack.enter_async_context(
                    ClientSession(read_stream, write_stream)
                )
                await session.initialize()

                self.session = session
                self._exit_stack = stack.pop_all()
                print("MCP connection successful.")
                return True

        except Exception as e:
            print(f"An unhandled error occurred during MCP connection: {e}")
            await self.disconnect()
            return False

    async def disconnect(self):
        if self._exit_stack:
            try:
                await self._exit_stack.aclose()
            except Exception as e:
                print(f"Error during disconnect: {e}")
            self._exit_stack = None
        self.session = None

    async def list_tools(self) -> List[Tool]:
        if not self.session:
            return []
        tools_response = await self.session.list_tools()
        return tools_response.tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        if not self.session:
            return "MCP unavailable, cannot call tool"
        result = await self.session.call_tool(tool_name, arguments)
        if result.content:
            return "\n".join(
                content.text for content in result.content if isinstance(content, TextContent)
            )
        return "No result from tool"
