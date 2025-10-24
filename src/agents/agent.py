from typing import Annotated, Any, Literal
import asyncio
from langchain_core.messages import BaseMessage
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from PIL import Image
import io

from src.llm_models import ChatGroq
from src.config import logger


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

        self.limit = chat_history_limit
        self.agent = self.create_workflow(tools=tools, show_graph=show_graph)
        logger.info("Agent created")

    async def ask(self, query: str, messages: list = None) -> tuple[BaseMessage, list | None]:
        """
        Process user messages
        :param query: user query
        :param messages: chat history or conversation [{"role": "system", "content": ...}, ...]
        :return: updated state's output and messages
        """
        messages = [] if not messages else messages
        messages.append({"role": "user", "content": query})
        response = await self.agent.ainvoke(
            {"messages":
                 [{"role": "system", "content": self.system_text}] + messages[-self.limit:]
             },
        )
        return response['messages'][-1].content, messages

    def stream_ask(
            self, query: str, messages: list = None,
            mode: Literal["values", "updates", "messages", "custom"] = "updates"
    ):
        """
        Process user messages
        :param query: user query
        :param messages: chat history or conversation
        :param mode: mode of streaming Literal["values", "updates", "messages", "custom"]
        :return: updated state's output and messages
        """
        messages = [] if not messages else messages
        for message_chunk in self.agent.stream(
                {
                    "input": query,
                    "messages": messages
                },
                stream_mode=mode,
        ):
            print(message_chunk)
            for key in message_chunk:
                if 'output' in message_chunk[key]:
                    print(f"{key}: {message_chunk[key]['output']}", flush=True)
                elif 'messages' in message_chunk[key]:
                    role = message_chunk[key]['messages'][-1]['role']
                    content = message_chunk[key]['messages'][-1]['content']
                    print(f"{role}: {content}", flush=True)
            # yield message_chunk.content

    def create_workflow(self, tools: list, show_graph: bool = True) -> CompiledStateGraph[Any, Any, Any, Any]:
        """
        Create react agent workflow
        """
        try:
            self.system_text += f"\n **AVAILABLE Tools**: {[t.name for t in tools]}"
        except:
            pass
        agent = create_react_agent(
            model=self.groq.llm,
            tools=tools
        )
        if show_graph:
            # display the workflow
            png_bytes = agent.get_graph().draw_mermaid_png()
            image = Image.open(io.BytesIO(png_bytes))
            image.show()

        return agent


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
    response, messages = asyncio.run(agent.ask("What can you do for me?", messages=messages))
    print(response)
    exit()
    # TODO to check streaming
    agent.stream_ask("What can you do for me?", messages=messages)
    exit()
    print(response)

    def stream_graph_updates(user_input: str):
        global messages
        print(messages)
        for event in agent.agent.stream({"input": user_input, "messages": messages}):
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
