"""Script de apoio para o GIF de demonstração do README.

Conecta ao `mcp-ibge` local via stdio, chama `comparar_municipios` para Rio
de Janeiro, Niterói e Maricá (RJ) e imprime o resultado formatado, como um
agente faria ao responder ao prompt do "30-second demo".

Também é importado por `generate_demo_gif.py` para obter dados reais e
atualizados da API do IBGE no momento em que o GIF é gerado.

Uso:
    uv run python scripts/demo_compare_municipios.py
"""

from __future__ import annotations

import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(command="uv", args=["run", "mcp-ibge"])

MUNICIPIOS = [
    {"nome": "Rio de Janeiro", "uf": "RJ"},
    {"nome": "Niterói", "uf": "RJ"},
    {"nome": "Maricá", "uf": "RJ"},
]


async def comparar_municipios_rj() -> dict:
    """Chama `comparar_municipios` no servidor mcp-ibge local e retorna o envelope."""
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "comparar_municipios", {"municipios": MUNICIPIOS}
            )
            text = "".join(part.text for part in result.content if hasattr(part, "text"))
            return json.loads(text)


def format_table(envelope: dict) -> list[str]:
    """Formata o envelope de `comparar_municipios` como linhas de tabela."""
    lines = ["comparar_municipios(municipios=[Rio de Janeiro, Niterói, Maricá])", ""]
    lines.append(f"{'Município':<16} {'UF':<3} {'População estimada':>20}  Período")
    for municipio in envelope["data"]["municipios"]:
        pop = municipio["indicadores"][0]
        lines.append(
            f"{municipio['nome']:<16} "
            f"{municipio['uf_sigla']:<3} "
            f"{pop['valor']:>20,.0f}  {pop['periodo']}"
        )
    return lines


async def main() -> None:
    envelope = await comparar_municipios_rj()
    for line in format_table(envelope):
        print(line)


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    asyncio.run(main())
