from typing import Annotated, Any

from langchain_core.messages import BaseMessage
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
    response: BaseMessage


class Agent:

    def __init__(
            self,
            system_text: str = "You are a helpful agent that can use tools to answer user queries.",
            chat_history_limit: int = 8,
            tools: list =None,
            show_graph: bool = True
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
        try:
            self.system_text += f"\n **AVAILABLE Tools**: {[t.name for t in tools]}"
        except:
            pass
        self.agent = create_react_agent(
            model=self.groq.llm,
            tools=tools
        )
        self.limit = chat_history_limit
        self.workflow = self.create_workflow(show_graph=show_graph)
        logger.info("Agent created")

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

    def _assist(self, state: State, context: dict = None):
        """
        Process user messages
        :param state: workflow state
        :param context: static context to be passed
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
                context=context
            )
            messages.append({"role": "assistant", "content": response['messages'][-1].content})
            full_history.extend(response['messages'])
            return {
                "output": response['messages'][-1].content,
                "messages": messages,
                "full_history": full_history,
                "response": response
            }
        except Exception as e:
            logger.error(f"Error at agent responding: {e}")

    def create_workflow(self, show_graph: bool = True) -> CompiledStateGraph[Any, Any, Any, Any]:
        """
        Create simple chatbot workflow
        """
        graph_builder = StateGraph(State)
        # Nodes
        graph_builder.add_node(self._assist)
        # Workflow
        graph_builder.add_edge(START, "_assist")
        graph_builder.add_edge("_assist", END)
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
    # Example improved system prompt for your Agent
    system_text = (
        "You are a helpful AI assistant. "
        "You can answer questions directly, or use tools when needed. "
        "Only use a tool if the user asks for something that requires it"
        "If you use a tool, explain what you are doing and present the result clearly. "
    )
    agent = Agent(
        system_text=system_text,
        tools=[tool],
        show_graph=True
    )
    response, messages = agent.ask("What can you do for me?", messages=messages)
    print(response)

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
