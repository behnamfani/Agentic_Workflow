"""
Shared tool registry: reused across personas.
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import Iterable


current_file_path = os.path.abspath(__file__)
current_directory_path = os.path.dirname(current_file_path)
backend_directory_path = os.path.dirname(current_directory_path)
src_directory_path = os.path.dirname(backend_directory_path)
for _p in (current_directory_path, src_directory_path, src_directory_path):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from src.backend.config import settings
from src.backend.tools import knowledge


_AVAILABLE_TOOLS: dict[str, dict] = {
    "knowledge_tools": {
        "get_tool": knowledge.get_tools
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


def get_tools(tool_names: Iterable[str]) -> list:
    """
    Get LangChain tools, starting and caching each one only once
    :param tool_names: names of tools to fetch
    :return: list of LangChain tools
    """
    missing = sorted({name for name in tool_names if name not in _tools_cache})
    for name in missing:
        tool_def = _AVAILABLE_TOOLS.get(name)
        if tool_def:
            _tools_cache[name] = run_async(tool_def["get_tool"]())

    result = []
    seen = set()
    for name in tool_names:
        for tool in _tools_cache.get(name, []):
            if tool.name not in seen:
                seen.add(tool.name)
                result.append(tool)
    return result
