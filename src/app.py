"""
Application class for managing chatbot interactions.
"""
import logging
from typing import Optional, Tuple, List

from src.agents.chatbot import Chatbot


logger = logging.getLogger(__name__)


class App:
    """
    Application wrapper for the Chatbot.
    Manages chatbot initialization and chat interactions.
    """

    def __init__(
        self,
        system_text: str = "You are a helpful assistant.",
        chat_history_limit: int = 8,
        show_graph: bool = False,
    ):
        """
        Initialize the App with a Chatbot instance.

        Args:
            system_text (str): System prompt for the chatbot.
            chat_history_limit (int): Maximum conversation history to keep.
            show_graph (bool): Whether to display the workflow graph.
        """
        logger.info(f"Initializing App with system_text: {system_text[:50]}...")
        self.chatbot = Chatbot(
            system_text=system_text,
            chat_history_limit=chat_history_limit,
            show_graph=show_graph,
        )
        self.messages: List = []
        logger.info("App initialized successfully.")

    def ask(self, query: str) -> Tuple[str, List]:
        """
        Send a query to the chatbot and get a response.

        Args:
            query (str): User query.

        Returns:
            Tuple[str, List]: Response text and updated message history.
        """
        logger.info(f"Processing query: {query[:50]}...")
        try:
            response, messages = self.chatbot.ask(query, messages=self.messages)
            self.messages = messages
            logger.info(f"Response generated successfully.")
            return response, messages
        except Exception as e:
            logger.error(f"Error during ask: {e}")
            raise

    def stream_ask(self, query: str):
        """
        Stream a response from the chatbot.

        Args:
            query (str): User query.
        """
        logger.info(f"Processing streaming query: {query[:50]}...")
        try:
            self.chatbot.stream_ask(query, messages=self.messages)
            logger.info("Streaming response completed.")
        except Exception as e:
            logger.error(f"Error during stream_ask: {e}")
            raise

    def clear_history(self) -> None:
        """Clear the conversation history."""
        logger.info("Clearing conversation history.")
        self.messages = []

    def get_messages(self) -> List:
        """
        Get the current message history.

        Returns:
            List: Current messages.
        """
        return self.messages

    def set_messages(self, messages: List) -> None:
        """
        Set the message history.

        Args:
            messages (List): New message history.
        """
        logger.info(f"Setting messages with {len(messages)} items.")
        self.messages = messages
