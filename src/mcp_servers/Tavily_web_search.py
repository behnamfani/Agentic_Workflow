from fastmcp import FastMCP
from tavily import TavilyClient

from src.config import settings

web_mcp = FastMCP("Tavily Web MCP")


# @web_mcp.tool
def search(text: str):
    """
    Search internet with the given text
    :param text: string text query to search the internet. Send the input as {'text': 'text_value'}
    :return: results of the internet search
    """
    try:
        tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        response = tavily_client.search(text)
        return response
    except Exception as e:
        return (f"Error happened during search call: {e}"
                f"If possible, try again.")


if __name__ == "__main__":
    web_mcp.run(transport="stdio")