"""Tools MCP do domínio de Localidades (regiões, estados, municípios)."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ..clients.localidades import LOCALIDADES_PATH
from ..config import get_settings
from ..services.localidades_service import LocalidadesService
from . import run_tool

_service = LocalidadesService()


def register(mcp: FastMCP) -> None:
    """Registra as tools de Localidades na instância FastMCP fornecida."""
    base_url = f"{get_settings().api_base_url}{LOCALIDADES_PATH}"

    @mcp.tool()
    async def listar_regioes() -> dict[str, Any]:
        """Lista as 5 grandes regiões geográficas do Brasil (Norte, Nordeste, Sudeste, Sul, CO)."""
        return await run_tool(
            _service.listar_regioes(),
            endpoint=f"{base_url}/regioes",
            params={},
        )

    @mcp.tool()
    async def listar_estados(
        regiao: Annotated[
            str | None,
            Field(
                description='Sigla da grande região ("N", "NE", "CO", "SE", "S") ou ID numérico.'
            ),
        ] = None,
    ) -> dict[str, Any]:
        """Lista os 26 estados e o Distrito Federal, com sigla, nome e região."""
        return await run_tool(
            _service.listar_estados(regiao=regiao),
            endpoint=f"{base_url}/estados",
            params={"regiao": regiao} if regiao else {},
        )

    @mcp.tool()
    async def obter_estado(
        uf: Annotated[
            str, Field(description='Sigla (ex.: "SP") ou ID IBGE (ex.: "35") do estado.')
        ],
    ) -> dict[str, Any]:
        """Obtém os detalhes de um estado (UF) brasileiro."""
        return await run_tool(
            _service.obter_estado(uf),
            endpoint=f"{base_url}/estados/{uf}",
            params={"uf": uf},
        )

    @mcp.tool()
    async def listar_municipios(
        uf: Annotated[
            str | None,
            Field(description='Sigla (ex.: "SP") ou ID IBGE. Sem isso, lista o Brasil todo.'),
        ] = None,
    ) -> dict[str, Any]:
        """Lista municípios brasileiros, opcionalmente filtrados por estado.

        Sem o parâmetro `uf`, retorna todos os ~5570 municípios do Brasil.
        """
        endpoint = f"{base_url}/estados/{uf}/municipios" if uf else f"{base_url}/municipios"
        return await run_tool(
            _service.listar_municipios(uf=uf),
            endpoint=endpoint,
            params={"uf": uf} if uf else {},
        )

    @mcp.tool()
    async def obter_municipio(
        codigo: Annotated[
            str,
            Field(description='Código IBGE do município com 7 dígitos (ex.: "3550308" = SP).'),
        ],
    ) -> dict[str, Any]:
        """Obtém os detalhes completos de um município pelo código IBGE."""
        return await run_tool(
            _service.obter_municipio(codigo),
            endpoint=f"{base_url}/municipios/{codigo}",
            params={"codigo": codigo},
        )

    @mcp.tool()
    async def buscar_municipios_por_nome(
        nome: Annotated[str, Field(description='Termo de busca (ex.: "Sao Jose").')],
        uf: Annotated[
            str | None,
            Field(description="Restringe a busca aos municípios desta UF (sigla ou ID)."),
        ] = None,
        limit: Annotated[int, Field(description="Número máximo de resultados.", ge=1, le=200)] = 20,
    ) -> dict[str, Any]:
        """Busca municípios cujo nome contenha o termo informado.

        A busca ignora maiúsculas/minúsculas e acentos (ex.: "sao jose"
        encontra "São José dos Campos"). Útil para descobrir o código IBGE de
        um município a partir do nome.
        """
        endpoint = f"{base_url}/estados/{uf}/municipios" if uf else f"{base_url}/municipios"
        params: dict[str, Any] = {"nome": nome, "limit": limit}
        if uf:
            params["uf"] = uf

        return await run_tool(
            _service.buscar_municipios_por_nome(nome=nome, uf=uf, limit=limit),
            endpoint=endpoint,
            params=params,
        )

    @mcp.tool()
    async def obter_distritos_municipio(
        codigo: Annotated[
            str,
            Field(description='Código IBGE do município com 7 dígitos (ex.: "3550308" = SP).'),
        ],
    ) -> dict[str, Any]:
        """Lista os distritos de um município pelo código IBGE."""
        return await run_tool(
            _service.obter_distritos_municipio(codigo),
            endpoint=f"{base_url}/municipios/{codigo}/distritos",
            params={"municipio_id": codigo},
        )
