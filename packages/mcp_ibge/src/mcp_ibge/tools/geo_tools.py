"""Tools MCP do módulo geoespacial (malhas e bounding boxes)."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ..geo.service import MAX_MUNICIPIOS_GEOJSON, GeoService
from . import run_typed_tool

_service = GeoService()

_SIMPLIFICADO_DESCRIPTION = (
    "Se `true` (padrão), retorna a geometria simplificada (qualidade "
    '"minima" da malha do IBGE) — resposta bem menor, adequada para '
    "visualização. Se `false`, retorna a geometria mais detalhada "
    '(qualidade "maxima"), que pode ser bem maior e, em casos extremos, '
    "exceder o limite de tamanho de resposta."
)

_CODIGOS_IBGE_DESCRIPTION = (
    "Códigos IBGE de 7 dígitos dos municípios, ex.: `[3304557, 3303302]`. "
    f"Máximo de {MAX_MUNICIPIOS_GEOJSON} municípios por chamada."
)


def register_geo_tools(mcp: FastMCP) -> None:
    """Registra as tools do módulo geoespacial na instância FastMCP fornecida."""

    @mcp.tool()
    async def obter_malha_municipio(
        codigo_ibge: Annotated[
            int, Field(description="Código IBGE de 7 dígitos do município (ex.: 3304557).")
        ],
        simplificado: Annotated[bool, Field(description=_SIMPLIFICADO_DESCRIPTION)] = True,
    ) -> dict[str, Any]:
        """Retorna a malha geográfica (GeoJSON) de um município.

        `data` é um objeto GeoJSON (`FeatureCollection`, `Feature` ou
        geometria) obtido da API de Malhas do IBGE
        (https://servicodados.ibge.gov.br/api/docs/malhas). Quando
        `simplificado=true` (padrão), a resposta inclui um aviso em
        `warnings` informando que a geometria foi simplificada.
        """
        return await run_typed_tool(
            _service.obter_malha_municipio(codigo_ibge, simplificado=simplificado)
        )

    @mcp.tool()
    async def obter_malha_uf(
        uf: Annotated[
            str, Field(description='Sigla (ex.: "RJ") ou código IBGE (ex.: "33") da UF.')
        ],
        simplificado: Annotated[bool, Field(description=_SIMPLIFICADO_DESCRIPTION)] = True,
    ) -> dict[str, Any]:
        """Retorna a malha geográfica (GeoJSON) de uma UF.

        `data` é um objeto GeoJSON (`FeatureCollection`, `Feature` ou
        geometria) obtido da API de Malhas do IBGE
        (https://servicodados.ibge.gov.br/api/docs/malhas). Quando
        `simplificado=true` (padrão), a resposta inclui um aviso em
        `warnings` informando que a geometria foi simplificada.
        """
        return await run_typed_tool(_service.obter_malha_uf(uf, simplificado=simplificado))

    @mcp.tool()
    async def obter_bbox_municipio(
        codigo_ibge: Annotated[
            int, Field(description="Código IBGE de 7 dígitos do município (ex.: 3304557).")
        ],
    ) -> dict[str, Any]:
        """Retorna o bounding box (caixa delimitadora) de um município, em WGS84.

        `data` traz `min_longitude`, `min_latitude`, `max_longitude`,
        `max_latitude` e `bbox` (no formato `[west, south, east, north]` do
        GeoJSON), calculados a partir da malha simplificada do município
        (https://servicodados.ibge.gov.br/api/docs/malhas) — por isso a
        resposta sempre inclui um aviso em `warnings` sobre a simplificação
        da geometria usada no cálculo.
        """
        return await run_typed_tool(_service.obter_bbox_municipio(codigo_ibge))

    @mcp.tool()
    async def gerar_geojson_municipios(
        codigos_ibge: Annotated[list[int], Field(description=_CODIGOS_IBGE_DESCRIPTION)],
    ) -> dict[str, Any]:
        """Combina as malhas de vários municípios em uma única `FeatureCollection` GeoJSON.

        Cada município resolvido aparece como uma `Feature` com
        `properties.codigo_ibge` e a geometria simplificada da malha. Códigos
        que não retornarem uma malha válida aparecem em
        `data.codigos_nao_resolvidos`, sem interromper a geração para os
        demais. A resposta sempre inclui um aviso em `warnings` sobre a
        simplificação da geometria.
        """
        return await run_typed_tool(_service.gerar_geojson_municipios(codigos_ibge))
