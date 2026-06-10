"""Cliente HTTP assíncrono base, compartilhado por todos os clientes IBGE.

Centraliza timeout, headers, cache opcional e tradução de erros de
rede/HTTP para as exceções de `mcp_ibge.utils.errors`.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

import httpx

from ..config import get_settings
from ..utils.cache import get_cache
from ..utils.errors import (
    IBGEClientError,
    IBGENotFoundError,
    IBGERateLimitError,
    IBGEServerError,
    IBGEValidationError,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class IBGEResult:
    """Resultado de uma chamada a uma API do IBGE, com dados para rastreabilidade.

    Attributes:
        data: Corpo da resposta já decodificado (lista ou dicionário JSON),
            possivelmente filtrado/transformado pelo client ou service.
        endpoint: URL completa do endpoint consultado (sem query string).
        params: Parâmetros relevantes da consulta, usados nos metadados de
            rastreabilidade da resposta da tool.
        raw: Corpo da resposta bruta da API, antes de qualquer filtro local
            (ex.: lista completa de municípios antes da busca por nome).
            `None` quando `data` já corresponde à resposta bruta.
    """

    data: Any
    endpoint: str
    params: dict[str, Any] = field(default_factory=dict)
    raw: Any = None


def _cache_key(url: str, params: dict[str, Any] | None) -> tuple[str, tuple[Any, ...]]:
    normalized = tuple(sorted((params or {}).items()))
    return url, normalized


def _error_for_status(exc: httpx.HTTPStatusError, url: str) -> IBGEClientError:
    status = exc.response.status_code
    message = f"IBGE retornou HTTP {status} para {url}"

    if status == 404:
        return IBGENotFoundError(message, url=url, status_code=status)
    if status in (400, 422):
        return IBGEValidationError(message, url=url, status_code=status)
    if status == 429:
        return IBGERateLimitError(message, url=url, status_code=status)
    if status >= 500:
        return IBGEServerError(message, url=url, status_code=status)
    return IBGEClientError(message, url=url, status_code=status)


class AsyncIBGEClient:
    """Cliente HTTP assíncrono com timeout e cache, parametrizado por um caminho base.

    `base_path` é combinado com `Settings.api_base_url` para formar a URL
    base do cliente (ex.: `base_path="/v1/localidades"`).
    """

    def __init__(self, base_path: str = "") -> None:
        settings = get_settings()
        self.base_url = f"{settings.api_base_url.rstrip('/')}{base_path}"

    async def get_json(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        use_cache: bool = True,
    ) -> Any:
        """Executa um GET em `base_url + path` e retorna o corpo JSON decodificado.

        Levanta uma subclasse de `IBGEClientError` em caso de timeout, erro de
        conexão, status HTTP de erro ou corpo que não seja JSON válido.
        """
        settings = get_settings()
        url = f"{self.base_url}{path}"

        cache = get_cache() if use_cache else None
        key = _cache_key(url, params)
        if cache is not None:
            cached = cache.get(key)
            if cached is not None:
                logger.debug("cache hit: %s params=%s", url, params)
                return cached

        logger.debug("GET %s params=%s", url, params)
        headers = {"User-Agent": settings.user_agent, "Accept": "application/json"}

        max_size = settings.max_response_size_bytes
        try:
            async with httpx.AsyncClient(timeout=settings.timeout, headers=headers) as client:
                async with client.stream("GET", url, params=params) as response:
                    response.raise_for_status()
                    body = bytearray()
                    async for chunk in response.aiter_bytes():
                        body.extend(chunk)
                        if len(body) > max_size:
                            raise IBGEServerError(
                                f"Resposta de {url} excede o limite de {max_size} bytes.",
                                url=url,
                            )
                data = json.loads(body)
        except httpx.TimeoutException as exc:
            raise IBGEClientError(
                f"Tempo limite excedido ({settings.timeout}s) ao consultar {url}", url=url
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise _error_for_status(exc, url) from exc
        except httpx.RequestError as exc:
            raise IBGEClientError(f"Falha de conexão ao consultar {url}: {exc}", url=url) from exc
        except ValueError as exc:
            raise IBGEServerError(f"Resposta inválida (JSON malformado) de {url}", url=url) from exc

        if cache is not None:
            cache.set(key, data)
        return data
