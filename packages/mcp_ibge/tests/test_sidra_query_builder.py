"""Testes da validação local de consultas SIDRA (`sidra.query_builder`)."""

from __future__ import annotations

from mcp_ibge.sidra.metadata_parser import AgregadoMetadataParsed, parse_agregado_metadata
from mcp_ibge.sidra.query_builder import validar_consulta


def _metadata_populacao() -> AgregadoMetadataParsed:
    raw = {
        "id": 6579,
        "nome": "População residente estimada",
        "periodicidade": {"frequencia": "anual", "inicio": 2001, "fim": 2024},
        "nivelTerritorial": {"Administrativo": ["N1", "N3", "N6"], "Especial": [], "IBGE": []},
        "variaveis": [{"id": 9324, "nome": "População residente estimada", "unidade": "Pessoas"}],
        "classificacoes": [],
    }
    return parse_agregado_metadata(raw)


def _metadata_ipca() -> AgregadoMetadataParsed:
    raw = {
        "id": 7060,
        "nome": "IPCA - Variação mensal",
        "periodicidade": {"frequencia": "mensal", "inicio": 197901, "fim": 202412},
        "nivelTerritorial": {"Administrativo": ["N1"], "Especial": [], "IBGE": []},
        "variaveis": [{"id": 63, "nome": "IPCA - Variação mensal", "unidade": "%"}],
        "classificacoes": [
            {
                "id": 315,
                "nome": "Geral, grupo, subgrupo, item e subitem",
                "categorias": [{"id": 7169, "nome": "Índice geral"}],
            }
        ],
    }
    return parse_agregado_metadata(raw)


def test_validar_consulta_valida():
    resultado = validar_consulta(
        _metadata_populacao(), variaveis="9324", localidades="N6[3550308]", periodos="2024"
    )

    assert resultado.valido is True
    assert resultado.variaveis_validas == ["9324"]
    assert resultado.variaveis_invalidas == []
    assert resultado.niveis_territoriais == ["N6"]
    assert resultado.niveis_invalidos == []
    assert resultado.erros == []
    assert resultado.avisos == []


def test_validar_consulta_aceita_all():
    resultado = validar_consulta(
        _metadata_populacao(), variaveis="all", localidades="N1[all]", periodos="-6"
    )

    assert resultado.valido is True
    assert resultado.variaveis_validas == ["all"]


def test_validar_consulta_variavel_inexistente():
    resultado = validar_consulta(
        _metadata_populacao(), variaveis="99999", localidades="N6[3550308]", periodos="2024"
    )

    assert resultado.valido is False
    assert resultado.variaveis_validas == []
    assert resultado.variaveis_invalidas == ["99999"]
    assert any("99999" in erro for erro in resultado.erros)


def test_validar_consulta_nivel_territorial_nao_disponivel():
    resultado = validar_consulta(
        _metadata_populacao(), variaveis="9324", localidades="N2[all]", periodos="2024"
    )

    assert resultado.valido is False
    assert resultado.niveis_territoriais == []
    assert resultado.niveis_invalidos == ["N2"]
    assert any("N2" in erro for erro in resultado.erros)


def test_validar_consulta_periodo_fora_do_intervalo_gera_aviso():
    resultado = validar_consulta(
        _metadata_populacao(), variaveis="9324", localidades="N6[3550308]", periodos="1990"
    )

    assert resultado.valido is True
    assert any("1990" in aviso for aviso in resultado.avisos)


def test_validar_consulta_classificacao_valida_com_categoria():
    resultado = validar_consulta(
        _metadata_ipca(),
        variaveis="63",
        localidades="N1[all]",
        periodos="202412",
        classificacao="315[7169]",
    )

    assert resultado.valido is True
    assert resultado.classificacao_valida is True


def test_validar_consulta_classificacao_inexistente():
    resultado = validar_consulta(
        _metadata_ipca(),
        variaveis="63",
        localidades="N1[all]",
        periodos="202412",
        classificacao="999[1]",
    )

    assert resultado.valido is False
    assert resultado.classificacao_valida is False
    assert any("999" in erro for erro in resultado.erros)


def test_validar_consulta_categoria_inexistente():
    resultado = validar_consulta(
        _metadata_ipca(),
        variaveis="63",
        localidades="N1[all]",
        periodos="202412",
        classificacao="315[1]",
    )

    assert resultado.valido is False
    assert resultado.classificacao_valida is False


def test_validar_consulta_classificacao_sem_categoria_e_valida():
    resultado = validar_consulta(
        _metadata_ipca(),
        variaveis="63",
        localidades="N1[all]",
        periodos="202412",
        classificacao="315",
    )

    assert resultado.valido is True
    assert resultado.classificacao_valida is True
