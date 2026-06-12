"""Agente LlamaIndex (FunctionAgent) consultando dados oficiais do IBGE via mcp-ibge.

Requisitos (veja README.md):
- Ollama em execução localmente, com um modelo que suporte "tool calling"
  (ex.: `ollama pull llama3.1`).
- `uv` instalado, para que `uvx mcp-ibge` funcione.

Uso:
    python agent.py "Quais são as grandes regiões do Brasil segundo o IBGE?"
"""

from __future__ import annotations

import asyncio
import sys

from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.ollama import Ollama
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

OLLAMA_MODEL = "llama3.1"

DEFAULT_PROMPT = "Quais são as grandes regiões do Brasil segundo o IBGE?"

SYSTEM_PROMPT = (
    "Você é um assistente que responde perguntas sobre o Brasil usando "
    "exclusivamente as tools disponíveis (dados oficiais do IBGE). Nunca "
    "invente nomes, códigos ou valores."
)


async def run(question: str) -> str:
    # Para um checkout local do mcp-data-br, troque por:
    # BasicMCPClient(
    #     "uv",
    #     args=["--directory", "/caminho/absoluto/para/mcp-data-br", "run", "mcp-ibge"],
    # )
    mcp_client = BasicMCPClient("uvx", args=["mcp-ibge"])
    tool_spec = McpToolSpec(client=mcp_client)
    tools = await tool_spec.to_tool_list_async()

    llm = Ollama(model=OLLAMA_MODEL, request_timeout=120.0)
    agent = FunctionAgent(tools=tools, llm=llm, system_prompt=SYSTEM_PROMPT)

    response = await agent.run(question)
    return str(response)


def main() -> None:
    question = " ".join(sys.argv[1:]) or DEFAULT_PROMPT
    print(asyncio.run(run(question)))


if __name__ == "__main__":
    main()
