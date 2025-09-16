import os
from langchain_groq import ChatGroq

from src.config import settings, logger

os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY


class Groq:

    def __init__(self, system_text="You are an helpful AI assistant."):
        """
        Create Groq chat llm given system text
        """
        try:
            self.system_text = system_text
            self.llm = ChatGroq(
                model=settings.MODEL_NAME,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                reasoning_format="parsed" if settings.REASONING else None,
                timeout=settings.TIMEOUT,
                max_retries=settings.MAX_RETERIES,
            )
        except Exception as e:
            logger.error(f"Error at creating model: {e}")

    def ask(self, query: str) -> str:
        """
        Generate response based on the system text and given query
        :param query: given query
        :return:
        """
        try:
            if isinstance(query, list):
                messages = [
                    {
                        "role": "system",
                        "content": [
                                       {
                                           "type": "text",
                                           "text": self.system_text
                                       },
                        ]
                    }
                ] + query
            else:
                messages = [
                    ("system", self.system_text),
                    ("human", f"{query}"),
                ]
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error at generating response: {e}")
            return f"Error at generating response: {e}"

    def ask_visual(self, query) -> str:
        pass