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


from src.backend.tools.mcp_registry import get_mcp_tools
from src.backend.tools.tool_registry import get_tools


REQUIRED_MCP_SERVERS = ["time_mcp", "calculator_mcp", "weather_mcp", "tavily_web_search"]
REQUIRED_TOOLS = ["knowledge_tools"]

tools = get_tools(REQUIRED_TOOLS) + get_mcp_tools(REQUIRED_MCP_SERVERS)
