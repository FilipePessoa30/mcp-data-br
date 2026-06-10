"""Testes da validação de configuração (`mcp_ibge.config.Settings`)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from mcp_ibge.config import Settings


def test_api_base_url_aceita_dominio_oficial():
    settings = Settings(api_base_url="https://servicodados.ibge.gov.br/api")
    assert settings.api_base_url == "https://servicodados.ibge.gov.br/api"


@pytest.mark.parametrize(
    "url",
    [
        "http://servicodados.ibge.gov.br/api",
        "https://evil.example.com/api",
        "https://servicodados.ibge.gov.br.evil.com/api",
        "ftp://servicodados.ibge.gov.br/api",
        "https://localhost/api",
        "not-a-url",
        "",
    ],
)
def test_api_base_url_rejeita_dominios_ou_esquemas_nao_oficiais(url: str):
    with pytest.raises(ValidationError):
        Settings(api_base_url=url)
