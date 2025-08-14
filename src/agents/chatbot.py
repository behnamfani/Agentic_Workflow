from typing import Annotated, Any

from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from PIL import Image
import io

from src.llm_models import ChatGroq


class State(TypedDict):
    input: str
    messages: list
    output: str


class Chatbot:

    def __init__(
            self,
            system_text: str = "You are a helpful assistant.",
            chat_history_limit: int = 3
    ):
        self.llm = ChatGroq.Groq(system_text=system_text)
        self.limit = chat_history_limit
        self.workflow = self.create_workflow()

    def ask(self, state: State):
        """
        Process user messages
        :param state: workflow state
        :return: updated state's output and messages
        """
        messages = state.get("messages", [])
        query = state.get("input", "")
        if len(messages) > 0:
            prompt = (f"Chat History: ### {messages[-self.limit:]}  ### "
                      f"\n\n"
                      f"User Query: ### {query} ###")
        else:
            prompt = query
        response = self.llm.ask(prompt)
        messages.extend([{"role": "user", "content": query}, {"role": "assistant", "content": response}])
        return {
            "output": response,
            "messages": messages
        }

    def create_workflow(self, show_graph: bool = True) -> CompiledStateGraph[Any, Any, Any, Any]:
        """
        Create simple chatbot workflow
        """
        graph_builder = StateGraph(State)
        # Nodes
        graph_builder.add_node("chatbot", self.ask)
        # Workflow
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", END)
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
    bot = Chatbot(system_text="You are a math teacher and a helpful assistant.")

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