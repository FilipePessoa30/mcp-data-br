"""Configuração central do servidor: URLs base, timeouts, cache e transporte.

Todos os valores são ajustáveis via variáveis de ambiente com prefixo
``MCP_IBGE_`` (ou um arquivo ``.env`` na raiz do projeto — veja
``.env.example``), o que permite customizar o comportamento sem alterar
código (ex.: ao rodar via Claude Desktop, Cursor ou Docker).
"""

from __future__ import annotations

from functools import lru_cache
from urllib.parse import urlparse

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Domínios oficiais do IBGE para os quais o servidor pode enviar requisições.
# `MCP_IBGE_API_BASE_URL` é validado contra esta lista — qualquer outro
# domínio (ou esquema diferente de "https") é rejeitado na inicialização.
ALLOWED_API_HOSTS: frozenset[str] = frozenset({"servicodados.ibge.gov.br"})


class Settings(BaseSettings):
    """Configurações do servidor, lidas de variáveis de ambiente / `.env`."""

    model_config = SettingsConfigDict(env_prefix="MCP_IBGE_", env_file=".env", extra="ignore")

    # URL base comum às APIs públicas do IBGE (sem necessidade de chave de API).
    # Cada cliente de domínio acrescenta seu próprio prefixo de versão/recurso
    # (ex.: "/v1/localidades", "/v3/agregados"). Restrita a `ALLOWED_API_HOSTS`.
    api_base_url: str = "https://servicodados.ibge.gov.br/api"

    # Identificação usada nos metadados de rastreabilidade e no header User-Agent.
    source_name: str = "IBGE - Instituto Brasileiro de Geografia e Estatística"
    user_agent: str = "mcp-ibge/0.1.0"

    # Timeout (em segundos) aplicado a cada requisição HTTP às APIs do IBGE.
    timeout: float = 30.0

    # Tamanho máximo (em bytes) aceito para o corpo de uma resposta da API do
    # IBGE. Respostas maiores são abortadas e tratadas como erro de servidor.
    max_response_size_bytes: int = 5_000_000

    # Cache simples em memória (TTL) para reduzir chamadas repetidas às APIs.
    cache_enabled: bool = True
    cache_ttl_seconds: float = 3600.0
    cache_max_size: int = 256

    # Logging e transporte do servidor MCP.
    log_level: str = "INFO"
    transport: str = "stdio"

    # Porta usada quando `transport` é "streamable-http" (ignorada em "stdio").
    port: int = 8000

    @field_validator("api_base_url")
    @classmethod
    def _validar_api_base_url(cls, value: str) -> str:
        """Garante que `api_base_url` aponta para um domínio oficial do IBGE via HTTPS."""
        parsed = urlparse(value)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_API_HOSTS:
            dominios = ", ".join(sorted(ALLOWED_API_HOSTS))
            raise ValueError(
                f'MCP_IBGE_API_BASE_URL inválida: "{value}". Deve ser uma URL '
                f"https para um domínio oficial do IBGE ({dominios})."
            )
        return value


@lru_cache
def get_settings() -> Settings:
    """Retorna a instância (única, em cache) das configurações do servidor."""
    return Settings()
