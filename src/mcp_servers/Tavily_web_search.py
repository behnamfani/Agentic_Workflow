import ast
from fastmcp import FastMCP
from tavily import TavilyClient
from typing import Union

from src.config import settings

web_mcp = FastMCP("Tavily Web MCP")


@web_mcp.tool
def search(text: str) -> str:
    """
    Search the internet with Tavily.
    Args:
        text (str): The query string to search the internet.
    Returns:
        str: Search results from Tavily.
    """
    try:
        tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        response = tavily_client.search(
            text,
            auto_parameters=True,
            search_depth='basic',
            max_results=5,
            include_answer=True,
            country="germany",
            include_domains=["*.com", "*.de"]
            # start_date=
        )
        return str(response)
    except Exception as e:
        return f"Error happened during search call: {e}. Check the error and try again."


def normalize_urls(urls: Union[str, list]) -> list:
    """
    Normalize input into a list of URLs.
    Handles:
        - A single URL string
        - A list of URLs
        - A string representation of a list of URLs
    """
    if isinstance(urls, list):
        return urls

    if isinstance(urls, str):
        # Try to interpret it as a Python literal (e.g. "[...]" → list)
        stripped = urls.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            try:
                parsed = ast.literal_eval(stripped)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
        # Otherwise, treat as single URL string
        return [urls]
    raise TypeError(f"Unsupported type for urls: {type(urls)}")


@web_mcp.tool
def extract(urls: Union[str, list]) -> str:
    """
    Extract the given URL with Tavily.
    Args:
        urls: The URL (str) or list of URLs to be extracted
    Returns:
        str: Extraction results from Tavily.
    """
    try:
        urls = normalize_urls(urls)
        tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        response = tavily_client.extract(
            urls,
            search_depth='basic',
            max_results=5,
            format='markdown',
            timeout=30
        )
        return str(response)
    except Exception as e:
        return f"Error happened during extract call: {e}. Check the error and try again."


if __name__ == "__main__":
    web_mcp.run(transport="stdio")