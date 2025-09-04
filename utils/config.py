import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash-lite")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
