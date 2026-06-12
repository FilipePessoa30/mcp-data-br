"""Configuração central do servidor (scaffold).

Segue o mesmo padrão do `mcp-ibge`
(`pydantic-settings`, prefixo de variável de ambiente próprio,
`get_settings()` cacheado) para que o servidor já seja executável — ainda
sem nenhuma *tool* registrada. Veja `docs/modules/inep.md` para o roadmap.

Todos os valores são ajustáveis via variáveis de ambiente com prefixo
``MCP_INEP_`` (ou um arquivo ``.env`` na raiz do projeto).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# Domínios oficiais permitidos para requisições do mcp-inep. Vazio por
# enquanto: nenhum cliente HTTP foi implementado ainda. Será preenchido em
# v0.2, quando as fontes de dados (Censo Escolar, Ideb, ...) forem
# confirmadas — ver "Fontes planejadas" em `docs/modules/inep.md`.
ALLOWED_API_HOSTS: frozenset[str] = frozenset()


class Settings(BaseSettings):
    """Configurações do servidor, lidas de variáveis de ambiente / `.env`."""

    model_config = SettingsConfigDict(env_prefix="MCP_INEP_", env_file=".env", extra="ignore")

    # Logging e transporte do servidor MCP (mesma convenção do mcp-ibge).
    log_level: str = "INFO"
    transport: str = "stdio"

    # Host/porta usados quando `transport` é "streamable-http" (ignorados em
    # "stdio"). Ver `docs/docker.md` para o padrão `0.0.0.0` em containers.
    host: str = "127.0.0.1"
    port: int = 8000


@lru_cache
def get_settings() -> Settings:
    """Retorna a instância (cacheada) de `Settings`."""
    return Settings()
