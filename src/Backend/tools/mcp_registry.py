"""
Shared MCP client/tool registry: one cached client per server, reused across personas.
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import Iterable

from langchain_mcp_adapters.client import MultiServerMCPClient

current_file_path = os.path.abspath(__file__)
current_directory_path = os.path.dirname(current_file_path)
src_directory_path = os.path.dirname(current_directory_path)
root_directory_path = os.path.dirname(src_directory_path)
for _p in (current_directory_path, src_directory_path, root_directory_path):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from src.Backend.config import settings

MCP_SERVERS_DIR = Path(src_directory_path) / "mcp_servers"

# Server definitions, one per capability, shared by all personas.
_SERVER_DEFS: dict[str, dict] = {
    "tavily_web_search": {
        "transport": "stdio",
        "command": sys.executable,
        "args": [str(MCP_SERVERS_DIR / "Tavily_web_search.py")],
        "env": {"TAVILY_API_KEY": settings.TAVILY_API_KEY or ""},
    },
    "time_mcp": {
        "transport": "stdio",
        "command": sys.executable,
        "args": [str(MCP_SERVERS_DIR / "time_mcp.py")],
    },
    "calculator_mcp": {
        "transport": "stdio",
        "command": sys.executable,
        "args": [str(MCP_SERVERS_DIR / "calculator_mcp.py")],
    },
    "weather_mcp": {
        "transport": "stdio",
        "command": sys.executable,
        "args": [str(MCP_SERVERS_DIR / "weather_mcp.py")],
    },
}

_tools_cache: dict[str, list] = {}


def run_async(coro):
    """
    Run an async coroutine from sync code, even if a loop is already running (e.g. Streamlit)
    :param coro: coroutine to run
    :return: the coroutine's result
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


def get_mcp_tools(server_names: Iterable[str]) -> list:
    """
    Get LangChain tools for the given MCP servers, starting and caching each server only once
    :param server_names: names of MCP servers to fetch tools from, e.g. ["tavily_web_search"]
    :return: list of LangChain tools from those servers
    """
    missing = sorted({name for name in server_names if name not in _tools_cache})
    for name in missing:
        client = MultiServerMCPClient({name: _SERVER_DEFS[name]})
        _tools_cache[name] = run_async(client.get_tools())

    result = []
    seen = set()
    for name in server_names:
        for tool in _tools_cache.get(name, []):
            if tool.name not in seen:
                seen.add(tool.name)
                result.append(tool)
    return result
