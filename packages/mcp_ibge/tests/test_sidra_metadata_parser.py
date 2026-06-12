"""Testes do parsing de metadados de agregados SIDRA (`sidra.metadata_parser`)."""

from __future__ import annotations

from mcp_ibge.sidra.metadata_parser import parse_agregado_metadata


def test_parse_agregado_metadata_populacao(agregado_metadados):
    parsed = parse_agregado_metadata(agregado_metadados)

    assert parsed.id == "6579"
    assert parsed.nome == "População residente estimada"
    assert parsed.pesquisa == "Estimativas de População"
    assert parsed.assunto == "População"
    assert parsed.periodicidade.frequencia == "anual"
    assert parsed.periodicidade.inicio == 2001
    assert parsed.periodicidade.fim == 2024
    assert parsed.niveis_territoriais == ["N1", "N2", "N3", "N6"]
    assert len(parsed.variaveis) == 1
    assert parsed.variaveis[0].id == "9324"
    assert parsed.variaveis[0].nome == "População residente estimada"
    assert parsed.variaveis[0].unidade == "Pessoas"
    assert parsed.classificacoes == []
    assert any("2001 a 2024" in limitacao for limitacao in parsed.limitacoes)
    assert any("N1, N2, N3, N6" in limitacao for limitacao in parsed.limitacoes)
    assert any("não possui classificações" in limitacao for limitacao in parsed.limitacoes)


def test_parse_agregado_metadata_com_classificacoes():
    raw = {
        "id": 7060,
        "nome": "IPCA - Variação mensal",
        "pesquisa": "IPCA",
        "assunto": "Inflação",
        "periodicidade": {"frequencia": "mensal", "inicio": 197901, "fim": 202412},
        "nivelTerritorial": {"Administrativo": ["N1"], "Especial": ["N7"], "IBGE": []},
        "variaveis": [{"id": 63, "nome": "IPCA - Variação mensal", "unidade": "%"}],
        "classificacoes": [
            {
                "id": 315,
                "nome": "Geral, grupo, subgrupo, item e subitem",
                "categorias": [
                    {"id": 7169, "nome": "Índice geral"},
                    {"id": 7170, "nome": "Alimentação e bebidas"},
                ],
            }
        ],
    }

    parsed = parse_agregado_metadata(raw)

    assert parsed.id == "7060"
    assert parsed.niveis_territoriais == ["N1", "N7"]
    assert len(parsed.classificacoes) == 1

    classificacao = parsed.classificacoes[0]
    assert classificacao.id == "315"
    assert {categoria.id for categoria in classificacao.categorias} == {"7169", "7170"}
    assert not any("não possui classificações" in limitacao for limitacao in parsed.limitacoes)


def test_parse_agregado_metadata_sem_periodicidade_nem_niveis():
    raw = {"id": 1, "nome": "Tabela sem metadados extras"}

    parsed = parse_agregado_metadata(raw)

    assert parsed.periodicidade.inicio is None
    assert parsed.niveis_territoriais == []
    assert parsed.variaveis == []
    assert parsed.classificacoes == []
    assert "Periodicidade não informada" in parsed.limitacoes[0]
    assert "Nenhum nível territorial informado" in parsed.limitacoes[1]
    assert "não possui classificações" in parsed.limitacoes[2]
