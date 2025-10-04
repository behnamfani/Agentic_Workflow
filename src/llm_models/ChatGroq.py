import os

from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from typing import  Union

from src.config import settings, logger
from src.utils.create_visual_payload import (
    visual_path,
    visual_public_url,
    is_url,
    is_local_path
)

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

    def ask(self, query: Union[str, list]) -> BaseMessage | str:
        """
        Generate response based on the system text and given query
        :param query: given query
        :return: response
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
            return self.llm.invoke(messages)
        except Exception as e:
            logger.error(f"Error at generating response: {e}")
            return f"Error at generating response: {e}"

    def ask_visual(self, query, url) -> str:
        """

        :param query: given query
        :param url: public URL or local path to visual file
        :return: response
        """
        if is_url(url):
            query = visual_public_url(query, url)
        elif is_local_path(url):
            query = visual_path(query, url)
        else:
            return "Could not find or open the visual URL"
        return self.ask(query)