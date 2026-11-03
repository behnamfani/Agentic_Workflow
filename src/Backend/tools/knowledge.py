from typing import Tuple, Type

from langchain_community.tools.semanticscholar import SemanticScholarQueryRun
from langchain_community.tools.semanticscholar.tool import SemanticScholarQueryRun
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import StructuredTool


wikipedia = None


def wikipedia_search(query: str) -> str:
    """Search Wikipedia for the given query and return a summary of the results."""
    global wikipedia
    if wikipedia is None:
        wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    return wikipedia.run(query)


def get_tools() -> tuple[SemanticScholarQueryRun, StructuredTool]:
    return SemanticScholarQueryRun(), StructuredTool.from_function(wikipedia_search)