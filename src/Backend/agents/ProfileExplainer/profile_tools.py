import os
import sys

# Add the parent directory to sys.path so we can import our models
current_file_path = os.path.abspath(__file__)
current_directory_path = os.path.dirname(current_file_path)
parent_directory_path = os.path.dirname(current_directory_path)
root_directory_path = os.path.dirname(os.path.dirname(parent_directory_path))
sys.path.insert(0, current_directory_path)
sys.path.insert(0, parent_directory_path)
sys.path.insert(0, root_directory_path)


from src.Backend.tools import skill_utils
from src.Backend.tools.mcp_registry import get_mcp_tools

# ProfileExplainer stays grounded strictly in Behnam's CV/skill files, so it
# intentionally requests no MCP servers; listed for symmetry with the other
# personas and to make extending it later a one-line change.
REQUIRED_MCP_SERVERS: list = []

tools = list(skill_utils.get_tools()) + get_mcp_tools(REQUIRED_MCP_SERVERS)