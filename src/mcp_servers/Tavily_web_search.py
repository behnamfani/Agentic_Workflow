import ast
import os

from fastmcp import FastMCP
from tavily import TavilyClient
from typing import Literal, Optional, Union

web_mcp = FastMCP("Tavily Web MCP")
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

@web_mcp.tool
def search(
    query: Optional[str] = None,
    country: str = "germany",
    max_results: int = 5,
    search_depth: Literal["basic", "advanced"] = "basic",
    topic: Literal["general", "news", "finance"] = "general",
    time_range: Optional[Literal["day", "week", "month", "year"]] = None,
    include_domains: Optional[list[str]] = None,
    **kwargs,
) -> str:
    """
    Search the internet with Tavily.
    Args:
        query (str): The query string to search the internet.
        country (str): Boost search results from this country. Should be the
            full country name in lowercase (e.g. "germany", "united states",
            "france"). Defaults to "germany".
        max_results (int): Maximum number of search results to return.
            Between 1 and 20. Defaults to 5.
        search_depth (str): "basic" for a fast search, "advanced" for a more
            thorough (and slower) search. Defaults to "basic".
        topic (str): The category of the search: "general", "news", or
            "finance". Defaults to "general".
        time_range (str, optional): Restrict results to a recent time
            window: "day", "week", "month", or "year". Omit for no limit.
        include_domains (list[str], optional): Restrict results to these domains.
            Omit or pass an empty list to search all domains.
    Returns:
        str: Search results from Tavily.
    """
    if not query or not isinstance(query, str):
        return (
            "Error: missing required argument 'query' (str). "
            "Call search again with a 'query' string, e.g. {'query': 'your search text'}."
        )
    try:
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
        search_kwargs = dict(
            auto_parameters=True,
            search_depth=search_depth,
            topic=topic,
            time_range=time_range,
            max_results=max_results,
            include_answer=True,
            country=country,
        )
        if include_domains:
            search_kwargs["include_domains"] = include_domains
        response = tavily_client.search(query, **search_kwargs)
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
def extract(
    urls: Optional[Union[str, list]] = None,
    extract_depth: Literal["basic", "advanced"] = "basic",
    format: Literal["markdown", "text"] = "markdown",
    **kwargs,
) -> str:
    """
    Extract the given URL with Tavily.
    Args:
        urls: The URL (str) or list of URLs to be extracted
        extract_depth (str): "basic" for a fast extraction, "advanced" for a
            more thorough (and slower) extraction, e.g. of tables or embedded
            content. Defaults to "basic".
        format (str): Output format of the extracted content: "markdown" or
            "text". Defaults to "markdown".
    Returns:
        str: Extraction results from Tavily.
    """
    if not urls:
        return (
            "Error: missing required argument 'urls' (str or list[str]). "
            "Call extract again with 'urls', e.g. {'urls': 'https://example.com'}."
        )
    try:
        urls = normalize_urls(urls)
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
        response = tavily_client.extract(
            urls,
            extract_depth=extract_depth,
            format=format,
            timeout=30
        )
        return str(response)
    except Exception as e:
        return f"Error happened during extract call: {e}. Check the error and try again."


if __name__ == "__main__":
    web_mcp.run(transport="stdio", show_banner=False)