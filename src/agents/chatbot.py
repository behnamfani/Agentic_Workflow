from typing import Annotated
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


llm = ChatGroq.Groq(system_text="You are a math teacher and a helpful assistant.")


def chatbot(state: State):
    messages = state.get("messages", [])
    query = state.get("input", "")
    if len(messages) > 0:
        prompt = (f"Chat History: ### {messages[-3:]}  ### "
                  f"\n\n"
                  f"User Query: ### {query} ###")
    else:
        prompt = query
    response = llm.ask(prompt)
    messages.extend([{"role": "user", "content": query}, {"role": "assistant", "content": response}])
    return {
        "output": response,
        "messages": messages
    }


graph_builder = StateGraph(State)
# Nodes
graph_builder.add_node("chatbot", chatbot)
# Workflow
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()
# Check the workflow
png_bytes = graph.get_graph().draw_mermaid_png()
image = Image.open(io.BytesIO(png_bytes))
image.show()
# print(graph.invoke({'input': "Hi", 'messages': []}))

# Testing
messages = []


def stream_graph_updates(user_input: str):
    global messages
    print(messages)
    for event in graph.stream({"input": user_input, "messages": messages}):
        for value in event.values():
            print("Assistant:", value["output"])


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