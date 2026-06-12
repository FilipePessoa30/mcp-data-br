"""Testes da camada de serviço `GeoService` (malhas geográficas e bounding boxes)."""

from __future__ import annotations

import httpx
import respx

from mcp_ibge.config import get_settings
from mcp_ibge.geo.client import MALHAS_PATH
from mcp_ibge.geo.service import (
    MAX_MUNICIPIOS_GEOJSON,
    GeoService,
    calcular_bbox,
    is_valid_geojson,
)

BASE_URL = f"{get_settings().api_base_url}{MALHAS_PATH}"


@respx.mock
async def test_obter_malha_municipio_simplificado_retorna_warning(malha_municipio_niteroi):
    respx.get(f"{BASE_URL}/municipios/3303302").mock(
        return_value=httpx.Response(200, json=malha_municipio_niteroi)
    )

    result = await GeoService().obter_malha_municipio(3303302)

    assert result.ok is True
    assert result.data == malha_municipio_niteroi
    assert result.warnings
    assert "simplificada" in result.warnings[0]
    assert result.metadata.territorial_level == "N6"
    assert result.metadata.params == {"codigo_ibge": 3303302, "qualidade": "minima"}


@respx.mock
async def test_obter_malha_municipio_nao_simplificado_sem_warning(malha_municipio_niteroi):
    respx.get(f"{BASE_URL}/municipios/3303302").mock(
        return_value=httpx.Response(200, json=malha_municipio_niteroi)
    )

    result = await GeoService().obter_malha_municipio(3303302, simplificado=False)

    assert result.ok is True
    assert result.warnings == []
    assert result.metadata.params["qualidade"] == "maxima"


@respx.mock
async def test_obter_malha_municipio_resposta_invalida_retorna_erro():
    respx.get(f"{BASE_URL}/municipios/3303302").mock(
        return_value=httpx.Response(200, json={"erro": "sem malha"})
    )

    result = await GeoService().obter_malha_municipio(3303302)

    assert result.ok is False
    assert result.data is None
    assert result.errors


@respx.mock
async def test_obter_malha_uf_simplificado_retorna_warning(malha_uf_rj):
    respx.get(f"{BASE_URL}/estados/RJ").mock(return_value=httpx.Response(200, json=malha_uf_rj))

    result = await GeoService().obter_malha_uf("RJ")

    assert result.ok is True
    assert result.data == malha_uf_rj
    assert result.warnings
    assert result.metadata.territorial_level == "N3"


@respx.mock
async def test_obter_malha_uf_resposta_invalida_retorna_erro():
    respx.get(f"{BASE_URL}/estados/RJ").mock(return_value=httpx.Response(200, json=[]))

    result = await GeoService().obter_malha_uf("RJ")

    assert result.ok is False
    assert result.data is None
    assert result.errors


@respx.mock
async def test_obter_bbox_municipio(malha_municipio_niteroi):
    respx.get(f"{BASE_URL}/municipios/3303302").mock(
        return_value=httpx.Response(200, json=malha_municipio_niteroi)
    )

    result = await GeoService().obter_bbox_municipio(3303302)

    assert result.ok is True
    assert result.data["min_longitude"] == -43.13
    assert result.data["max_longitude"] == -43.05
    assert result.data["min_latitude"] == -22.92
    assert result.data["max_latitude"] == -22.86
    assert result.data["bbox"] == [-43.13, -22.92, -43.05, -22.86]
    assert result.warnings


@respx.mock
async def test_obter_bbox_municipio_sem_geometria_retorna_erro():
    respx.get(f"{BASE_URL}/municipios/3303302").mock(
        return_value=httpx.Response(200, json={"type": "FeatureCollection", "features": []})
    )

    result = await GeoService().obter_bbox_municipio(3303302)

    assert result.ok is False
    assert result.data is None
    assert result.errors


@respx.mock
async def test_gerar_geojson_municipios(malha_municipio_niteroi):
    respx.get(f"{BASE_URL}/municipios/3303302").mock(
        return_value=httpx.Response(200, json=malha_municipio_niteroi)
    )

    result = await GeoService().gerar_geojson_municipios([3303302])

    assert result.ok is True
    assert result.data.type == "FeatureCollection"
    assert len(result.data.features) == 1
    assert result.data.features[0]["properties"]["codigo_ibge"] == 3303302
    assert result.data.codigos_nao_resolvidos == []
    assert result.warnings


@respx.mock
async def test_gerar_geojson_municipios_codigo_sem_malha_valida_e_listado(malha_municipio_niteroi):
    respx.get(f"{BASE_URL}/municipios/3303302").mock(
        return_value=httpx.Response(200, json=malha_municipio_niteroi)
    )
    respx.get(f"{BASE_URL}/municipios/3304557").mock(
        return_value=httpx.Response(200, json={"erro": "sem malha"})
    )

    result = await GeoService().gerar_geojson_municipios([3303302, 3304557])

    assert result.ok is True
    assert len(result.data.features) == 1
    assert result.data.features[0]["properties"]["codigo_ibge"] == 3303302
    assert [item.codigo_ibge for item in result.data.codigos_nao_resolvidos] == [3304557]
    assert any("3304557" in aviso for aviso in result.warnings)


async def test_gerar_geojson_municipios_lista_vazia_retorna_erro():
    result = await GeoService().gerar_geojson_municipios([])

    assert result.ok is False
    assert result.data is None
    assert result.errors


async def test_gerar_geojson_municipios_acima_do_limite_retorna_erro():
    codigos = [3303302] * (MAX_MUNICIPIOS_GEOJSON + 1)

    result = await GeoService().gerar_geojson_municipios(codigos)

    assert result.ok is False
    assert result.data is None
    assert result.errors


@respx.mock
async def test_gerar_geojson_municipios_todos_invalidos_retorna_erro():
    respx.get(f"{BASE_URL}/municipios/3303302").mock(
        return_value=httpx.Response(200, json={"erro": "sem malha"})
    )

    result = await GeoService().gerar_geojson_municipios([3303302])

    assert result.ok is False
    assert result.data is None
    assert result.errors


def test_calcular_bbox_com_feature_collection(malha_municipio_niteroi):
    bbox = calcular_bbox(malha_municipio_niteroi)

    assert bbox is not None
    assert bbox.as_geojson_bbox() == [-43.13, -22.92, -43.05, -22.86]


def test_calcular_bbox_sem_geometria_retorna_none():
    assert calcular_bbox({"type": "FeatureCollection", "features": []}) is None
    assert calcular_bbox(None) is None
    assert calcular_bbox({"tipo": "invalido"}) is None


def test_is_valid_geojson():
    assert is_valid_geojson({"type": "FeatureCollection", "features": []}) is True
    assert is_valid_geojson({"type": "Polygon", "coordinates": []}) is True
    assert is_valid_geojson({"erro": "sem malha"}) is False
    assert is_valid_geojson([1, 2, 3]) is False
