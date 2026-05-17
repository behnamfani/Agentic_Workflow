import os
import sys
import asyncio
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient

# Add the parent directory to sys.path so we can import our models
current_file_path = os.path.abspath(__file__)
current_directory_path = os.path.dirname(current_file_path)
parent_directory_path = os.path.dirname(current_directory_path)
src_directory_path = os.path.dirname(parent_directory_path)
sys.path.insert(0, current_directory_path)
sys.path.insert(0, parent_directory_path)
sys.path.insert(0, src_directory_path)


from src.tools import knowledge
from src.config import settings
wiki_tool = list(knowledge.get_tools())[0]


mcp_config = {
    "tavily_web_search": {
        "transport": "stdio",
        "command": sys.executable,  # Use the current Python executable
        "args": [str(Path(src_directory_path) / "mcp_servers" / "Tavily_web_search.py")],
        "env": {
            "TAVILY_API_KEY": settings.TAVILY_API_KEY
        },
    },
}

client = MultiServerMCPClient(mcp_config)
tools = asyncio.run(client.get_tools()) + [wiki_tool]