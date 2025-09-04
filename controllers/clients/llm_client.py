from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from utils.config import MODEL_NAME, TEMPERATURE, GEMINI_API_KEY


class SimpleLLMClient:

    def __init__(self):
        self.model = self._create_model()

    def _create_model(self):
        return ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            google_api_key=GEMINI_API_KEY,
            temperature=TEMPERATURE
        )

    async def chat(self, message: str) -> str:
        try:
            response = await self.model.ainvoke([HumanMessage(content=message)])
            return response.content
        except Exception as e:
            return f"Error: {str(e)}"
