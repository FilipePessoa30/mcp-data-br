"""Testes da sugestão de consultas SIDRA por palavras-chave (`sidra.suggestions`)."""

from __future__ import annotations

from mcp_ibge.schemas.agregados import AgregadoSummary
from mcp_ibge.sidra.metadata_parser import SidraVariavel
from mcp_ibge.sidra.suggestions import (
    extrair_palavras_chave,
    ranquear_agregados,
    sugerir_localidade,
    sugerir_variavel,
)


def test_extrair_palavras_chave_remove_stopwords_e_curtas():
    palavras = extrair_palavras_chave("Qual é a população dos municípios em 2024?")

    assert "qual" not in palavras
    assert "dos" not in palavras
    assert "em" not in palavras
    assert "populacao" in palavras
    assert "municipios" in palavras
    assert "2024" in palavras


def test_ranquear_agregados_ordena_por_pontuacao():
    agregados = [
        AgregadoSummary(id="1", nome="Índice de preços ao consumidor"),
        AgregadoSummary(id="6579", nome="População residente estimada"),
        AgregadoSummary(id="9514", nome="Censo Demográfico - população e domicílios"),
    ]

    sugestoes = ranquear_agregados(["populacao"], agregados)

    assert [s.id for s in sugestoes] == ["6579", "9514"]
    assert all(s.pontuacao > 0 for s in sugestoes)


def test_ranquear_agregados_sem_correspondencia_retorna_vazio():
    agregados = [AgregadoSummary(id="1", nome="Índice de preços ao consumidor")]

    assert ranquear_agregados(["populacao"], agregados) == []


def test_sugerir_variavel_escolhe_melhor_pontuacao():
    variaveis = [
        SidraVariavel(id="93", nome="Variação mensal"),
        SidraVariavel(id="1000093", nome="Variação acumulada no ano"),
    ]

    sugerida = sugerir_variavel(["acumulada"], variaveis)

    assert sugerida is not None
    assert sugerida.id == "1000093"


def test_sugerir_variavel_sem_correspondencia_retorna_primeira():
    variaveis = [SidraVariavel(id="93", nome="Variação mensal")]

    sugerida = sugerir_variavel(["xyz"], variaveis)

    assert sugerida is not None
    assert sugerida.id == "93"


def test_sugerir_variavel_lista_vazia_retorna_none():
    assert sugerir_variavel(["populacao"], []) is None


def test_sugerir_localidade_reconhece_palavra_chave():
    assert sugerir_localidade(["populacao", "municipios"]) == "N6[all]"
    assert sugerir_localidade(["populacao", "estados"]) == "N3[all]"


def test_sugerir_localidade_sem_correspondencia_retorna_padrao():
    assert sugerir_localidade(["populacao"]) == "N1[all]"
