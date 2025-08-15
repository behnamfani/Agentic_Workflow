from typing import Annotated, Any

from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from PIL import Image
import io

from src.llm_models import ChatGroq
from src.config import logger


class State(TypedDict):
    input: str
    messages: list
    output: str
    full_history: list


class Agent:

    def __init__(
            self,
            system_text: str = "You are a helpful agent that can use tools to answer user queries.",
            chat_history_limit: int = 3,
            tools=None
    ):
        if tools is None:
            tools = []
        try:
            system_text = (f"{system_text} \n"
                           f"AVAILABLE Tools: {[t.name for t in tools]}") if len(tools) > 0 else system_text
        except:
            pass

        self.groq = ChatGroq.Groq()
        self.system_text = system_text
        self.agent = create_react_agent(
            model=self.groq.llm,
            tools=tools
        )
        self.limit = chat_history_limit
        self.workflow = self.create_workflow()
        logger.info("Agent created")

    def ask(self, state: State):
        """
        Process user messages
        :param state: workflow state
        :return: updated state's output and messages
        """
        try:
            messages = state.get("messages", [])
            full_history = state.get("full_history", [])
            query = state.get("input", "")
            messages.append({"role": "user", "content": query})
            response = self.agent.invoke(
                {"messages":
                     [{"role": "system", "content": self.system_text}] + messages[-self.limit:]
                 },
                context={"user": "Behnam"}
            )
            messages.append({"role": "assistant", "content": response['messages'][-1].content})
            full_history.extend(response['messages'])
            return {
                "output": response['messages'][-1].content,
                "messages": messages,
                "full_history": full_history
            }
        except Exception as e:
            logger.error(f"Error at agent responding: {e}")

    def create_workflow(self, show_graph: bool = True) -> CompiledStateGraph[Any, Any, Any, Any]:
        """
        Create simple chatbot workflow
        """
        graph_builder = StateGraph(State)
        # Nodes
        graph_builder.add_node("agent", self.ask)
        # Workflow
        graph_builder.add_edge(START, "agent")
        graph_builder.add_edge("agent", END)
        graph = graph_builder.compile()
        if show_graph:
            # display the workflow
            png_bytes = graph.get_graph().draw_mermaid_png()
            image = Image.open(io.BytesIO(png_bytes))
            image.show()
            # print(graph.invoke({'input': "Hi", 'messages': []}))

        return graph


if __name__ == "__main__":
    # Testing chatbot workflow
    messages = []
    from src.tools import PDF_Reader
    tool = PDF_Reader.get_tool()
    agent = Agent(
        system_text="You are a helpful assistant. that can use tools to answer questions.",
        tools=[tool]
    )

    def stream_graph_updates(user_input: str):
        global messages
        print(messages)
        for event in agent.workflow.stream({"input": user_input, "messages": messages}):
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
