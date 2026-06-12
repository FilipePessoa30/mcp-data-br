"""Testes da camada de serviço `SidraService` (TypedToolResult, fonte e metadata)."""

from __future__ import annotations

import httpx
import respx

from mcp_ibge.clients.agregados import AGREGADOS_PATH
from mcp_ibge.config import get_settings
from mcp_ibge.services.sidra_service import SidraService

BASE_URL = f"{get_settings().api_base_url}{AGREGADOS_PATH}"

LISTA_AGREGADOS = [
    {
        "id": "POP",
        "nome": "Estimativas de população",
        "agregados": [{"id": 6579, "nome": "População residente estimada"}],
    },
    {
        "id": "IPCA",
        "nome": "Índice de Preços",
        "agregados": [{"id": 7060, "nome": "IPCA - Variação mensal"}],
    },
]

METADADOS_POPULACAO = {
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


# ---------------------------------------------------------------------------
# buscar_tabelas_sidra
# ---------------------------------------------------------------------------


@respx.mock
async def test_buscar_tabelas_sidra_encontra_por_palavra_chave():
    respx.get(BASE_URL).mock(return_value=httpx.Response(200, json=LISTA_AGREGADOS))

    service = SidraService()
    result = await service.buscar_tabelas_sidra("população")

    assert result.ok is True
    assert [item.id for item in result.data] == ["6579"]
    assert result.data[0].pontuacao > 0
    assert result.warnings == []


@respx.mock
async def test_buscar_tabelas_sidra_sem_resultado_gera_warning():
    respx.get(BASE_URL).mock(return_value=httpx.Response(200, json=LISTA_AGREGADOS))

    service = SidraService()
    result = await service.buscar_tabelas_sidra("agropecuária")

    assert result.ok is True
    assert result.data == []
    assert result.warnings


async def test_buscar_tabelas_sidra_limite_invalido():
    service = SidraService()
    result = await service.buscar_tabelas_sidra("população", limite=0)

    assert result.ok is False
    assert result.data == []
    assert result.errors


# ---------------------------------------------------------------------------
# explicar_tabela_sidra
# ---------------------------------------------------------------------------


@respx.mock
async def test_explicar_tabela_sidra():
    respx.get(f"{BASE_URL}/6579/metadados").mock(
        return_value=httpx.Response(200, json=METADADOS_POPULACAO)
    )

    service = SidraService()
    result = await service.explicar_tabela_sidra("6579")

    assert result.ok is True
    assert result.data.nome == "População residente estimada"
    assert result.data.niveis_territoriais == ["N1", "N3", "N6"]
    assert result.data.limitacoes


@respx.mock
async def test_explicar_tabela_sidra_inexistente():
    respx.get(f"{BASE_URL}/9999999/metadados").mock(return_value=httpx.Response(404))

    service = SidraService()
    result = await service.explicar_tabela_sidra("9999999")

    assert result.ok is False
    assert result.data is None
    assert result.errors


# ---------------------------------------------------------------------------
# listar_variaveis_tabela_sidra / listar_classificacoes_tabela_sidra
# ---------------------------------------------------------------------------


@respx.mock
async def test_listar_variaveis_tabela_sidra():
    respx.get(f"{BASE_URL}/6579/metadados").mock(
        return_value=httpx.Response(200, json=METADADOS_POPULACAO)
    )

    service = SidraService()
    result = await service.listar_variaveis_tabela_sidra("6579")

    assert result.ok is True
    assert [v.id for v in result.data] == ["9324"]


@respx.mock
async def test_listar_classificacoes_tabela_sidra():
    respx.get(f"{BASE_URL}/6579/metadados").mock(
        return_value=httpx.Response(200, json=METADADOS_POPULACAO)
    )

    service = SidraService()
    result = await service.listar_classificacoes_tabela_sidra("6579")

    assert result.ok is True
    assert result.data == []


# ---------------------------------------------------------------------------
# sugerir_consulta_sidra
# ---------------------------------------------------------------------------


@respx.mock
async def test_sugerir_consulta_sidra():
    respx.get(BASE_URL).mock(return_value=httpx.Response(200, json=LISTA_AGREGADOS))
    respx.get(f"{BASE_URL}/6579/metadados").mock(
        return_value=httpx.Response(200, json=METADADOS_POPULACAO)
    )

    service = SidraService()
    result = await service.sugerir_consulta_sidra("população dos municípios em 2024")

    assert result.ok is True
    assert result.data.agregado_id == "6579"
    assert result.data.variaveis == "9324"
    assert result.data.localidades == "N6[all]"
    assert result.warnings


@respx.mock
async def test_sugerir_consulta_sidra_sem_candidatos():
    respx.get(BASE_URL).mock(return_value=httpx.Response(200, json=LISTA_AGREGADOS))

    service = SidraService()
    result = await service.sugerir_consulta_sidra("xpto qwerty")

    assert result.ok is False
    assert result.data is None
    assert result.errors


# ---------------------------------------------------------------------------
# validar_consulta_sidra
# ---------------------------------------------------------------------------


@respx.mock
async def test_validar_consulta_sidra_valida():
    respx.get(f"{BASE_URL}/6579/metadados").mock(
        return_value=httpx.Response(200, json=METADADOS_POPULACAO)
    )

    service = SidraService()
    result = await service.validar_consulta_sidra("6579", "9324", "N6[3550308]", "2024")

    assert result.ok is True
    assert result.data.valido is True
    assert result.errors == []


@respx.mock
async def test_validar_consulta_sidra_variavel_invalida():
    respx.get(f"{BASE_URL}/6579/metadados").mock(
        return_value=httpx.Response(200, json=METADADOS_POPULACAO)
    )

    service = SidraService()
    result = await service.validar_consulta_sidra("6579", "99999", "N6[3550308]", "2024")

    assert result.ok is False
    assert result.data.valido is False
    assert result.errors


async def test_validar_consulta_sidra_formato_invalido():
    service = SidraService()
    result = await service.validar_consulta_sidra("abc", "9324", "N6[3550308]", "2024")

    assert result.ok is False
    assert result.data is None
    assert result.errors


# ---------------------------------------------------------------------------
# executar_consulta_sidra_validada
# ---------------------------------------------------------------------------


@respx.mock
async def test_executar_consulta_sidra_validada_executa_quando_valida():
    respx.get(f"{BASE_URL}/6579/metadados").mock(
        return_value=httpx.Response(200, json=METADADOS_POPULACAO)
    )
    respx.get(f"{BASE_URL}/6579/periodos/2024/variaveis/9324").mock(
        return_value=httpx.Response(200, json=DADOS_CONSULTA)
    )

    service = SidraService()
    result = await service.executar_consulta_sidra_validada("6579", "9324", "N6[3550308]", "2024")

    assert result.ok is True
    assert result.data[0].valor == 12345678.0


@respx.mock
async def test_executar_consulta_sidra_validada_nao_executa_quando_invalida():
    respx.get(f"{BASE_URL}/6579/metadados").mock(
        return_value=httpx.Response(200, json=METADADOS_POPULACAO)
    )

    service = SidraService()
    result = await service.executar_consulta_sidra_validada("6579", "99999", "N6[3550308]", "2024")

    assert result.ok is False
    assert result.data == []
    assert result.errors
