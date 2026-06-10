"""Testes de contrato das tools MCP: nomes registrados e formato do envelope."""

from __future__ import annotations

import httpx
import respx

from mcp_ibge.clients.agregados import AGREGADOS_PATH
from mcp_ibge.clients.localidades import LOCALIDADES_PATH
from mcp_ibge.config import get_settings
from mcp_ibge.server import mcp

LOCALIDADES_BASE_URL = f"{get_settings().api_base_url}{LOCALIDADES_PATH}"
AGREGADOS_BASE_URL = f"{get_settings().api_base_url}{AGREGADOS_PATH}"

EXPECTED_TOOLS = {
    "listar_regioes",
    "listar_estados",
    "obter_estado",
    "listar_municipios",
    "buscar_municipio",
    "obter_codigo_municipio",
    "obter_municipio_por_codigo",
    "listar_distritos",
    "listar_agregados",
    "obter_metadados_agregado",
    "consultar_dados_agregado",
    "obter_populacao_municipio",
}


async def test_todas_as_tools_esperadas_estao_registradas():
    tools = await mcp.list_tools()
    nomes = {tool.name for tool in tools}

    assert EXPECTED_TOOLS.issubset(nomes)


def _assert_metadata_contract(metadata: dict) -> None:
    for campo in ("source_name", "source_url", "retrieved_at", "endpoint", "params"):
        assert campo in metadata
    assert metadata["source_name"] == get_settings().source_name


@respx.mock
async def test_envelope_de_sucesso_contem_metadata_e_data():
    respx.get(f"{LOCALIDADES_BASE_URL}/regioes").mock(
        return_value=httpx.Response(200, json=[{"id": 1, "sigla": "N", "nome": "Norte"}])
    )

    _, structured = await mcp.call_tool("listar_regioes", {})

    assert "data" in structured
    assert "error" not in structured
    _assert_metadata_contract(structured["metadata"])
    assert structured["metadata"]["endpoint"] == f"{LOCALIDADES_BASE_URL}/regioes"


@respx.mock
async def test_envelope_de_erro_contem_metadata_e_error():
    respx.get(f"{LOCALIDADES_BASE_URL}/municipios/9999999").mock(
        return_value=httpx.Response(404, json={"detail": "not found"})
    )

    _, structured = await mcp.call_tool("obter_municipio_por_codigo", {"codigo_ibge": 9999999})

    assert "error" in structured
    assert "data" not in structured
    _assert_metadata_contract(structured["metadata"])


@respx.mock
async def test_consultar_dados_agregado_resolve_alias_br():
    dados = [{"id": "9324", "resultados": []}]
    respx.get(f"{AGREGADOS_BASE_URL}/6579/periodos/-1/variaveis/9324").mock(
        return_value=httpx.Response(200, json=dados)
    )

    _, structured = await mcp.call_tool(
        "consultar_dados_agregado",
        {"agregado_id": 6579, "variaveis": "9324", "localidades": "BR"},
    )

    assert structured["data"] == dados
    assert structured["metadata"]["params"]["localidades"] == "N1[all]"


@respx.mock
async def test_obter_populacao_municipio_envelope():
    endpoint = f"{AGREGADOS_BASE_URL}/6579/periodos/-1/variaveis/9324"
    dados = [{"id": "9324", "resultados": []}]
    respx.get(endpoint).mock(return_value=httpx.Response(200, json=dados))

    _, structured = await mcp.call_tool(
        "obter_populacao_municipio", {"codigo_municipio": "4205407"}
    )

    assert structured["data"] == dados
    assert structured["metadata"]["endpoint"] == endpoint
    assert structured["metadata"]["params"]["codigo_municipio"] == "4205407"
