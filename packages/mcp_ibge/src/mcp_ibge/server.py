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
from .tools import (
    agregados_tools,
    comparacao_tools,
    geo_tools,
    localidades_tools,
    perfil_tools,
    sidra_tools,
)

_settings = get_settings()

mcp = FastMCP(
    "mcp-ibge",
    instructions=(
        "Servidor MCP para consultar dados públicos e oficiais do IBGE: "
        "localidades (regiões, estados, municípios e seus códigos), agregados "
        "estatísticos do SIDRA (com metadados de variáveis e períodos), "
        "indicadores de população, perfis básicos de municípios "
        "(`gerar_perfil_municipal`) e malhas geográficas em GeoJSON "
        "(`obter_malha_municipio`, `obter_malha_uf`, `obter_bbox_municipio`, "
        "`gerar_geojson_municipios`). Toda resposta inclui metadados de fonte "
        "(source_name, source_url, retrieved_at, endpoint, params) para "
        "rastreabilidade."
    ),
    port=_settings.port,
)

localidades_tools.register_localidades_tools(mcp)
agregados_tools.register_agregados_tools(mcp)
sidra_tools.register_sidra_tools(mcp)
perfil_tools.register_perfil_tools(mcp)
comparacao_tools.register_comparacao_tools(mcp)
geo_tools.register_geo_tools(mcp)


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
        "1. Monte a lista de municípios no formato "
        '`[{"nome": ..., "uf": ...}, ...]` e chame a tool '
        "`comparar_municipios(municipios=..., indicadores=[...], ano=...)`. "
        "Ela resolve o código IBGE de cada município (reportando "
        "ambiguidades em `municipios_nao_resolvidos`) e já consulta os "
        "indicadores básicos disponíveis (atualmente, população residente "
        "estimada).\n"
        "2. Se `indicador` não estiver em `data.indicadores_consultados` "
        "(veja `data.indicadores_nao_implementados` e `warnings`), use "
        "`listar_agregados`, `obter_metadados_agregado` e "
        "`listar_variaveis_agregado` para localizar o agregado/variável do "
        "SIDRA correspondentes e `consultar_agregado` para cada município, "
        "usando o mesmo período sempre que possível.\n"
        "3. Ao apresentar os resultados, sempre cite:\n"
        "   - a fonte (`data.fontes` ou `metadata.source_name`/"
        "`metadata.source_url`);\n"
        "   - o ano/período de referência (`periodo` de cada indicador);\n"
        "   - a unidade de medida (`unidade`);\n"
        "   - limitações: `data.limitacoes`, municípios em "
        "`municipios_nao_resolvidos`, e `warnings` retornados pelas tools.\n"
        "4. Não invente valores: se um indicador não estiver disponível para "
        "um município, informe isso explicitamente em vez de estimar."
    )


def main() -> None:
    """Configura logging e inicia o servidor MCP."""
    configure_logging()
    logging.getLogger(__name__).info("Iniciando mcp-ibge (transporte=%s)", _settings.transport)
    transport = cast("Literal['stdio', 'sse', 'streamable-http']", _settings.transport)
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
