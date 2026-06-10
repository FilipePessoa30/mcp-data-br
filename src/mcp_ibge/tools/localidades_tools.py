"""Tools MCP do domínio de Localidades (regiões, estados, municípios, distritos)."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ..services.localidades_service import LocalidadesService
from . import run_typed_tool

_service = LocalidadesService()


def register(mcp: FastMCP) -> None:
    """Registra as tools de Localidades na instância FastMCP fornecida."""

    @mcp.tool()
    async def listar_regioes() -> dict[str, Any]:
        """Lista as 5 grandes regiões geográficas do Brasil (Norte, Nordeste, Sudeste, Sul, CO)."""
        return await run_typed_tool(_service.listar_regioes())

    @mcp.tool()
    async def listar_estados() -> dict[str, Any]:
        """Lista os 26 estados e o Distrito Federal, ordenados por nome."""
        return await run_typed_tool(_service.listar_estados())

    @mcp.tool()
    async def obter_estado(
        uf: Annotated[
            str, Field(description='Sigla (ex.: "SP") ou código IBGE (ex.: "35") do estado.')
        ],
    ) -> dict[str, Any]:
        """Obtém os detalhes de um estado (UF) brasileiro."""
        return await run_typed_tool(_service.obter_estado(uf))

    @mcp.tool()
    async def listar_municipios(
        uf: Annotated[str, Field(description='Sigla (ex.: "SP") ou código IBGE da UF.')],
    ) -> dict[str, Any]:
        """Lista os municípios de uma UF."""
        return await run_typed_tool(_service.listar_municipios(uf))

    @mcp.tool()
    async def buscar_municipio(
        nome: Annotated[str, Field(description="Nome (ou parte do nome) do município a buscar.")],
        uf: Annotated[
            str | None,
            Field(description="Restringe a busca aos municípios desta UF (sigla ou código)."),
        ] = None,
        limite: Annotated[
            int, Field(description="Número máximo de candidatos retornados.", ge=1, le=50)
        ] = 10,
    ) -> dict[str, Any]:
        """Busca municípios por nome com correspondência aproximada (ignora acentos/caixa).

        Tenta correspondência exata, depois "contém" e, por fim, similaridade
        textual. Sem `uf`, busca em todo o Brasil. Quando há mais de uma
        correspondência, a resposta inclui um aviso (`warnings`) sugerindo
        refinar a busca.
        """
        return await run_typed_tool(_service.buscar_municipio(nome, uf=uf, limite=limite))

    @mcp.tool()
    async def obter_codigo_municipio(
        nome: Annotated[str, Field(description="Nome do município.")],
        uf: Annotated[str, Field(description='Sigla (ex.: "SP") ou código IBGE da UF.')],
    ) -> dict[str, Any]:
        """Obtém o código IBGE de 7 dígitos de um município pelo nome e UF.

        Retorna erro se nenhum município corresponder ou se o nome for
        ambíguo dentro da UF informada.
        """
        return await run_typed_tool(_service.obter_codigo_municipio(nome, uf))

    @mcp.tool()
    async def obter_municipio_por_codigo(
        codigo_ibge: Annotated[
            int, Field(description="Código IBGE do município com 7 dígitos (ex.: 3550308 = SP).")
        ],
    ) -> dict[str, Any]:
        """Obtém os detalhes de um município pelo código IBGE, com UF e região."""
        return await run_typed_tool(_service.obter_municipio_por_codigo(codigo_ibge))

    @mcp.tool()
    async def listar_distritos(
        codigo_municipio: Annotated[
            int, Field(description="Código IBGE do município com 7 dígitos (ex.: 3550308 = SP).")
        ],
    ) -> dict[str, Any]:
        """Lista os distritos de um município pelo código IBGE."""
        return await run_typed_tool(_service.listar_distritos(codigo_municipio))
