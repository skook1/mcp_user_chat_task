from controllers.chats.chat_agent import SimpleChatAgent


class SimpleChat:
    def __init__(self):
        self.agent = SimpleChatAgent()

    async def run(self):
        print("You started the chat")
        print("=" * 40)

        print("Loading...")
        if not await self.agent.initialize():
            print("Problem with MCP connection")

        tools = self.agent.get_available_tools()

        if tools:
            print(f"Available tools:")
            for tool in tools:
                print(f"- Name: {tool['tool_name']}")
                print(f"  Description: {tool['description']}")
            print("You can use them by typing their name followed by input")
        else:
            print("No tools found - AI will work directly with LLM")

        print("\nType 'quit' to exit\n" + "-" * 40)

        try:
            while True:
                user_input = input("You: ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                if not user_input:
                    continue

                response = await self.agent.chat(user_input)
                print(f"Bot: {response}\n")

        except KeyboardInterrupt:
            print("\nChat ended")

        finally:
            await self.agent.cleanup()


async def run_chat():
    chat = SimpleChat()
    await chat.run()
