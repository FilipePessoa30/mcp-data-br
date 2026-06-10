"""Testes do cliente "fino" `LocalidadesClient` (sem regras de negócio)."""

from __future__ import annotations

import httpx
import pytest
import respx

from mcp_ibge.clients.localidades import LOCALIDADES_PATH, LocalidadesClient
from mcp_ibge.config import get_settings
from mcp_ibge.utils.errors import IBGENotFoundError, IBGEValidationError

BASE_URL = f"{get_settings().api_base_url}{LOCALIDADES_PATH}"

REGIOES = [
    {"id": 1, "sigla": "N", "nome": "Norte"},
    {"id": 2, "sigla": "NE", "nome": "Nordeste"},
]

ESTADOS = [
    {
        "id": 35,
        "sigla": "SP",
        "nome": "São Paulo",
        "regiao": {"id": 3, "sigla": "SE", "nome": "Sudeste"},
    },
]

MUNICIPIOS_SP = [
    {"id": 3550308, "nome": "São Paulo"},
    {"id": 3548807, "nome": "São José dos Campos"},
]

MUNICIPIOS_BRASIL = [
    *MUNICIPIOS_SP,
    {"id": 4205407, "nome": "Florianópolis"},
]

DISTRITOS_SP = [
    {
        "id": 355030801,
        "nome": "Sé",
        "municipio": {"id": 3550308, "nome": "São Paulo"},
    },
]


@respx.mock
async def test_get_regioes():
    respx.get(f"{BASE_URL}/regioes").mock(return_value=httpx.Response(200, json=REGIOES))

    client = LocalidadesClient()
    result = await client.get_regioes()

    assert result.data == REGIOES
    assert result.endpoint == f"{BASE_URL}/regioes"
    assert result.params == {}


@respx.mock
async def test_get_estados():
    respx.get(f"{BASE_URL}/estados").mock(return_value=httpx.Response(200, json=ESTADOS))

    client = LocalidadesClient()
    result = await client.get_estados()

    assert result.data == ESTADOS
    assert result.endpoint == f"{BASE_URL}/estados"


@respx.mock
async def test_get_estado_por_sigla():
    respx.get(f"{BASE_URL}/estados/SP").mock(return_value=httpx.Response(200, json=ESTADOS[0]))

    client = LocalidadesClient()
    result = await client.get_estado("sp")

    assert result.data == ESTADOS[0]
    assert result.params == {"uf": "sp"}


@respx.mock
async def test_get_estado_por_codigo_numerico():
    respx.get(f"{BASE_URL}/estados/35").mock(return_value=httpx.Response(200, json=ESTADOS[0]))

    client = LocalidadesClient()
    result = await client.get_estado("35")

    assert result.data == ESTADOS[0]
    assert result.params == {"uf": "35"}


async def test_get_estado_uf_invalida_levanta_erro_de_validacao():
    client = LocalidadesClient()

    with pytest.raises(IBGEValidationError):
        await client.get_estado("XX")


@respx.mock
async def test_get_municipios_by_uf():
    respx.get(f"{BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=MUNICIPIOS_SP)
    )

    client = LocalidadesClient()
    result = await client.get_municipios_by_uf("SP")

    assert result.data == MUNICIPIOS_SP
    assert result.params == {"uf": "SP"}


async def test_get_municipios_by_uf_uf_invalida_levanta_erro_de_validacao():
    client = LocalidadesClient()

    with pytest.raises(IBGEValidationError):
        await client.get_municipios_by_uf("ZZ")


@respx.mock
async def test_get_municipios_brasil_inteiro():
    respx.get(f"{BASE_URL}/municipios").mock(
        return_value=httpx.Response(200, json=MUNICIPIOS_BRASIL)
    )

    client = LocalidadesClient()
    result = await client.get_municipios()

    assert result.data == MUNICIPIOS_BRASIL
    assert result.endpoint == f"{BASE_URL}/municipios"
    assert result.params == {}


@respx.mock
async def test_get_municipio():
    municipio = {"id": 3550308, "nome": "São Paulo"}
    respx.get(f"{BASE_URL}/municipios/3550308").mock(
        return_value=httpx.Response(200, json=municipio)
    )

    client = LocalidadesClient()
    result = await client.get_municipio(3550308)

    assert result.data == municipio
    assert result.params == {"municipio_id": 3550308}


@respx.mock
async def test_get_municipio_404_levanta_erro():
    respx.get(f"{BASE_URL}/municipios/9999999").mock(
        return_value=httpx.Response(404, json={"detail": "not found"})
    )

    client = LocalidadesClient()
    with pytest.raises(IBGENotFoundError) as exc_info:
        await client.get_municipio(9999999)

    assert exc_info.value.status_code == 404


@respx.mock
async def test_search_municipios_ignora_acentos_e_caixa():
    respx.get(f"{BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=MUNICIPIOS_SP)
    )

    client = LocalidadesClient()
    result = await client.search_municipios("sao jose", uf="SP")

    assert [m["nome"] for m in result.data] == ["São José dos Campos"]
    assert result.params == {"nome": "sao jose", "uf": "SP"}
    assert result.raw == MUNICIPIOS_SP


@respx.mock
async def test_search_municipios_sem_uf_busca_brasil_inteiro():
    respx.get(f"{BASE_URL}/municipios").mock(
        return_value=httpx.Response(200, json=MUNICIPIOS_BRASIL)
    )

    client = LocalidadesClient()
    result = await client.search_municipios("florianopolis")

    assert [m["nome"] for m in result.data] == ["Florianópolis"]
    assert result.params == {"nome": "florianopolis"}
    assert result.raw == MUNICIPIOS_BRASIL


@respx.mock
async def test_search_municipios_sem_correspondencia_retorna_lista_vazia():
    respx.get(f"{BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=MUNICIPIOS_SP)
    )

    client = LocalidadesClient()
    result = await client.search_municipios("Curitiba", uf="SP")

    assert result.data == []
    assert result.raw == MUNICIPIOS_SP


@respx.mock
async def test_get_distritos_by_municipio():
    respx.get(f"{BASE_URL}/municipios/3550308/distritos").mock(
        return_value=httpx.Response(200, json=DISTRITOS_SP)
    )

    client = LocalidadesClient()
    result = await client.get_distritos_by_municipio(3550308)

    assert result.data == DISTRITOS_SP
    assert result.params == {"municipio_id": 3550308}


@respx.mock
async def test_get_json_usa_cache():
    route = respx.get(f"{BASE_URL}/regioes").mock(return_value=httpx.Response(200, json=REGIOES))

    client = LocalidadesClient()
    await client.get_regioes()
    await client.get_regioes()

    assert route.call_count == 1
