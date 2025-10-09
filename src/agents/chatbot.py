from typing import Annotated, Any, Union

from langchain_core.messages import BaseMessage
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables.graph import MermaidDrawMethod
from PIL import Image
import io

from src.llm_models import ChatGroq


class State(TypedDict):
    input: str
    messages: list
    output: str
    response: BaseMessage


class Chatbot:

    def __init__(
            self,
            system_text: str = "You are a helpful assistant.",
            chat_history_limit: int = 8,
            show_graph: bool = True
    ):
        self.llm = ChatGroq.Groq(system_text=system_text)
        self.limit = chat_history_limit
        self.workflow = self.create_workflow(show_graph=show_graph)

    def ask(self, query: str, messages: list = None) -> tuple[BaseMessage, list | None]:
        """
        Process user messages
        :param query: user query
        :param messages: chat history or conversation
        :return: updated state's output and messages
        """
        messages = [] if not messages else messages
        state = self.workflow.invoke({
            "input": query,
            "messages": messages
        })
        return state['output'], state['messages']

    def stream_ask(self, query: str, messages: list = None):
        """
        Process user messages
        :param query: user query
        :param messages: chat history or conversation
        :return: updated state's output and messages
        """
        messages = [] if not messages else messages
        for message_chunk, metadata in self.workflow.stream(
                {
                    "input": query,
                    "messages": messages
                },
                stream_mode="messages",
        ):
            if message_chunk.content:
                print(message_chunk.content, flush=True)
                # yield message_chunk.content

    def _chat(self, state: State):
        """
        Process user messages
        :param state: workflow state
        :return: updated state's output and messages
        """
        messages = state.get("messages", [])
        query = state.get("input", "")
        messages.append({"role": "user", "content": query})
        response = self.llm.ask(messages[-self.limit:])
        messages.extend([{"role": "assistant", "content": response.content}])
        return {
            "output": response.content,
            "messages": messages,
            "response": response
        }

    def create_workflow(self, show_graph: bool = True) -> CompiledStateGraph[Any, Any, Any, Any]:
        """
        Create simple chatbot workflow
        """
        graph_builder = StateGraph(State)
        # Nodes
        graph_builder.add_node(self._chat)
        # Workflow
        graph_builder.add_edge(START, "_chat")
        graph_builder.add_edge("_chat", END)
        graph = graph_builder.compile()
        if show_graph:
            # display the workflow
            png_bytes = graph.get_graph().draw_mermaid_png()
            image = Image.open(io.BytesIO(png_bytes))
            image.show()

        return graph


if __name__ == "__main__":
    # Testing chatbot workflow
    messages = []
    bot = Chatbot(system_text="You are a math teacher and a helpful assistant.", show_graph=True)
    response, messages = bot.ask("Tell me a famous math problem", messages=messages)
    print(response)

    def stream_graph_updates(user_input: str):
        global messages
        print(messages)
        for event in bot.workflow.stream({"input": user_input, "messages": messages}):
            for value in event.values():
                print("Assistant:", value["output"])
                messages = value["messages"]
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            stream_graph_updates(user_input)
        except:
            # fallback if input() is not available
            user_input = "What do you know about LangGraph?"
            print("User: " + user_input)
            stream_graph_updates(user_input)
            break