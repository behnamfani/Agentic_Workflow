from langchain_mcp_adapters.client import MultiServerMCPClient
from pathlib import Path
import os
import sys
import asyncio


current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)

# Append the current and parent directories to the system path
sys.path.append(current_dir)
sys.path.append(parent_dir)

from src.agents.agent import Agent


mcp_folder_path = Path(parent_dir) / "src" / "mcp_servers"
weather_mcp_path = mcp_folder_path / "weather_mcp.py"
calculator_mcp_path = mcp_folder_path / "calculator_mcp.py"
client = MultiServerMCPClient(  
    {
        "weather_mcp": {
            "transport": "stdio",
            "command": "python",
            "args": [str(weather_mcp_path)],
        },
        "calculator": {
            "transport": "stdio",
            "command": "python",
            "args": [str(calculator_mcp_path)],
        },
    }
)


tools = asyncio.run(client.get_tools())
print(f"Loaded tools: {[tool.name for tool in tools]}")

agent = Agent(
    system_text="You are a helpful assistant. that can use tools to answer questions.",
    tools=tools,
    show_graph=False
)
response, messages = asyncio.run(agent.stream_ask("What are the tools you have access to?", messages=[]))
print(f"\n=======================\n")
response, messages = asyncio.run(agent.stream_ask("What mathematical functions you can calculate", messages=messages))
print(f"\n=======================\n")
response, messages = asyncio.run(agent.stream_ask("Compute the cosh of 10", messages=messages))
print(f"\n=======================\n")