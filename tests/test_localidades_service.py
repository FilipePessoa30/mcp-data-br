"""Testes da camada de serviço `LocalidadesService` (filtros, busca, validação)."""

from __future__ import annotations

import httpx
import respx

from mcp_ibge.clients.localidades import LOCALIDADES_PATH
from mcp_ibge.config import get_settings
from mcp_ibge.services.localidades_service import LocalidadesService

BASE_URL = f"{get_settings().api_base_url}{LOCALIDADES_PATH}"

REGIOES = [
    {"id": 1, "sigla": "N", "nome": "Norte"},
    {"id": 3, "sigla": "SE", "nome": "Sudeste"},
]

ESTADOS = [
    {
        "id": 35,
        "sigla": "SP",
        "nome": "São Paulo",
        "regiao": {"id": 3, "sigla": "SE", "nome": "Sudeste"},
    },
    {
        "id": 23,
        "sigla": "CE",
        "nome": "Ceará",
        "regiao": {"id": 2, "sigla": "NE", "nome": "Nordeste"},
    },
    {
        "id": 11,
        "sigla": "RO",
        "nome": "Rondônia",
        "regiao": {"id": 1, "sigla": "N", "nome": "Norte"},
    },
]


def _municipio_sp(municipio_id: int, nome: str) -> dict:
    return {
        "id": municipio_id,
        "nome": nome,
        "microrregiao": {
            "id": 35061,
            "nome": "São Paulo",
            "mesorregiao": {
                "id": 3515,
                "nome": "Metropolitana de São Paulo",
                "UF": {
                    "id": 35,
                    "sigla": "SP",
                    "nome": "São Paulo",
                    "regiao": {"id": 3, "sigla": "SE", "nome": "Sudeste"},
                },
            },
        },
    }


MUNICIPIOS_SP = [
    _municipio_sp(3550308, "São Paulo"),
    _municipio_sp(3548807, "São José dos Campos"),
    _municipio_sp(3509502, "Campinas"),
]

MUNICIPIOS_SAO_JOSE = [
    _municipio_sp(3548807, "São José dos Campos"),
    _municipio_sp(3549904, "São José do Rio Preto"),
]

DISTRITOS_SP = [
    {
        "id": 355030801,
        "nome": "Sé",
        "municipio": {"id": 3550308, "nome": "São Paulo"},
    },
]


@respx.mock
async def test_listar_regioes():
    respx.get(f"{BASE_URL}/regioes").mock(return_value=httpx.Response(200, json=REGIOES))

    result = await LocalidadesService().listar_regioes()

    assert result.ok is True
    assert [r.sigla for r in result.data] == ["N", "SE"]
    assert result.metadata.endpoint == f"{BASE_URL}/regioes"


@respx.mock
async def test_listar_estados_ordenados_por_nome():
    respx.get(f"{BASE_URL}/estados").mock(return_value=httpx.Response(200, json=ESTADOS))

    result = await LocalidadesService().listar_estados()

    assert result.ok is True
    assert [e.nome for e in result.data] == ["Ceará", "Rondônia", "São Paulo"]


@respx.mock
async def test_obter_estado_por_sigla():
    respx.get(f"{BASE_URL}/estados/SP").mock(return_value=httpx.Response(200, json=ESTADOS[0]))

    result = await LocalidadesService().obter_estado("SP")

    assert result.ok is True
    assert result.data is not None
    assert result.data.sigla == "SP"
    assert result.data.regiao is not None
    assert result.data.regiao.sigla == "SE"


@respx.mock
async def test_obter_estado_por_codigo_numerico():
    respx.get(f"{BASE_URL}/estados/35").mock(return_value=httpx.Response(200, json=ESTADOS[0]))

    result = await LocalidadesService().obter_estado("35")

    assert result.ok is True
    assert result.data is not None
    assert result.data.sigla == "SP"


async def test_obter_estado_uf_invalida():
    result = await LocalidadesService().obter_estado("XX")

    assert result.ok is False
    assert result.data is None
    assert result.errors
    assert "UF inválida" in result.errors[0]
    assert result.metadata.params == {"uf": "XX"}


@respx.mock
async def test_listar_municipios_por_uf():
    respx.get(f"{BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=MUNICIPIOS_SP)
    )

    result = await LocalidadesService().listar_municipios("SP")

    assert result.ok is True
    assert [m.nome for m in result.data] == ["São Paulo", "São José dos Campos", "Campinas"]
    assert result.data[0].uf_sigla == "SP"
    assert result.data[0].regiao_nome == "Sudeste"


async def test_listar_municipios_uf_invalida():
    result = await LocalidadesService().listar_municipios("ZZ")

    assert result.ok is False
    assert result.data == []
    assert result.errors


@respx.mock
async def test_buscar_municipio_encontrado_por_nome_exato():
    respx.get(f"{BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=MUNICIPIOS_SP)
    )

    result = await LocalidadesService().buscar_municipio("Campinas", uf="SP")

    assert result.ok is True
    assert [m.nome for m in result.data] == ["Campinas"]
    assert result.warnings == []


@respx.mock
async def test_buscar_municipio_encontrado_sem_acento():
    respx.get(f"{BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=MUNICIPIOS_SP)
    )

    result = await LocalidadesService().buscar_municipio("sao jose", uf="SP")

    assert result.ok is True
    assert [m.nome for m in result.data] == ["São José dos Campos"]
    assert result.warnings == []


@respx.mock
async def test_buscar_municipio_ambiguo_retorna_candidatos_e_warning():
    respx.get(f"{BASE_URL}/municipios").mock(
        return_value=httpx.Response(200, json=MUNICIPIOS_SAO_JOSE)
    )

    result = await LocalidadesService().buscar_municipio("São José")

    assert result.ok is True
    assert {m.nome for m in result.data} == {"São José dos Campos", "São José do Rio Preto"}
    assert result.warnings
    assert "São José" in result.warnings[0]


@respx.mock
async def test_obter_codigo_municipio():
    respx.get(f"{BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=MUNICIPIOS_SP)
    )

    result = await LocalidadesService().obter_codigo_municipio("Campinas", "SP")

    assert result.ok is True
    assert result.data == 3509502


@respx.mock
async def test_obter_codigo_municipio_ambiguo():
    respx.get(f"{BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=MUNICIPIOS_SAO_JOSE)
    )

    result = await LocalidadesService().obter_codigo_municipio("São José", "SP")

    assert result.ok is False
    assert result.data is None
    assert result.warnings


async def test_obter_codigo_municipio_uf_invalida():
    result = await LocalidadesService().obter_codigo_municipio("Campinas", "ZZ")

    assert result.ok is False
    assert result.data is None
    assert result.errors


@respx.mock
async def test_obter_municipio_por_codigo():
    municipio = _municipio_sp(3550308, "São Paulo")
    respx.get(f"{BASE_URL}/municipios/3550308").mock(
        return_value=httpx.Response(200, json=municipio)
    )

    result = await LocalidadesService().obter_municipio_por_codigo(3550308)

    assert result.ok is True
    assert result.data is not None
    assert result.data.nome == "São Paulo"
    assert result.data.uf_sigla == "SP"
    assert result.data.regiao_nome == "Sudeste"


@respx.mock
async def test_obter_municipio_por_codigo_inexistente():
    respx.get(f"{BASE_URL}/municipios/9999999").mock(
        return_value=httpx.Response(404, json={"detail": "not found"})
    )

    result = await LocalidadesService().obter_municipio_por_codigo(9999999)

    assert result.ok is False
    assert result.data is None
    assert result.errors


@respx.mock
async def test_listar_distritos():
    respx.get(f"{BASE_URL}/municipios/3550308/distritos").mock(
        return_value=httpx.Response(200, json=DISTRITOS_SP)
    )

    result = await LocalidadesService().listar_distritos(3550308)

    assert result.ok is True
    assert result.data[0].nome == "Sé"
    assert result.data[0].municipio_id == 3550308
