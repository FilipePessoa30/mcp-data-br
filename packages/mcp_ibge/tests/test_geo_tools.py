"""Testes de contrato das tools MCP do módulo geoespacial."""

from __future__ import annotations

import httpx
import respx

from mcp_ibge.config import get_settings
from mcp_ibge.geo.client import MALHAS_PATH
from mcp_ibge.server import mcp

from .conftest import assert_envelope_contract

BASE_URL = f"{get_settings().api_base_url}{MALHAS_PATH}"

EXPECTED_GEO_TOOLS = {
    "obter_malha_municipio",
    "obter_malha_uf",
    "obter_bbox_municipio",
    "gerar_geojson_municipios",
}


async def test_tools_geo_estao_registradas():
    tools = await mcp.list_tools()
    nomes = {tool.name for tool in tools}

    assert EXPECTED_GEO_TOOLS.issubset(nomes)


@respx.mock
async def test_obter_malha_municipio_retorna_contrato(malha_municipio_niteroi):
    respx.get(f"{BASE_URL}/municipios/3303302").mock(
        return_value=httpx.Response(200, json=malha_municipio_niteroi)
    )

    _, structured = await mcp.call_tool("obter_malha_municipio", {"codigo_ibge": 3303302})

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert structured["data"] == malha_municipio_niteroi
    assert structured["warnings"]
    assert structured["metadata"]["territorial_level"] == "N6"


@respx.mock
async def test_obter_malha_uf_retorna_contrato(malha_uf_rj):
    respx.get(f"{BASE_URL}/estados/RJ").mock(return_value=httpx.Response(200, json=malha_uf_rj))

    _, structured = await mcp.call_tool("obter_malha_uf", {"uf": "RJ"})

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert structured["data"] == malha_uf_rj
    assert structured["warnings"]
    assert structured["metadata"]["territorial_level"] == "N3"


@respx.mock
async def test_obter_bbox_municipio_retorna_contrato(malha_municipio_niteroi):
    respx.get(f"{BASE_URL}/municipios/3303302").mock(
        return_value=httpx.Response(200, json=malha_municipio_niteroi)
    )

    _, structured = await mcp.call_tool("obter_bbox_municipio", {"codigo_ibge": 3303302})

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert structured["data"]["bbox"] == [-43.13, -22.92, -43.05, -22.86]
    assert structured["warnings"]


@respx.mock
async def test_gerar_geojson_municipios_retorna_contrato(malha_municipio_niteroi):
    respx.get(f"{BASE_URL}/municipios/3303302").mock(
        return_value=httpx.Response(200, json=malha_municipio_niteroi)
    )

    _, structured = await mcp.call_tool("gerar_geojson_municipios", {"codigos_ibge": [3303302]})

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert structured["data"]["type"] == "FeatureCollection"
    assert structured["data"]["features"][0]["properties"]["codigo_ibge"] == 3303302
    assert structured["data"]["codigos_nao_resolvidos"] == []
    assert structured["warnings"]


async def test_gerar_geojson_municipios_lista_vazia_retorna_envelope_de_erro():
    _, structured = await mcp.call_tool("gerar_geojson_municipios", {"codigos_ibge": []})

    assert_envelope_contract(structured)
    assert structured["ok"] is False
    assert structured["data"] is None
    assert structured["errors"]


@respx.mock
async def test_obter_malha_municipio_resposta_invalida_retorna_envelope_de_erro():
    respx.get(f"{BASE_URL}/municipios/3303302").mock(
        return_value=httpx.Response(200, json={"erro": "sem malha"})
    )

    _, structured = await mcp.call_tool("obter_malha_municipio", {"codigo_ibge": 3303302})

    assert_envelope_contract(structured)
    assert structured["ok"] is False
    assert structured["data"] is None
    assert structured["errors"]
