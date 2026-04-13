from langchain_community.tools.semanticscholar.tool import SemanticScholarQueryRun
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import StructuredTool


wikipedia = None

def wikipedia_search(query: str) -> str:
    global wikipedia
    if wikipedia is None:
        wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    return wikipedia.run(query)

def get_knowledge_tools() -> list:
    tools = [SemanticScholarQueryRun(), WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())]
    return tools

def get_tools() -> tuple[StructuredTool, StructuredTool]:
    return SemanticScholarQueryRun, StructuredTool.from_function(wikipedia_search)