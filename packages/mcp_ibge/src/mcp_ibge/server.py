"""Servidor MCP `mcp-ibge`.

Wireup: cria a instância `FastMCP`, registra as tools de cada domínio
(`tools.localidades_tools`, `tools.agregados_tools`, ...), o resource de
status (`ibge://status`) e o prompt `comparar_municipios`.

Execução:
    python -m mcp_ibge.server

Por padrão usa o transporte stdio (recomendado para Claude Desktop, Cursor e
demais clientes MCP locais). O transporte pode ser trocado via a variável de
ambiente `MCP_IBGE_TRANSPORT` (ex.: "streamable-http"); a porta usada nesse
modo é configurável via `MCP_IBGE_PORT`.

Importante: nunca usar `print()`. Em modo stdio, stdout é reservado para o
protocolo MCP — todo log vai para stderr via `logging`.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from importlib.metadata import version
from typing import Annotated, Any, Literal, cast

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .config import get_settings
from .logging_config import configure_logging
from .tools import agregados_tools, localidades_tools, sidra_tools

_settings = get_settings()

mcp = FastMCP(
    "mcp-ibge",
    instructions=(
        "Servidor MCP para consultar dados públicos e oficiais do IBGE: "
        "localidades (regiões, estados, municípios e seus códigos), agregados "
        "estatísticos do SIDRA (com metadados de variáveis e períodos) e "
        "indicadores de população. Toda resposta inclui metadados de fonte "
        "(source_name, source_url, retrieved_at, endpoint, params) para "
        "rastreabilidade."
    ),
    port=_settings.port,
)

localidades_tools.register_localidades_tools(mcp)
agregados_tools.register_agregados_tools(mcp)
sidra_tools.register_sidra_tools(mcp)


@mcp.resource("ibge://status")
async def status() -> dict[str, Any]:
    """Status do servidor: versão, tools disponíveis e horário atual."""
    tools = await mcp.list_tools()
    return {
        "status": "ok",
        "server": "mcp-ibge",
        "version": version("mcp-ibge"),
        "tools": sorted(tool.name for tool in tools),
        "timestamp": datetime.now(UTC).isoformat(),
    }


@mcp.prompt()
def comparar_municipios(
    municipios: Annotated[
        str,
        Field(
            description=(
                "Municípios a comparar, com a UF de cada um, ex.: "
                '"São Paulo/SP, Rio de Janeiro/RJ, Florianópolis/SC".'
            )
        ),
    ],
    indicador: Annotated[
        str,
        Field(description='Indicador a comparar (ex.: "população", "área territorial").'),
    ] = "população",
) -> str:
    """Orienta a comparação de municípios usando as tools de dados do IBGE."""
    return (
        f'Compare o indicador "{indicador}" entre os seguintes municípios: '
        f"{municipios}.\n\n"
        "Siga estes passos:\n"
        "1. Para cada município, use `obter_codigo_municipio` (nome + UF) "
        "para obter o código IBGE; se o nome for ambíguo, refine com a UF "
        "ou peça esclarecimento ao usuário.\n"
        "2. Use `listar_agregados`, `obter_metadados_agregado` e "
        "`listar_variaveis_agregado` para localizar o agregado e a variável "
        "do SIDRA correspondentes ao indicador (para população, prefira "
        "`consultar_populacao_municipio`).\n"
        "3. Consulte os dados com `consultar_agregado` (ou "
        "`consultar_populacao_municipio`), usando o mesmo período para "
        "todos os municípios sempre que possível.\n"
        "4. Ao apresentar os resultados, sempre cite:\n"
        "   - a fonte (`metadata.source_name` e `metadata.source_url`);\n"
        "   - o ano/período de referência (`periodo` ou "
        "`metadata.params.periodos`);\n"
        "   - a unidade territorial (`localidade_nome`/nível territorial) e "
        "a unidade de medida (`unidade`);\n"
        "   - limitações: dados ausentes/sigilosos (`valor: null`), "
        "estimativas vs. censo, `warnings` retornados pelas tools, e "
        "diferenças de período entre os municípios comparados.\n"
        "5. Não invente valores: se uma tool retornar erro ou dado ausente, "
        "informe isso explicitamente em vez de estimar."
    )


def main() -> None:
    """Configura logging e inicia o servidor MCP."""
    configure_logging()
    logging.getLogger(__name__).info("Iniciando mcp-ibge (transporte=%s)", _settings.transport)
    transport = cast("Literal['stdio', 'sse', 'streamable-http']", _settings.transport)
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
