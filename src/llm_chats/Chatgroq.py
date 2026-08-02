import os

from langchain_core.messages import AIMessage, BaseMessage
from langchain_groq import ChatGroq
from typing import  Union

from src.config import settings, logger
from src.utils.create_visual_payload import (
    visual_path,
    visual_public_url,
    is_url,
    is_local_path
)

if not settings.GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in settings/.env")
os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY


class Groq:

    def __init__(self, system_text="You are an helpful AI assistant."):
        """
        Create Groq chat llm given system text
        """
        self.system_text = system_text
        common_kwargs = dict(
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            reasoning_format="parsed" if settings.REASONING else None,
            timeout=settings.TIMEOUT,
            max_retries=settings.MAX_RETERIES,
        )
        self.llm = ChatGroq(model=settings.MODEL_NAME, **common_kwargs)
        self.backup_llm = ChatGroq(model=settings.BACKUP_MODEL_NAME, **common_kwargs)

    def ask(self, query: Union[str, list]) -> BaseMessage:
        """
        Generate response based on the system text and given query
        :param query: given query
        :return: response, always a BaseMessage (an AIMessage wraps any error)
        """
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
        try:
            return self.llm.invoke(messages)
        except Exception as e:
            logger.warning(f"Model changes from {settings.MODEL_NAME} to {settings.BACKUP_MODEL_NAME} due to error {e}")
        try:
            return self.backup_llm.invoke(messages)
        except Exception as e:
            logger.error(f"Error at generating response: {e}")
            return AIMessage(content=f"Error at generating response: {e}")

    def ask_visual(self, query: str, url: str) -> BaseMessage:
        """
        Generate response based on the system text, given query, and a visual (image) file
        :param query: given query
        :param url: public URL or local path to visual file
        :return: response, always a BaseMessage (an AIMessage wraps any error)
        """
        if is_url(url):
            query = visual_public_url(query, url)
        elif is_local_path(url):
            query = visual_path(query, url)
        else:
            return AIMessage(content="Could not find or open the visual URL")
        return self.ask(query)