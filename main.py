import asyncio
import sys
from controllers.chats.chat import run_chat

if __name__ == "__main__":
    try:
        asyncio.run(run_chat())
    except KeyboardInterrupt:
        print("\nExit")
    except Exception as e:
        sys.exit(1)
