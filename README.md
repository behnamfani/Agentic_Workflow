# Agentic_Workflow
Agentic workflow examples and small tools built on Langgraph and related Python libraries.

## What this repo contains
- `src/agents/chatbot.py`: Chatbot implementation used in examples.
- `src/agents/agent.py`: Generic agent that can call tools (see `calculate_age` in the notebook).
- `notebooks/chatbot_agent_example.ipynb`: Guided examples showing `Chatbot` and `Agent` usage.

## Tech stack
- **Language:** Python 3.11+
- **Core libs:** `langgraph`, `langchain-core`, `groq`, `fastmcp`, `openai` and ecosystem packages listed in `requirements.txt`.

## Quickstart (Windows PowerShell)
```powershell
# create virtual env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# install dependencies
pip install -r requirements.txt
# run notebooks (launch Jupyter Lab/Notebook)
jupyter lab
```

## Examples
- Open `notebooks/chatbot_agent_example.ipynb` to see how the `Chatbot` and `Agent` are instantiated and used.
- See `src/agents` for implementation details and `src/mcp_servers` for example MCP servers used by agents.

## Next steps
- Run the notebook, modify the `system_text` or tools, and experiment with streaming vs synchronous calls.

Short, focused examples are in `notebooks/` and the core code is in `src/agents/`.

## Quick examples

- Chatbot (synchronous):

```python
from src.agents.chatbot import Chatbot

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
from src.agents.agent import Agent
import asyncio

def calculate_age(birth_date: str, target_date: str | None = None) -> str:
	# minimal shim; see `notebooks/chatbot_agent_example.ipynb` for full function
	return f"Age calculator received: {birth_date} -> {target_date or 'today'}"

agent = Agent(system_text="You are a helpful assistant that can use tools.", tools=[calculate_age], show_graph=False)

async def run():
	messages = []
	response, messages = await agent.stream_ask("My birthday is 1991-12-20. Tell me interesting insights", messages=messages, mode="updates")
	print(response)

asyncio.run(run())
```

See `notebooks/chatbot_agent_example.ipynb` for the full `calculate_age` implementation and more usage patterns.
