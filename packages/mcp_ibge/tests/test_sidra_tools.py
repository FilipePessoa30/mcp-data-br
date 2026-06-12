"""Testes de contrato das tools MCP do SIDRA Query Builder: existência e formato JSON."""

from __future__ import annotations

import httpx
import pytest
import respx

from mcp_ibge.clients.agregados import AGREGADOS_PATH
from mcp_ibge.config import get_settings
from mcp_ibge.server import mcp

from .conftest import assert_envelope_contract

BASE_URL = f"{get_settings().api_base_url}{AGREGADOS_PATH}"

SIDRA_TOOLS = {
    "buscar_tabelas_sidra",
    "explicar_tabela_sidra",
    "listar_variaveis_tabela_sidra",
    "listar_classificacoes_tabela_sidra",
    "sugerir_consulta_sidra",
    "validar_consulta_sidra",
    "executar_consulta_sidra_validada",
}

LISTA_AGREGADOS = [
    {
        "id": "POP",
        "nome": "Estimativas de população",
        "agregados": [{"id": 6579, "nome": "População residente estimada"}],
    },
]

METADADOS = {
    "id": 6579,
    "nome": "População residente estimada",
    "pesquisa": "Estimativas de População",
    "assunto": "População",
    "periodicidade": {"frequencia": "anual", "inicio": 2001, "fim": 2024},
    "nivelTerritorial": {"Administrativo": ["N1", "N3", "N6"], "Especial": [], "IBGE": []},
    "variaveis": [{"id": 9324, "nome": "População residente estimada", "unidade": "Pessoas"}],
    "classificacoes": [],
}

DADOS_CONSULTA = [
    {
        "id": "9324",
        "unidade": "Pessoas",
        "resultados": [
            {
                "series": [
                    {
                        "localidade": {"id": "3550308", "nome": "São Paulo"},
                        "serie": {"2024": "12345678"},
                    }
                ]
            }
        ],
    }
]


async def test_todas_as_tools_de_sidra_estao_registradas():
    tools = await mcp.list_tools()
    nomes = {tool.name for tool in tools}

    assert SIDRA_TOOLS.issubset(nomes)


@respx.mock
@pytest.mark.parametrize(
    ("nome_tool", "argumentos", "endpoint_mock", "resposta_mock"),
    [
        ("buscar_tabelas_sidra", {"tema": "população"}, BASE_URL, LISTA_AGREGADOS),
        (
            "explicar_tabela_sidra",
            {"agregado_id": "6579"},
            f"{BASE_URL}/6579/metadados",
            METADADOS,
        ),
        (
            "listar_variaveis_tabela_sidra",
            {"agregado_id": "6579"},
            f"{BASE_URL}/6579/metadados",
            METADADOS,
        ),
        (
            "listar_classificacoes_tabela_sidra",
            {"agregado_id": "6579"},
            f"{BASE_URL}/6579/metadados",
            METADADOS,
        ),
    ],
)
async def test_tool_retorna_contrato_json_em_caso_de_sucesso(
    nome_tool, argumentos, endpoint_mock, resposta_mock
):
    respx.get(endpoint_mock).mock(return_value=httpx.Response(200, json=resposta_mock))

    _, structured = await mcp.call_tool(nome_tool, argumentos)

    assert_envelope_contract(structured)
    assert "data" in structured


@respx.mock
async def test_sugerir_consulta_sidra_nao_executa_consulta():
    respx.get(BASE_URL).mock(return_value=httpx.Response(200, json=LISTA_AGREGADOS))
    respx.get(f"{BASE_URL}/6579/metadados").mock(return_value=httpx.Response(200, json=METADADOS))

    _, structured = await mcp.call_tool(
        "sugerir_consulta_sidra", {"pergunta": "população dos municípios em 2024"}
    )

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert structured["data"]["agregado_id"] == "6579"
    assert structured["data"]["localidades"] == "N6[all]"
    assert structured["warnings"]


@respx.mock
async def test_validar_consulta_sidra_valida():
    respx.get(f"{BASE_URL}/6579/metadados").mock(return_value=httpx.Response(200, json=METADADOS))

    _, structured = await mcp.call_tool(
        "validar_consulta_sidra",
        {
            "agregado_id": "6579",
            "variaveis": "9324",
            "localidades": "N6[3550308]",
            "periodos": "2024",
        },
    )

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert structured["data"]["valido"] is True


@respx.mock
async def test_validar_consulta_sidra_invalida():
    respx.get(f"{BASE_URL}/6579/metadados").mock(return_value=httpx.Response(200, json=METADADOS))

    _, structured = await mcp.call_tool(
        "validar_consulta_sidra",
        {
            "agregado_id": "6579",
            "variaveis": "99999",
            "localidades": "N6[3550308]",
            "periodos": "2024",
        },
    )

    assert_envelope_contract(structured)
    assert structured["ok"] is False
    assert structured["data"]["valido"] is False
    assert structured["errors"]


@respx.mock
async def test_executar_consulta_sidra_validada_executa_quando_valida():
    respx.get(f"{BASE_URL}/6579/metadados").mock(return_value=httpx.Response(200, json=METADADOS))
    respx.get(f"{BASE_URL}/6579/periodos/2024/variaveis/9324").mock(
        return_value=httpx.Response(200, json=DADOS_CONSULTA)
    )

    _, structured = await mcp.call_tool(
        "executar_consulta_sidra_validada",
        {
            "agregado_id": "6579",
            "variaveis": "9324",
            "localidades": "N6[3550308]",
            "periodos": "2024",
        },
    )

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert structured["data"][0]["valor"] == 12345678.0


@respx.mock
async def test_executar_consulta_sidra_validada_nao_executa_quando_invalida():
    respx.get(f"{BASE_URL}/6579/metadados").mock(return_value=httpx.Response(200, json=METADADOS))

    _, structured = await mcp.call_tool(
        "executar_consulta_sidra_validada",
        {
            "agregado_id": "6579",
            "variaveis": "99999",
            "localidades": "N6[3550308]",
            "periodos": "2024",
        },
    )

    assert_envelope_contract(structured)
    assert structured["ok"] is False
    assert structured["data"] == []
    assert structured["errors"]


@respx.mock
async def test_tool_retorna_contrato_json_em_caso_de_erro():
    respx.get(f"{BASE_URL}/9999999/metadados").mock(return_value=httpx.Response(404))

    _, structured = await mcp.call_tool("explicar_tabela_sidra", {"agregado_id": "9999999"})

    assert_envelope_contract(structured)
    assert structured["ok"] is False
    assert structured["data"] is None
    assert structured["errors"]
