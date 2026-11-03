import os
import sys

# Add the parent directory to sys.path so we can import our models
current_file_path = os.path.abspath(__file__)
current_directory_path = os.path.dirname(current_file_path)
parent_directory_path = os.path.dirname(current_directory_path)
src_directory_path = os.path.dirname(parent_directory_path)
sys.path.insert(0, current_directory_path)
sys.path.insert(0, parent_directory_path)
sys.path.insert(0, src_directory_path)


from src.backend.tools import knowledge
from src.backend.tools.mcp_registry import get_mcp_tools

REQUIRED_MCP_SERVERS = ["tavily_web_search"]

scholar_tool, wiki_tool = knowledge.get_tools()
tools = get_mcp_tools(REQUIRED_MCP_SERVERS) + [wiki_tool]
