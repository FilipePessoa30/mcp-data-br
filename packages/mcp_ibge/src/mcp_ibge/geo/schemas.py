"""Schemas Pydantic do módulo geoespacial (`mcp_ibge.geo`).

Define os tipos usados por `obter_malha_municipio`, `obter_malha_uf`,
`obter_bbox_municipio` e `gerar_geojson_municipios`. As malhas em si são
devolvidas como GeoJSON (`dict[str, Any]`), validado por `GEOJSON_TYPES`
(ver `service.is_valid_geojson`); os modelos abaixo cobrem o bounding box e o
agrupamento de municípios não resolvidos em `gerar_geojson_municipios`.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

# Valores aceitos pelo parâmetro `qualidade` da API de Malhas do IBGE
# (https://servicodados.ibge.gov.br/api/docs/malhas). "minima" produz a
# geometria mais simplificada (resposta bem menor); "maxima" produz a
# geometria mais detalhada (resposta maior, podendo atingir o limite de
# tamanho configurado em `Settings.max_response_size_bytes`).
QUALIDADE_SIMPLIFICADA = "minima"
QUALIDADE_COMPLETA = "maxima"

# Tipos de objeto GeoJSON aceitos como retorno válido (RFC 7946).
GEOJSON_TYPES: frozenset[str] = frozenset(
    {
        "FeatureCollection",
        "Feature",
        "Point",
        "MultiPoint",
        "LineString",
        "MultiLineString",
        "Polygon",
        "MultiPolygon",
        "GeometryCollection",
    }
)


class BBox(BaseModel):
    """Bounding box de uma geometria, em graus decimais (WGS84)."""

    min_longitude: float
    min_latitude: float
    max_longitude: float
    max_latitude: float

    def as_geojson_bbox(self) -> list[float]:
        """Representação no formato `bbox` do GeoJSON: `[west, south, east, north]`."""
        return [self.min_longitude, self.min_latitude, self.max_longitude, self.max_latitude]


class MunicipioGeoNaoResolvido(BaseModel):
    """Município cujo código IBGE não retornou uma malha válida."""

    codigo_ibge: int
    motivo: str


class GeoJSONMunicipios(BaseModel):
    """`FeatureCollection` GeoJSON com a malha de cada município resolvido.

    `codigos_nao_resolvidos` é um membro adicional (permitido pelo GeoJSON
    como "foreign member") com os códigos IBGE cuja malha não pôde ser
    obtida, e o respectivo motivo.
    """

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[dict[str, Any]] = Field(default_factory=list)
    codigos_nao_resolvidos: list[MunicipioGeoNaoResolvido] = Field(default_factory=list)
