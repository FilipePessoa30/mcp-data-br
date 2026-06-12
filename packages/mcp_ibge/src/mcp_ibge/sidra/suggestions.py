"""Sugestão de consultas SIDRA por busca em metadados, palavras-chave e regras simples.

Nenhuma chamada a modelos de linguagem é feita aqui: a "sugestão" é apenas uma
pontuação textual — quantas palavras-chave extraídas da pergunta do usuário
aparecem no nome de cada agregado/variável já obtido da API — mais um pequeno
dicionário de palavras-chave -> nível territorial. O resultado é sempre uma
*proposta* (`SugestaoConsulta`), nunca uma execução.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

from ..schemas.agregados import AgregadoSummary
from ..utils.normalization import normalize_text
from .metadata_parser import SidraVariavel

_PALAVRA = re.compile(r"[a-z0-9]+")

# Palavras muito comuns em português, ignoradas na extração de palavras-chave.
_STOPWORDS = {
    "a",
    "o",
    "as",
    "os",
    "de",
    "da",
    "do",
    "das",
    "dos",
    "em",
    "no",
    "na",
    "nos",
    "nas",
    "um",
    "uma",
    "uns",
    "umas",
    "para",
    "por",
    "com",
    "sem",
    "que",
    "qual",
    "quais",
    "quanto",
    "quantos",
    "quanta",
    "quantas",
    "como",
    "onde",
    "quando",
    "e",
    "ou",
    "se",
    "ao",
    "aos",
    "entre",
    "sobre",
    "sob",
    "foi",
    "sao",
    "ser",
    "tem",
    "ha",
    "existe",
    "existem",
    "esta",
    "estao",
    "me",
    "diga",
    "mostre",
    "mostra",
    "quero",
    "saber",
    "dados",
    "dado",
    "qtde",
    "total",
    "valor",
    "valores",
    "todo",
    "toda",
    "todos",
    "todas",
}

# Palavras-chave -> expressão `localidades` correspondente (formato N<nivel>[<ids>]).
_LOCALIDADE_PALAVRAS_CHAVE: dict[str, str] = {
    "brasil": "N1[all]",
    "pais": "N1[all]",
    "nacional": "N1[all]",
    "regiao": "N2[all]",
    "regioes": "N2[all]",
    "estado": "N3[all]",
    "estados": "N3[all]",
    "uf": "N3[all]",
    "municipio": "N6[all]",
    "municipios": "N6[all]",
    "cidade": "N6[all]",
    "cidades": "N6[all]",
}

# Padrão usado quando nenhuma palavra-chave de localidade é encontrada (Brasil).
_LOCALIDADE_PADRAO = "N1[all]"


def extrair_palavras_chave(texto: str) -> list[str]:
    """Extrai palavras-chave de `texto`: normaliza (sem acentos/caixa), remove
    pontuação e descarta palavras curtas (<3 caracteres) ou em `_STOPWORDS`.
    """
    normalizado = normalize_text(texto)
    palavras = _PALAVRA.findall(normalizado)
    return [palavra for palavra in palavras if len(palavra) >= 3 and palavra not in _STOPWORDS]


def _pontuar(palavras_chave: list[str], texto: str) -> int:
    """Conta quantas `palavras_chave` aparecem em `texto` (normalizado)."""
    normalizado = normalize_text(texto)
    return sum(1 for palavra in palavras_chave if palavra in normalizado)


class AgregadoSugerido(BaseModel):
    """Um agregado candidato, com sua pontuação de relevância para a pergunta."""

    id: str
    nome: str
    pontuacao: int


def ranquear_agregados(
    palavras_chave: list[str], agregados: list[AgregadoSummary]
) -> list[AgregadoSugerido]:
    """Ordena `agregados` pela quantidade de `palavras_chave` que aparecem no `nome`.

    Agregados com pontuação 0 são descartados. A ordem relativa entre
    agregados com a mesma pontuação é preservada (ordem original).
    """
    pontuados = [
        AgregadoSugerido(
            id=agregado.id, nome=agregado.nome, pontuacao=_pontuar(palavras_chave, agregado.nome)
        )
        for agregado in agregados
    ]
    relevantes = [agregado for agregado in pontuados if agregado.pontuacao > 0]
    return sorted(relevantes, key=lambda agregado: agregado.pontuacao, reverse=True)


def sugerir_variavel(
    palavras_chave: list[str], variaveis: list[SidraVariavel]
) -> SidraVariavel | None:
    """Sugere a variável de `variaveis` cujo nome melhor pontua para `palavras_chave`.

    Sem nenhuma correspondência, retorna a primeira variável (se houver
    alguma) — a tabela costuma ter poucas variáveis e a primeira é geralmente
    a principal. Retorna `None` se `variaveis` estiver vazia.
    """
    if not variaveis:
        return None

    melhor_variavel, melhor_pontuacao = variaveis[0], 0
    for variavel in variaveis:
        pontuacao = _pontuar(palavras_chave, variavel.nome)
        if pontuacao > melhor_pontuacao:
            melhor_variavel, melhor_pontuacao = variavel, pontuacao
    return melhor_variavel


def sugerir_localidade(palavras_chave: list[str]) -> str:
    """Sugere a expressão `localidades` (ex.: "N3[all]") a partir de `_LOCALIDADE_PALAVRAS_CHAVE`.

    Sem correspondência, retorna `_LOCALIDADE_PADRAO` ("N1[all]" = Brasil).
    """
    for palavra in palavras_chave:
        localidade = _LOCALIDADE_PALAVRAS_CHAVE.get(palavra)
        if localidade:
            return localidade
    return _LOCALIDADE_PADRAO


class SugestaoConsulta(BaseModel):
    """Proposta de consulta SIDRA, a ser revisada/validada antes de executar."""

    agregado_id: str
    agregado_nome: str
    variaveis: str
    variavel_nome: str | None = None
    localidades: str
    periodos: str = "-1"
    classificacao: str | None = None
    alternativas: list[AgregadoSugerido] = Field(default_factory=list)
