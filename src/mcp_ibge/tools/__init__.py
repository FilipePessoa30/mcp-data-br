"""Tools FastMCP: convertem chamadas de serviço no envelope padrão de resposta.

Cada submódulo (`localidades_tools`, `agregados_tools`, ...) expõe uma função
`register(mcp)` que registra suas tools na instância `FastMCP` do servidor.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable
from typing import Any

from pydantic import BaseModel

from ..clients.base import IBGEResult
from ..schemas.common import TypedToolResult, build_error_response, build_response
from ..utils.errors import IBGEClientError

logger = logging.getLogger(__name__)


async def run_tool(
    call: Awaitable[IBGEResult],
    *,
    endpoint: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Executa uma chamada de serviço e converte o resultado no envelope padrão.

    Em caso de sucesso retorna `{"metadata": {...}, "data": ...}`; em caso de
    erro (de rede/HTTP ou inesperado) retorna `{"metadata": {...}, "error": "..."}`.
    """
    try:
        result = await call
    except IBGEClientError as exc:
        logger.warning("Erro ao consultar %s: %s", exc.url, exc)
        return build_error_response(
            source_url=exc.url, endpoint=exc.url, params=params, error=str(exc)
        )
    except Exception as exc:  # pragma: no cover - rede de segurança
        logger.exception("Erro inesperado ao consultar %s", endpoint)
        return build_error_response(
            source_url=endpoint,
            endpoint=endpoint,
            params=params,
            error=f"Erro inesperado: {exc}",
        )

    return build_response(
        source_url=result.endpoint,
        endpoint=result.endpoint,
        params=result.params,
        data=result.data,
    )


def _dump(value: Any) -> Any:
    """Converte (recursivamente) modelos Pydantic em estruturas JSON simples."""
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_dump(item) for item in value]
    return value


async def run_typed_tool(call: Awaitable[TypedToolResult[Any]]) -> dict[str, Any]:
    """Executa uma chamada de serviço que retorna `TypedToolResult` e converte
    o resultado no envelope padrão de resposta.

    Em caso de sucesso (`ok=True`) retorna `{"metadata": ..., "data": ...}`,
    incluindo `"warnings"` quando houver. Em caso de falha (`ok=False` ou
    exceção inesperada) retorna `{"metadata": ..., "error": "..."}`.
    """
    try:
        result = await call
    except Exception as exc:  # pragma: no cover - rede de segurança
        logger.exception("Erro inesperado ao executar tool tipada")
        return build_error_response(
            source_url="", endpoint="", params={}, error=f"Erro inesperado: {exc}"
        )

    metadata = result.metadata

    if not result.ok:
        error = "; ".join(result.errors or result.warnings) or "Erro desconhecido"
        logger.warning("Erro ao consultar %s: %s", metadata.endpoint, error)
        return build_error_response(
            source_url=metadata.source_url,
            endpoint=metadata.endpoint,
            params=metadata.params,
            error=error,
        )

    response = build_response(
        source_url=metadata.source_url,
        endpoint=metadata.endpoint,
        params=metadata.params,
        data=_dump(result.data),
    )
    if result.warnings:
        response["warnings"] = result.warnings
    return response
