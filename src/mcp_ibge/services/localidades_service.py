"""Regras de negócio do domínio de Localidades: filtros, busca e validação.

Esta camada usa `LocalidadesClient` para falar com a API do IBGE e os schemas
de `mcp_ibge.schemas.localidades` para devolver dados limpos, tipados e
rastreáveis (`TypedToolResult`) às tools MCP.
"""

from __future__ import annotations

import difflib
from datetime import UTC, datetime
from typing import Any

from ..clients.localidades import LocalidadesClient
from ..config import get_settings
from ..schemas.common import SourceMetadata, TypedToolResult
from ..schemas.localidades import (
    District,
    Municipality,
    Region,
    State,
    district_from_raw,
    municipality_from_raw,
    region_from_raw,
    state_from_raw,
)
from ..utils.errors import IBGEClientError
from ..utils.normalization import normalize_text


def _metadata(*, endpoint: str, params: dict[str, Any]) -> SourceMetadata:
    return SourceMetadata(
        source_name=get_settings().source_name,
        source_url=endpoint,
        endpoint=endpoint,
        params=params,
        retrieved_at=datetime.now(UTC),
    )


def _selecionar_candidatos(
    nome: str, municipios: list[dict[str, Any]], limite: int
) -> tuple[list[dict[str, Any]], list[str]]:
    """Seleciona candidatos por busca fuzzy: exato -> contém -> similaridade.

    A busca ignora acentos e caixa. Retorna os candidatos (até `limite`) e
    eventuais avisos (ex.: quando há mais de uma correspondência).
    """
    termo = normalize_text(nome)

    exatos = [m for m in municipios if normalize_text(m.get("nome", "")) == termo]
    if exatos:
        candidatos = exatos
    else:
        contidos = [m for m in municipios if termo in normalize_text(m.get("nome", ""))]
        if contidos:
            candidatos = contidos
        else:
            por_nome_normalizado = {normalize_text(m.get("nome", "")): m for m in municipios}
            proximos = difflib.get_close_matches(
                termo, por_nome_normalizado.keys(), n=limite, cutoff=0.6
            )
            candidatos = [por_nome_normalizado[n] for n in proximos]

    warnings: list[str] = []
    if len(candidatos) > 1:
        nomes = ", ".join(m.get("nome", "?") for m in candidatos[:limite])
        warnings.append(
            f'Encontrados {len(candidatos)} municípios para "{nome}": {nomes}. '
            'Refine a busca com "uf" ou um nome mais específico.'
        )

    return candidatos[:limite], warnings


class LocalidadesService:
    """Operações de alto nível sobre regiões, estados, municípios e distritos."""

    def __init__(self, client: LocalidadesClient | None = None) -> None:
        self._client = client or LocalidadesClient()

    async def listar_regioes(self) -> TypedToolResult[list[Region]]:
        """Lista as 5 grandes regiões geográficas do Brasil."""
        result = await self._client.get_regioes()
        regioes = [region_from_raw(item) for item in result.data]
        return TypedToolResult(
            ok=True,
            data=regioes,
            metadata=_metadata(endpoint=result.endpoint, params=result.params),
        )

    async def listar_estados(self) -> TypedToolResult[list[State]]:
        """Lista os 26 estados e o Distrito Federal, ordenados por nome."""
        result = await self._client.get_estados()
        estados = sorted(
            (state_from_raw(item) for item in result.data),
            key=lambda estado: normalize_text(estado.nome),
        )
        return TypedToolResult(
            ok=True,
            data=estados,
            metadata=_metadata(endpoint=result.endpoint, params=result.params),
        )

    async def obter_estado(self, uf: str) -> TypedToolResult[State | None]:
        """Obtém os detalhes de um estado por sigla (ex.: "SP") ou código IBGE."""
        try:
            result = await self._client.get_estado(uf)
        except IBGEClientError as exc:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=_metadata(endpoint=exc.url, params={"uf": uf}),
                errors=[str(exc)],
            )

        return TypedToolResult(
            ok=True,
            data=state_from_raw(result.data),
            metadata=_metadata(endpoint=result.endpoint, params=result.params),
        )

    async def listar_municipios(self, uf: str) -> TypedToolResult[list[Municipality]]:
        """Lista os municípios de uma UF (sigla ou código IBGE)."""
        try:
            result = await self._client.get_municipios_by_uf(uf)
        except IBGEClientError as exc:
            return TypedToolResult(
                ok=False,
                data=[],
                metadata=_metadata(endpoint=exc.url, params={"uf": uf}),
                errors=[str(exc)],
            )

        municipios = [municipality_from_raw(item) for item in result.data]
        return TypedToolResult(
            ok=True,
            data=municipios,
            metadata=_metadata(endpoint=result.endpoint, params=result.params),
        )

    async def buscar_municipio(
        self, nome: str, uf: str | None = None, limite: int = 10
    ) -> TypedToolResult[list[Municipality]]:
        """Busca municípios pelo nome com correspondência aproximada (fuzzy).

        A busca ignora acentos e caixa, e tenta nesta ordem: correspondência
        exata, depois "contém" e, por fim, similaridade textual (`difflib`).
        Quando há mais de uma correspondência, um aviso é incluído em
        `warnings` pedindo para refinar a busca (ex.: informando `uf`).
        """
        params: dict[str, Any] = {"nome": nome, "limite": limite}
        if uf:
            params["uf"] = uf

        try:
            result = (
                await self._client.get_municipios_by_uf(uf)
                if uf
                else await self._client.get_municipios()
            )
        except IBGEClientError as exc:
            return TypedToolResult(
                ok=False,
                data=[],
                metadata=_metadata(endpoint=exc.url, params=params),
                errors=[str(exc)],
            )

        candidatos_raw, warnings = _selecionar_candidatos(nome, result.data, limite)
        municipios = [municipality_from_raw(item) for item in candidatos_raw]

        return TypedToolResult(
            ok=True,
            data=municipios,
            metadata=_metadata(endpoint=result.endpoint, params=params),
            warnings=warnings,
        )

    async def obter_codigo_municipio(self, nome: str, uf: str) -> TypedToolResult[int | None]:
        """Obtém o código IBGE de 7 dígitos de um município pelo nome e UF."""
        busca = await self.buscar_municipio(nome, uf=uf, limite=5)

        if not busca.ok:
            return TypedToolResult(
                ok=False, data=None, metadata=busca.metadata, errors=busca.errors
            )

        if not busca.data:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=busca.metadata,
                errors=[f'Nenhum município encontrado para "{nome}" na UF "{uf}".'],
            )

        if len(busca.data) > 1:
            return TypedToolResult(
                ok=False, data=None, metadata=busca.metadata, warnings=busca.warnings
            )

        return TypedToolResult(ok=True, data=busca.data[0].id, metadata=busca.metadata)

    async def obter_municipio_por_codigo(
        self, codigo_ibge: int
    ) -> TypedToolResult[Municipality | None]:
        """Obtém um município pelo código IBGE, com UF e região resolvidas."""
        try:
            result = await self._client.get_municipio(codigo_ibge)
        except IBGEClientError as exc:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=_metadata(endpoint=exc.url, params={"municipio_id": codigo_ibge}),
                errors=[str(exc)],
            )

        return TypedToolResult(
            ok=True,
            data=municipality_from_raw(result.data),
            metadata=_metadata(endpoint=result.endpoint, params=result.params),
        )

    async def listar_distritos(self, codigo_municipio: int) -> TypedToolResult[list[District]]:
        """Lista os distritos de um município pelo código IBGE."""
        try:
            result = await self._client.get_distritos_by_municipio(codigo_municipio)
        except IBGEClientError as exc:
            return TypedToolResult(
                ok=False,
                data=[],
                metadata=_metadata(endpoint=exc.url, params={"municipio_id": codigo_municipio}),
                errors=[str(exc)],
            )

        distritos = [district_from_raw(item) for item in result.data]
        return TypedToolResult(
            ok=True,
            data=distritos,
            metadata=_metadata(endpoint=result.endpoint, params=result.params),
        )
