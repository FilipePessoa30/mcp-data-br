"""Testes do cliente "fino" `AgregadosClient` (sem regras de negócio)."""

from __future__ import annotations

import httpx
import pytest
import respx

from mcp_ibge.clients.agregados import AGREGADOS_PATH, AgregadosClient
from mcp_ibge.config import get_settings
from mcp_ibge.utils.errors import IBGENotFoundError, IBGEValidationError

BASE_URL = f"{get_settings().api_base_url}{AGREGADOS_PATH}"

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
    "variaveis": [{"id": 9324, "nome": "População residente estimada", "unidade": "Pessoas"}],
}

PERIODOS = [{"id": "2024", "literals": ["2024"], "modificacao": "2025-08-29T00:00:00.000-03:00"}]

VARIAVEIS = [{"id": 9324, "nome": "População residente estimada", "unidade": "Pessoas"}]

LOCALIDADES = [{"id": "3550308", "nome": "São Paulo", "nivel": {"id": "N6", "nome": "Município"}}]

DADOS = [
    {
        "id": "9324",
        "variavel": "População residente estimada",
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


@respx.mock
async def test_list_agregados_sem_filtro():
    respx.get(BASE_URL).mock(return_value=httpx.Response(200, json=LISTA_AGREGADOS))

    client = AgregadosClient()
    result = await client.list_agregados()

    assert result.data == LISTA_AGREGADOS
    assert result.endpoint == BASE_URL
    assert result.params == {}


@respx.mock
async def test_list_agregados_repassa_query_params():
    route = respx.get(BASE_URL).mock(return_value=httpx.Response(200, json=[]))

    client = AgregadosClient()
    await client.list_agregados(pesquisa="Censo Demográfico", assunto="População")

    request = route.calls.last.request
    assert request.url.params["pesquisa"] == "Censo Demográfico"
    assert request.url.params["assunto"] == "População"


@respx.mock
async def test_get_agregado_metadata():
    respx.get(f"{BASE_URL}/6579/metadados").mock(return_value=httpx.Response(200, json=METADADOS))

    client = AgregadosClient()
    result = await client.get_agregado_metadata("6579")

    assert result.data == METADADOS
    assert result.endpoint == f"{BASE_URL}/6579/metadados"
    assert result.params == {"agregado_id": "6579"}


@respx.mock
async def test_get_agregado_metadata_agregado_inexistente_404():
    respx.get(f"{BASE_URL}/9999999/metadados").mock(return_value=httpx.Response(404))

    client = AgregadosClient()
    with pytest.raises(IBGENotFoundError):
        await client.get_agregado_metadata("9999999")


@respx.mock
async def test_get_agregado_metadata_resposta_vazia_levanta_not_found():
    respx.get(f"{BASE_URL}/9999999/metadados").mock(return_value=httpx.Response(200, json={}))

    client = AgregadosClient()
    with pytest.raises(IBGENotFoundError):
        await client.get_agregado_metadata("9999999")


@respx.mock
async def test_get_agregado_periodos():
    respx.get(f"{BASE_URL}/6579/periodos").mock(return_value=httpx.Response(200, json=PERIODOS))

    client = AgregadosClient()
    result = await client.get_agregado_periodos("6579")

    assert result.data == PERIODOS
    assert result.params == {"agregado_id": "6579"}


@respx.mock
async def test_get_agregado_variaveis():
    respx.get(f"{BASE_URL}/6579/variaveis").mock(return_value=httpx.Response(200, json=VARIAVEIS))

    client = AgregadosClient()
    result = await client.get_agregado_variaveis("6579")

    assert result.data == VARIAVEIS
    assert result.params == {"agregado_id": "6579"}


@respx.mock
async def test_get_agregado_localidades():
    respx.get(f"{BASE_URL}/6579/localidades/N6").mock(
        return_value=httpx.Response(200, json=LOCALIDADES)
    )

    client = AgregadosClient()
    result = await client.get_agregado_localidades("6579", "N6")

    assert result.data == LOCALIDADES
    assert result.params == {"agregado_id": "6579", "niveis": "N6"}


@respx.mock
async def test_query_agregado_valores_padrao():
    route = respx.get(f"{BASE_URL}/6579/periodos/-1/variaveis/9324").mock(
        return_value=httpx.Response(200, json=DADOS)
    )

    client = AgregadosClient()
    result = await client.query_agregado(
        "6579", variaveis="9324", localidades="N1[all]", periodos="-1"
    )

    assert result.data == DADOS
    assert route.calls.last.request.url.params["localidades"] == "N1[all]"
    assert result.params["localidades"] == "N1[all]"
    assert result.params["periodos"] == "-1"


@respx.mock
async def test_query_agregado_com_classificacao_e_view():
    route = respx.get(f"{BASE_URL}/6579/periodos/2021/variaveis/9324").mock(
        return_value=httpx.Response(200, json=DADOS)
    )

    client = AgregadosClient()
    result = await client.query_agregado(
        "6579",
        variaveis="9324",
        localidades="N6[3550308]",
        periodos="2021",
        classificacao="2[6794]",
        view="flat",
    )

    request = route.calls.last.request
    assert request.url.params["localidades"] == "N6[3550308]"
    assert request.url.params["classificacao"] == "2[6794]"
    assert request.url.params["view"] == "flat"
    assert result.params["classificacao"] == "2[6794]"
    assert result.params["view"] == "flat"


@respx.mock
async def test_query_agregado_resposta_vazia_levanta_not_found():
    respx.get(f"{BASE_URL}/6579/periodos/-1/variaveis/99999999").mock(
        return_value=httpx.Response(200, json=[])
    )

    client = AgregadosClient()
    with pytest.raises(IBGENotFoundError):
        await client.query_agregado(
            "6579", variaveis="99999999", localidades="N1[all]", periodos="-1"
        )


@respx.mock
async def test_query_agregado_variavel_invalida_400():
    respx.get(f"{BASE_URL}/6579/periodos/-1/variaveis/abc").mock(return_value=httpx.Response(400))

    client = AgregadosClient()
    with pytest.raises(IBGEValidationError):
        await client.query_agregado("6579", variaveis="abc", localidades="N1[all]", periodos="-1")


@pytest.mark.parametrize(
    ("metodo", "argumentos"),
    [
        ("get_agregado_metadata", ("",)),
        ("get_agregado_periodos", ("  ",)),
        ("get_agregado_variaveis", ("",)),
    ],
)
async def test_metodos_validam_agregado_id_vazio(metodo, argumentos):
    client = AgregadosClient()
    with pytest.raises(IBGEValidationError):
        await getattr(client, metodo)(*argumentos)


async def test_get_agregado_localidades_valida_niveis_vazio():
    client = AgregadosClient()
    with pytest.raises(IBGEValidationError):
        await client.get_agregado_localidades("6579", "")


@pytest.mark.parametrize(
    ("variaveis", "localidades"),
    [
        ("", "N1[all]"),
        ("9324", ""),
    ],
)
async def test_query_agregado_valida_strings_vazias(variaveis, localidades):
    client = AgregadosClient()
    with pytest.raises(IBGEValidationError):
        await client.query_agregado("6579", variaveis=variaveis, localidades=localidades)
