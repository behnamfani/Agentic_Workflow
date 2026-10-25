<p align="center">
  <img src="pictures/catbot.png" alt="PaperSoccer Logo" width="220">
</p>

# Agentic_Workflow
"Catbot" — a Streamlit app with three chat personas (General, ProfileExplainer, BoardGenie), built on LangGraph/LangChain, Groq-hosted LLMs, and FastMCP tool servers.

## What this repo contains
- `src/UI/streamlit_ui.py`: the Streamlit app — bot selection screen, per-bot config, and chat.
- `src/agents/General/`, `src/agents/ProfileExplainer/`, `src/agents/BoardGenie/`: one system-prompt module + one tools module per persona.
- `src/agents_utils/chatbot.py`, `src/agents_utils/agent.py`: the two backends (`Chatbot` for tool-less personas, `Agent`/ReAct for personas with tools) wrapped by `src/app.py`'s `App`.
- `src/tools/mcp_registry.py`: shared, cached MCP (FastMCP stdio) server registry used by all three personas so a server like Tavily only ever spins up once.
- `src/mcp_servers/`: the FastMCP servers themselves (Tavily web search, time, calculator, weather).
- `src/llm_chats/Chatgroq.py`: Groq LLM wrapper with primary/backup model fallback, used by every agent/chatbot.
- `notebooks/chatbot_agent_example.ipynb`: standalone guided examples showing `Chatbot` and `Agent` usage outside the Streamlit app.

See [CLAUDE.md](CLAUDE.md) for the full architecture write-up.

## Tech stack
- **Language:** Python 3.11+
- **Core libs:** `langgraph`, `langchain`/`langchain-core`, `langchain-groq`, `langchain-mcp-adapters`, `fastmcp`, `streamlit`, `tavily-python` and ecosystem packages listed in `requirements.txt`.

## Quickstart (Windows PowerShell)
```powershell
# create virtual env
python -m venv venv
.\venv\Scripts\Activate.ps1
# install dependencies
pip install -r requirements.txt
# set GROQ_API_KEY, TAVILY_API_KEY, etc. in a .env file at the repo root
# run the app (Streamlit UI on port 8505)
python start.py
```

## Examples
- Run `python start.py` to use the three personas through the Streamlit UI.
- Open `notebooks/chatbot_agent_example.ipynb` to see `Chatbot`/`Agent` used standalone, outside the app.
- See `src/agents/` for each persona's prompt + tools, and `src/mcp_servers/` for the MCP servers they share via `src/tools/mcp_registry.py`.

## Next steps
See `ideas.txt` for planned work, including splitting BoardGenie into a multi-agent LangGraph (recommend / play / teach personas under one supervisor).

## Quick examples

- Chatbot (synchronous):

```python
from src.agents_utils.chatbot import Chatbot

bot = Chatbot(system_text="You are a helpful assistant that tells everything in jokes.", show_graph=False)
messages = []
response, messages = bot.ask(query="Tell me about LOTR", messages=messages)
print(response)
```

- Chatbot (streaming):

```python
# uses the same `bot` and `messages` as above
bot.stream_ask(query="Great, thanks", messages=messages)
```

- Agent with a simple tool (async):

```python
from src.agents_utils.agent import Agent
import asyncio


def calculate_age(birth_date: str, target_date: str | None = None) -> str:
    # minimal shim; see `notebooks/chatbot_agent_example.ipynb` for full function
    return f"Age calculator received: {birth_date} -> {target_date or 'today'}"


agent = Agent(system_text="You are a helpful assistant that can use tools.", tools=[calculate_age], show_graph=False)


async def run():
    messages = []
    response, messages = await agent.stream_ask("My birthday is 1991-12-20. Tell me interesting insights",
                                                messages=messages, mode="updates")
    print(response)


asyncio.run(run())
```

See `notebooks/chatbot_agent_example.ipynb` for the full `calculate_age` implementation and more usage patterns.
