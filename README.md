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
