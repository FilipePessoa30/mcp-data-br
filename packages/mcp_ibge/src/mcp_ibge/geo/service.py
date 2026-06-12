"""Regras de negócio do módulo geoespacial (`mcp_ibge.geo`).

Consulta malhas geográficas (municípios e UFs) e bounding boxes a partir da
API de Malhas do IBGE, sempre em GeoJSON
(https://servicodados.ibge.gov.br/api/docs/malhas).

Por padrão (`simplificado=True`) usa a qualidade "minima" da malha, que
reduz bastante o tamanho da resposta às custas de uma geometria menos
detalhada — nesse caso, a resposta inclui um aviso em `warnings` informando
que a geometria foi simplificada. `gerar_geojson_municipios` sempre usa a
malha simplificada (e sempre avisa), para manter a resposta combinada de
vários municípios dentro do limite de tamanho configurado em
`Settings.max_response_size_bytes`.
"""

from __future__ import annotations

from typing import Any

from ..schemas.common import SourceMetadata, TypedToolResult, build_metadata
from .client import MalhasClient
from .schemas import (
    GEOJSON_TYPES,
    QUALIDADE_COMPLETA,
    QUALIDADE_SIMPLIFICADA,
    BBox,
    GeoJSONMunicipios,
    MunicipioGeoNaoResolvido,
)

# Número máximo de municípios por chamada de `gerar_geojson_municipios`, para
# limitar o número de requisições e o tamanho da resposta combinada.
MAX_MUNICIPIOS_GEOJSON = 10

# Nível territorial IBGE (ver `metadata.territorial_level`).
_NIVEL_MUNICIPIO = "N6"
_NIVEL_UF = "N3"

_AVISO_SIMPLIFICADO = (
    'Geometria simplificada (qualidade "minima" da malha do IBGE): adequada '
    "para visualização em mapas, mas não para análises que exigem precisão "
    "geométrica/cartográfica."
)


def is_valid_geojson(value: Any) -> bool:
    """`True` se `value` é um objeto GeoJSON minimamente válido (RFC 7946)."""
    return isinstance(value, dict) and value.get("type") in GEOJSON_TYPES


def _extrair_geometria(malha: Any) -> dict[str, Any] | None:
    """Extrai uma geometria GeoJSON de uma malha (`FeatureCollection`, `Feature` ou geometria)."""
    if not isinstance(malha, dict):
        return None

    tipo = malha.get("type")
    if tipo == "FeatureCollection":
        features = malha.get("features") or []
        if not features:
            return None
        return _extrair_geometria(features[0])
    if tipo == "Feature":
        geometria = malha.get("geometry")
        return geometria if isinstance(geometria, dict) else None
    if tipo in GEOJSON_TYPES:
        return malha
    return None


def _coordenadas(geometria: dict[str, Any] | None) -> list[Any]:
    if geometria is None:
        return []
    if geometria.get("type") == "GeometryCollection":
        coordenadas: list[Any] = []
        for sub_geometria in geometria.get("geometries") or []:
            coordenadas.extend(_coordenadas(sub_geometria))
        return coordenadas
    return geometria.get("coordinates") or []


def _achatar_pontos(coordenadas: Any) -> list[tuple[float, float]]:
    """Achata recursivamente um `coordinates` do GeoJSON em pontos `(longitude, latitude)`."""
    if not coordenadas:
        return []

    primeiro = coordenadas[0]
    if isinstance(primeiro, int | float):
        # `coordenadas` já é um ponto `[lon, lat, ...]` (altitude/medida ignoradas).
        return [(float(coordenadas[0]), float(coordenadas[1]))]

    pontos: list[tuple[float, float]] = []
    for item in coordenadas:
        pontos.extend(_achatar_pontos(item))
    return pontos


def calcular_bbox(malha: Any) -> BBox | None:
    """Calcula o bounding box (WGS84) de uma malha GeoJSON, ou `None` se vazia/inválida."""
    pontos = _achatar_pontos(_coordenadas(_extrair_geometria(malha)))
    if not pontos:
        return None

    longitudes = [ponto[0] for ponto in pontos]
    latitudes = [ponto[1] for ponto in pontos]
    return BBox(
        min_longitude=min(longitudes),
        min_latitude=min(latitudes),
        max_longitude=max(longitudes),
        max_latitude=max(latitudes),
    )


class GeoService:
    """Consultas geoespaciais (malhas e bounding boxes) baseadas na API de Malhas do IBGE."""

    def __init__(self, client: MalhasClient | None = None) -> None:
        self._client = client or MalhasClient()

    async def obter_malha_municipio(
        self, codigo_ibge: int, simplificado: bool = True
    ) -> TypedToolResult[dict[str, Any] | None]:
        """Malha (GeoJSON) de um município pelo código IBGE."""
        qualidade = QUALIDADE_SIMPLIFICADA if simplificado else QUALIDADE_COMPLETA
        result = await self._client.get_malha_municipio(codigo_ibge, qualidade)
        metadata = build_metadata(
            source_url=result.endpoint,
            endpoint=result.endpoint,
            params=result.params,
            territorial_level=_NIVEL_MUNICIPIO,
            cache_hit=result.cache_hit,
        )

        if not is_valid_geojson(result.data):
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=metadata,
                errors=[f"A malha do município {codigo_ibge} não retornou um GeoJSON válido."],
            )

        warnings = [_AVISO_SIMPLIFICADO] if simplificado else []
        return TypedToolResult(ok=True, data=result.data, metadata=metadata, warnings=warnings)

    async def obter_malha_uf(
        self, uf: str, simplificado: bool = True
    ) -> TypedToolResult[dict[str, Any] | None]:
        """Malha (GeoJSON) de uma UF pela sigla ou código IBGE."""
        qualidade = QUALIDADE_SIMPLIFICADA if simplificado else QUALIDADE_COMPLETA
        result = await self._client.get_malha_uf(uf, qualidade)
        metadata = build_metadata(
            source_url=result.endpoint,
            endpoint=result.endpoint,
            params=result.params,
            territorial_level=_NIVEL_UF,
            cache_hit=result.cache_hit,
        )

        if not is_valid_geojson(result.data):
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=metadata,
                errors=[f'A malha da UF "{uf}" não retornou um GeoJSON válido.'],
            )

        warnings = [_AVISO_SIMPLIFICADO] if simplificado else []
        return TypedToolResult(ok=True, data=result.data, metadata=metadata, warnings=warnings)

    async def obter_bbox_municipio(
        self, codigo_ibge: int
    ) -> TypedToolResult[dict[str, Any] | None]:
        """Bounding box (WGS84) de um município, calculado a partir da malha simplificada."""
        result = await self._client.get_malha_municipio(codigo_ibge, QUALIDADE_SIMPLIFICADA)
        metadata = build_metadata(
            source_url=result.endpoint,
            endpoint=result.endpoint,
            params=result.params,
            territorial_level=_NIVEL_MUNICIPIO,
            cache_hit=result.cache_hit,
        )

        bbox = calcular_bbox(result.data)
        if bbox is None:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=metadata,
                errors=[
                    f"Não foi possível calcular o bounding box do município {codigo_ibge}: "
                    "a malha retornada não contém geometria válida."
                ],
            )

        dados = bbox.model_dump(mode="json")
        dados["bbox"] = bbox.as_geojson_bbox()
        return TypedToolResult(
            ok=True, data=dados, metadata=metadata, warnings=[_AVISO_SIMPLIFICADO]
        )

    async def gerar_geojson_municipios(
        self, codigos_ibge: list[int]
    ) -> TypedToolResult[GeoJSONMunicipios | None]:
        """`FeatureCollection` GeoJSON com a malha simplificada de cada município informado."""
        if not codigos_ibge:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=build_metadata(source_url="", endpoint=""),
                errors=['Informe ao menos um código IBGE em "codigos_ibge".'],
            )

        if len(codigos_ibge) > MAX_MUNICIPIOS_GEOJSON:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=build_metadata(source_url="", endpoint=""),
                errors=[
                    f"No máximo {MAX_MUNICIPIOS_GEOJSON} municípios por chamada "
                    f"(recebidos {len(codigos_ibge)})."
                ],
            )

        features: list[dict[str, Any]] = []
        nao_resolvidos: list[MunicipioGeoNaoResolvido] = []
        warnings: list[str] = [_AVISO_SIMPLIFICADO]
        endpoints: list[str] = []
        metadata_referencia: SourceMetadata | None = None
        cache_hit = True

        for codigo in codigos_ibge:
            result = await self._client.get_malha_municipio(codigo, QUALIDADE_SIMPLIFICADA)
            if result.endpoint not in endpoints:
                endpoints.append(result.endpoint)
            cache_hit = cache_hit and result.cache_hit
            if metadata_referencia is None:
                metadata_referencia = build_metadata(
                    source_url=result.endpoint,
                    endpoint=result.endpoint,
                    params=result.params,
                    territorial_level=_NIVEL_MUNICIPIO,
                    cache_hit=result.cache_hit,
                )

            geometria = _extrair_geometria(result.data)
            if geometria is None:
                nao_resolvidos.append(
                    MunicipioGeoNaoResolvido(
                        codigo_ibge=codigo,
                        motivo="A malha retornada não contém geometria válida.",
                    )
                )
                continue

            features.append(
                {"type": "Feature", "properties": {"codigo_ibge": codigo}, "geometry": geometria}
            )

        metadata_base = metadata_referencia or build_metadata(source_url="", endpoint="")

        if not features:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=metadata_base,
                warnings=warnings,
                errors=["Nenhum dos códigos IBGE informados pôde ser resolvido."],
            )

        geojson = GeoJSONMunicipios(features=features, codigos_nao_resolvidos=nao_resolvidos)

        if nao_resolvidos:
            warnings.append(
                "Códigos IBGE sem malha válida (ver `data.codigos_nao_resolvidos`): "
                + ", ".join(str(item.codigo_ibge) for item in nao_resolvidos)
            )

        metadata = metadata_base.model_copy(
            update={
                "params": {"codigos_ibge": codigos_ibge, "endpoints": endpoints},
                "cache_hit": cache_hit,
            }
        )

        return TypedToolResult(ok=True, data=geojson, metadata=metadata, warnings=warnings)
