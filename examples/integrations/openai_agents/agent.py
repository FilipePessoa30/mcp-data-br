"""Script simples: OpenAI Agents SDK + mcp-ibge gerando um perfil municipal.

Por padrão usa um modelo local via Ollama, através do endpoint
OpenAI-compatible que o Ollama expõe em http://localhost:11434/v1 — não é
necessária nenhuma chave de API real (veja README.md para usar a OpenAI de
fato).

Requisitos:
- Ollama em execução localmente, com um modelo que suporte "tool calling"
  (ex.: `ollama pull llama3.1`).
- `uv` instalado, para que `uvx mcp-ibge` funcione.

Uso:
    python agent.py "Gere um perfil básico do município de Maricá, RJ."
"""

from __future__ import annotations

import asyncio
import os
import sys

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from agents.mcp import MCPServerStdio
from openai import AsyncOpenAI

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")

DEFAULT_PROMPT = "Gere um perfil básico do município de Maricá, RJ."

SYSTEM_PROMPT = (
    "Você é um assistente que responde perguntas sobre municípios "
    "brasileiros usando exclusivamente as tools disponíveis (dados oficiais "
    "do IBGE). Nunca invente códigos, nomes ou valores."
)

# Evita que o SDK tente enviar traços para a plataforma da OpenAI, o que
# exigiria OPENAI_API_KEY mesmo usando um modelo local.
set_tracing_disabled(True)


async def run(question: str) -> str:
    client = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    model = OpenAIChatCompletionsModel(model=OLLAMA_MODEL, openai_client=client)

    # Para um checkout local do mcp-data-br, troque `params` por:
    # {
    #     "command": "uv",
    #     "args": ["--directory", "/caminho/absoluto/para/mcp-data-br", "run", "mcp-ibge"],
    # }
    async with MCPServerStdio(
        params={"command": "uvx", "args": ["mcp-ibge"]},
        name="mcp-ibge",
    ) as ibge_server:
        agent = Agent(
            name="Assistente IBGE",
            instructions=SYSTEM_PROMPT,
            model=model,
            mcp_servers=[ibge_server],
        )
        result = await Runner.run(agent, question)
        return result.final_output


def main() -> None:
    question = " ".join(sys.argv[1:]) or DEFAULT_PROMPT
    print(asyncio.run(run(question)))


if __name__ == "__main__":
    main()
