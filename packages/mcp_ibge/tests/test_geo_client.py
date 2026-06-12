"""Testes do cliente "fino" `MalhasClient` (sem regras de negócio)."""

from __future__ import annotations

import httpx
import pytest
import respx

from mcp_ibge.config import get_settings
from mcp_ibge.geo.client import MALHAS_PATH, MalhasClient
from mcp_ibge.utils.errors import IBGENotFoundError, IBGEValidationError

BASE_URL = f"{get_settings().api_base_url}{MALHAS_PATH}"


@respx.mock
async def test_get_malha_municipio(malha_municipio_niteroi):
    respx.get(f"{BASE_URL}/municipios/3303302").mock(
        return_value=httpx.Response(200, json=malha_municipio_niteroi)
    )

    client = MalhasClient()
    result = await client.get_malha_municipio(3303302, "minima")

    assert result.data == malha_municipio_niteroi
    assert result.endpoint == f"{BASE_URL}/municipios/3303302"
    assert result.params == {"codigo_ibge": 3303302, "qualidade": "minima"}


@respx.mock
async def test_get_malha_municipio_envia_formato_e_qualidade(malha_municipio_niteroi):
    route = respx.get(f"{BASE_URL}/municipios/3303302").mock(
        return_value=httpx.Response(200, json=malha_municipio_niteroi)
    )

    client = MalhasClient()
    await client.get_malha_municipio(3303302, "maxima")

    request = route.calls.last.request
    assert request.url.params["formato"] == "application/vnd.geo+json"
    assert request.url.params["qualidade"] == "maxima"


async def test_get_malha_municipio_codigo_invalido_levanta_erro_de_validacao():
    client = MalhasClient()

    with pytest.raises(IBGEValidationError):
        await client.get_malha_municipio(123, "minima")


@respx.mock
async def test_get_malha_municipio_404_levanta_erro():
    respx.get(f"{BASE_URL}/municipios/9999999").mock(
        return_value=httpx.Response(404, json={"detail": "not found"})
    )

    client = MalhasClient()
    with pytest.raises(IBGENotFoundError):
        await client.get_malha_municipio(9999999, "minima")


@respx.mock
async def test_get_malha_uf_por_sigla(malha_uf_rj):
    respx.get(f"{BASE_URL}/estados/RJ").mock(return_value=httpx.Response(200, json=malha_uf_rj))

    client = MalhasClient()
    result = await client.get_malha_uf("rj", "minima")

    assert result.data == malha_uf_rj
    assert result.endpoint == f"{BASE_URL}/estados/RJ"
    assert result.params == {"uf": "RJ", "qualidade": "minima"}


async def test_get_malha_uf_invalida_levanta_erro_de_validacao():
    client = MalhasClient()

    with pytest.raises(IBGEValidationError):
        await client.get_malha_uf("ZZ", "minima")


@respx.mock
async def test_get_malha_uf_usa_cache(malha_uf_rj):
    route = respx.get(f"{BASE_URL}/estados/RJ").mock(
        return_value=httpx.Response(200, json=malha_uf_rj)
    )

    client = MalhasClient()
    await client.get_malha_uf("RJ", "minima")
    await client.get_malha_uf("RJ", "minima")

    assert route.call_count == 1
