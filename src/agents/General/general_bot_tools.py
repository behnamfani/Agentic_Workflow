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


from src.tools import knowledge
tools = list(knowledge.get_tools())

print(parent_directory_path)

mcp_config = {
    "time_mcp": {
        "name": "Time Tool",
        "description": "Use this for getting current time, timestamps, time conversions, and world clock information.",
        "transport": "stdio",
        "command": "python",
        "args": ["/path/to/math_server.py"],

    }
}