"""Agente local mínimo: Ollama + mcp-ibge via stdio, sem chave de API.

Requisitos (veja README.md):
- Ollama em execução localmente, com um modelo que suporte "tool calling"
  (ex.: `ollama pull llama3.1`).
- `uv` instalado, para que `uvx mcp-ibge` funcione.

Uso:
    python agent.py "Qual é o código IBGE do município de Niterói, no Rio de Janeiro?"
"""

from __future__ import annotations

import asyncio
import sys

import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool

OLLAMA_MODEL = "llama3.1"

DEFAULT_PROMPT = "Qual é o código IBGE do município de Niterói, no Rio de Janeiro?"

# Para um checkout local do mcp-data-br, troque por:
# StdioServerParameters(
#     command="uv",
#     args=["--directory", "/caminho/absoluto/para/mcp-data-br", "run", "mcp-ibge"],
# )
SERVER = StdioServerParameters(command="uvx", args=["mcp-ibge"])

SYSTEM_PROMPT = (
    "Você é um assistente que responde perguntas sobre municípios "
    "brasileiros usando exclusivamente as tools disponíveis (dados oficiais "
    "do IBGE). Nunca invente códigos, nomes ou valores."
)


def _mcp_tool_to_ollama(tool: Tool) -> dict:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema,
        },
    }


async def run(question: str) -> str:
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            ollama_tools = [_mcp_tool_to_ollama(tool) for tool in tools_result.tools]

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ]

            response = ollama.chat(model=OLLAMA_MODEL, messages=messages, tools=ollama_tools)
            message = response["message"]
            messages.append(message)

            for call in message.get("tool_calls") or []:
                name = call["function"]["name"]
                arguments = call["function"]["arguments"]
                result = await session.call_tool(name, arguments)
                content = "".join(
                    part.text for part in result.content if hasattr(part, "text")
                )
                messages.append({"role": "tool", "content": content})

            if message.get("tool_calls"):
                final = ollama.chat(model=OLLAMA_MODEL, messages=messages)
                return final["message"]["content"]

            return message["content"]


def main() -> None:
    question = " ".join(sys.argv[1:]) or DEFAULT_PROMPT
    print(asyncio.run(run(question)))


if __name__ == "__main__":
    main()
