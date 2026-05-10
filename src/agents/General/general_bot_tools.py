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
tools = list(knowledge.get_tools())


mcp_config = {
    "time_mcp": {
        "transport": "stdio",
        "command": sys.executable,  # Use the current Python executable
        "args": [str(Path(src_directory_path) / "mcp_servers" / "time_mcp.py")],
    }
}

client = MultiServerMCPClient(mcp_config)
tools += asyncio.run(client.get_tools())