"""Testes da hierarquia de exceções e do tratamento de erros do AsyncIBGEClient."""

from __future__ import annotations

import httpx
import pytest
import respx

from mcp_ibge.clients.base import AsyncIBGEClient
from mcp_ibge.config import get_settings
from mcp_ibge.utils.errors import (
    IBGEClientError,
    IBGENotFoundError,
    IBGERateLimitError,
    IBGEServerError,
    IBGEValidationError,
)

BASE_URL = get_settings().api_base_url


@respx.mock
async def test_404_levanta_not_found_error():
    respx.get(f"{BASE_URL}/teste").mock(return_value=httpx.Response(404))

    client = AsyncIBGEClient()
    with pytest.raises(IBGENotFoundError) as exc_info:
        await client.get_json("/teste")

    assert isinstance(exc_info.value, IBGEClientError)
    assert exc_info.value.status_code == 404
    assert exc_info.value.url == f"{BASE_URL}/teste"


@respx.mock
@pytest.mark.parametrize("status_code", [400, 422])
async def test_400_e_422_levantam_validation_error(status_code: int):
    respx.get(f"{BASE_URL}/teste").mock(return_value=httpx.Response(status_code))

    client = AsyncIBGEClient()
    with pytest.raises(IBGEValidationError) as exc_info:
        await client.get_json("/teste")

    assert exc_info.value.status_code == status_code


@respx.mock
async def test_429_levanta_rate_limit_error():
    respx.get(f"{BASE_URL}/teste").mock(return_value=httpx.Response(429))

    client = AsyncIBGEClient()
    with pytest.raises(IBGERateLimitError) as exc_info:
        await client.get_json("/teste")

    assert exc_info.value.status_code == 429


@respx.mock
async def test_503_levanta_server_error():
    respx.get(f"{BASE_URL}/teste").mock(return_value=httpx.Response(503))

    client = AsyncIBGEClient()
    with pytest.raises(IBGEServerError) as exc_info:
        await client.get_json("/teste")

    assert exc_info.value.status_code == 503


@respx.mock
async def test_json_invalido_levanta_server_error():
    respx.get(f"{BASE_URL}/teste").mock(return_value=httpx.Response(200, content=b"nao e json"))

    client = AsyncIBGEClient()
    with pytest.raises(IBGEServerError) as exc_info:
        await client.get_json("/teste")

    assert exc_info.value.status_code is None


@respx.mock
async def test_timeout_levanta_client_error():
    respx.get(f"{BASE_URL}/teste").mock(side_effect=httpx.TimeoutException("timeout"))

    client = AsyncIBGEClient()
    with pytest.raises(IBGEClientError) as exc_info:
        await client.get_json("/teste")

    assert exc_info.value.status_code is None


@respx.mock
async def test_erro_de_conexao_levanta_client_error():
    respx.get(f"{BASE_URL}/teste").mock(side_effect=httpx.ConnectError("falha de conexão"))

    client = AsyncIBGEClient()
    with pytest.raises(IBGEClientError):
        await client.get_json("/teste")


@respx.mock
async def test_resposta_acima_do_limite_levanta_server_error(monkeypatch):
    settings = get_settings().model_copy(update={"max_response_size_bytes": 10})
    monkeypatch.setattr("mcp_ibge.clients.base.get_settings", lambda: settings)

    respx.get(f"{BASE_URL}/teste").mock(return_value=httpx.Response(200, json={"dados": "x" * 100}))

    client = AsyncIBGEClient()
    with pytest.raises(IBGEServerError) as exc_info:
        await client.get_json("/teste")

    assert exc_info.value.status_code is None
