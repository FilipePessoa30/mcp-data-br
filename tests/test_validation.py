"""Testes dos validadores de formato em `mcp_ibge.utils.validation`."""

from __future__ import annotations

import pytest

from mcp_ibge.utils.errors import IBGEValidationError
from mcp_ibge.utils.validation import (
    validate_agregado_id,
    validate_municipality_code,
    validate_niveis,
    validate_periodos,
    validate_uf,
)


@pytest.mark.parametrize("uf", ["RJ", "rj", " rj ", "33", "SP", "DF", "53"])
def test_validate_uf_aceita_sigla_ou_codigo_validos(uf: str):
    assert validate_uf(uf) == uf.strip().upper()


@pytest.mark.parametrize("uf", ["XX", "ZZ", "99", "00", "", "   ", "Rio de Janeiro", "R J"])
def test_validate_uf_rejeita_valores_invalidos(uf: str):
    with pytest.raises(IBGEValidationError):
        validate_uf(uf)


@pytest.mark.parametrize("codigo", [3550308, "3550308", "9999999", " 3304557 "])
def test_validate_municipality_code_aceita_codigos_de_7_digitos(codigo: int | str):
    resultado = validate_municipality_code(codigo)
    assert resultado == int(str(codigo).strip())
    assert isinstance(resultado, int)


@pytest.mark.parametrize(
    "codigo",
    ["", "   ", "123", "12345678", "abcdefg", "-123456", "33.5030.8", 3.5],
)
def test_validate_municipality_code_rejeita_valores_invalidos(codigo: object):
    with pytest.raises(IBGEValidationError):
        validate_municipality_code(codigo)  # type: ignore[arg-type]


@pytest.mark.parametrize("agregado_id", ["6579", " 6579 ", "1", "123456789"])
def test_validate_agregado_id_aceita_ids_numericos(agregado_id: str):
    assert validate_agregado_id(agregado_id) == agregado_id.strip()


@pytest.mark.parametrize("agregado_id", ["", "   ", "abc", "65a9", "-6579", "65 79", "6579.0"])
def test_validate_agregado_id_rejeita_valores_invalidos(agregado_id: str):
    with pytest.raises(IBGEValidationError):
        validate_agregado_id(agregado_id)


@pytest.mark.parametrize(
    "periodos",
    [
        "-1",
        "-6",
        "2021",
        "2024",
        "all",
        "2010-2020",
        "2010,2015-2020,-1",
        "202101",
        "202101-202104",
    ],
)
def test_validate_periodos_aceita_formatos_validos(periodos: str):
    assert validate_periodos(periodos) == periodos


@pytest.mark.parametrize(
    "periodos",
    ["", "   ", "abc", "21", "2021;2022", "2021--2022", "-", "2021,abc", "ALL"],
)
def test_validate_periodos_rejeita_valores_invalidos(periodos: str):
    with pytest.raises(IBGEValidationError):
        validate_periodos(periodos)


@pytest.mark.parametrize("niveis", ["N1", "N6", "N105", "N1|N3", "N1|N3|N6", " N6 "])
def test_validate_niveis_aceita_formatos_validos(niveis: str):
    assert validate_niveis(niveis) == niveis.strip()


@pytest.mark.parametrize("niveis", ["", "   ", "6", "n6", "N", "N1|", "N1|n3", "N1,N3", "N1234"])
def test_validate_niveis_rejeita_valores_invalidos(niveis: str):
    with pytest.raises(IBGEValidationError):
        validate_niveis(niveis)
