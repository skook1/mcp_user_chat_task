import json
from typing import List, Optional, Dict, Any

from controllers.clients.llm_client import SimpleLLMClient
from controllers.clients.mcp_client import SimpleMCPClient


class SimpleChatAgent:
    def __init__(self):
        self.mcp_client: Optional[SimpleMCPClient] = None
        self.llm_client = SimpleLLMClient()
        self.tools: List[Dict[str, Any]] = []

    async def initialize(self) -> bool:
        try:
            self.mcp_client = SimpleMCPClient()
            connected = await self.mcp_client.connect()
            if not connected:
                print("MCP server unavailable. Tools: 0")
                self.tools = []
                self.mcp_client = None
                return False

            mcp_tools = await self.mcp_client.list_tools()
            self.tools = [{
                "tool_name": tool.name,
                "input_schema": tool.inputSchema,
                "description": tool.description
            } for tool in mcp_tools]
            return True
        except Exception as e:
            print(f"Error during initialization: {e}")
            self.tools = []
            return False

    async def chat(self, message: str) -> str:
        if not self.tools:
            return await self.llm_client.chat(message)

        prompt = self._build_tool_choice_prompt(message)
        chosen_tool_response = await self.llm_client.chat(prompt)

        try:
            chosen_tool = json.loads(chosen_tool_response)
            tool_name = chosen_tool.get("tool_name")
            tool_args = chosen_tool.get("arguments", {})
        except json.JSONDecodeError:
            print("Invalid JSON response from LLM, falling back to simple chat.")
            return await self.llm_client.chat(message)
        except KeyError:
            print("Missing 'tool_name' or 'arguments' in LLM response, falling back to simple chat.")
            return await self.llm_client.chat(message)

        if tool_name and self.mcp_client:
            try:
                tool_result = await self.mcp_client.call_tool(tool_name, tool_args)
                human_readable = await self.llm_client.chat(
                    f"Prepare an exhaustive answer to what the user asked based on:\n{tool_result}"
                )
                return human_readable
            except Exception as e:
                print(f"Error calling tool '{tool_name}': {e}, falling back to simple chat.")
                return await self.llm_client.chat(message)

        return await self.llm_client.chat(message)

    def _build_tool_choice_prompt(self, user_message: str) -> str:
        tools_info = [
            f"Name: {t['tool_name']}, Description: {t['description']}, Input Schema: {json.dumps(t['input_schema'])}"
            for t in self.tools
        ]
        prompt = f"""
        You have several active tools: {json.dumps(tools_info, indent=2)}
        User query: "{user_message}"
        Determine if you can use the tool from the list.
        Return the data in this format:
        {{"tool_name": "<tool name>", "arguments": {{<arguments from input_schema>}}}}
        """
        return prompt

    async def cleanup(self):
        if self.mcp_client:
            await self.mcp_client.disconnect()
            self.mcp_client = None

    def get_available_tools(self) -> List[Dict[str, Any]]:
        return self.tools
