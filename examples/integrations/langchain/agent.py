"""Agente LangGraph (ReAct) usando as tools do mcp-ibge via MCP, com LLM local.

Requisitos (veja README.md):
- Ollama em execução localmente, com um modelo que suporte "tool calling"
  (ex.: `ollama pull llama3.1`).
- `uv` instalado, para que `uvx mcp-ibge` funcione.

Uso:
    python agent.py "Compare a população estimada de Niterói e Maricá (RJ)."
"""

from __future__ import annotations

import asyncio
import sys

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

OLLAMA_MODEL = "llama3.1"

DEFAULT_PROMPT = "Compare a população estimada de Niterói e Maricá (RJ)."

# Para um checkout local do mcp-data-br, troque por:
# "ibge": {
#     "command": "uv",
#     "args": ["--directory", "/caminho/absoluto/para/mcp-data-br", "run", "mcp-ibge"],
#     "transport": "stdio",
# }
MCP_SERVERS = {
    "ibge": {
        "command": "uvx",
        "args": ["mcp-ibge"],
        "transport": "stdio",
    }
}

SYSTEM_PROMPT = (
    "Você é um assistente que responde perguntas sobre municípios "
    "brasileiros usando exclusivamente as tools disponíveis (dados oficiais "
    "do IBGE). Nunca invente códigos, nomes ou valores."
)


async def run(question: str) -> str:
    client = MultiServerMCPClient(MCP_SERVERS)
    tools = await client.get_tools()

    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0)
    agent = create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)

    result = await agent.ainvoke({"messages": [("user", question)]})
    return result["messages"][-1].content


def main() -> None:
    question = " ".join(sys.argv[1:]) or DEFAULT_PROMPT
    print(asyncio.run(run(question)))


if __name__ == "__main__":
    main()
