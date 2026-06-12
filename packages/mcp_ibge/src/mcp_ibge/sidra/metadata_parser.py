"""Parsing dos metadados de um agregado SIDRA (`/agregados/{id}/metadados`).

Converte o JSON bruto (já disponível em `AgregadoMetadata.raw`) em um modelo
tipado com periodicidade, níveis territoriais, variáveis, classificações e uma
lista de limitações em texto. Usado pelo SIDRA Query Builder para explicar,
sugerir e validar consultas sem repetir o parsing em cada tool/service.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# Grupos de `nivelTerritorial` retornados por `/agregados/{id}/metadados`.
_GRUPOS_NIVEL_TERRITORIAL = ("Administrativo", "Especial", "IBGE")


class SidraCategoria(BaseModel):
    """Categoria de uma classificação (ex.: "Norte" dentro da classificação "Região")."""

    model_config = ConfigDict(extra="allow")

    id: str
    nome: str
    unidade: str | None = None


class SidraClassificacao(BaseModel):
    """Classificação disponível em um agregado (ex.: "Sexo", "Grupo de idade")."""

    model_config = ConfigDict(extra="allow")

    id: str
    nome: str
    categorias: list[SidraCategoria] = Field(default_factory=list)


class SidraVariavel(BaseModel):
    """Variável disponível em um agregado (ex.: "População residente estimada")."""

    model_config = ConfigDict(extra="allow")

    id: str
    nome: str
    unidade: str | None = None


class SidraPeriodicidade(BaseModel):
    """Periodicidade de um agregado (ex.: anual, de 2001 a 2024)."""

    frequencia: str | None = None
    inicio: int | None = None
    fim: int | None = None


class AgregadoMetadataParsed(BaseModel):
    """Metadados de um agregado SIDRA, organizados para descoberta/validação de consultas."""

    id: str
    nome: str
    pesquisa: str | None = None
    assunto: str | None = None
    periodicidade: SidraPeriodicidade
    niveis_territoriais: list[str] = Field(default_factory=list)
    variaveis: list[SidraVariavel] = Field(default_factory=list)
    classificacoes: list[SidraClassificacao] = Field(default_factory=list)
    limitacoes: list[str] = Field(default_factory=list)


def _parse_periodicidade(data: Any) -> SidraPeriodicidade:
    if not isinstance(data, dict):
        return SidraPeriodicidade()
    return SidraPeriodicidade(
        frequencia=data.get("frequencia"),
        inicio=data.get("inicio"),
        fim=data.get("fim"),
    )


def _parse_niveis_territoriais(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return []

    niveis: dict[str, None] = {}
    for grupo in _GRUPOS_NIVEL_TERRITORIAL:
        for nivel in data.get(grupo) or []:
            niveis[str(nivel)] = None
    return list(niveis)


def _parse_variaveis(data: Any) -> list[SidraVariavel]:
    if not isinstance(data, list):
        return []
    return [
        SidraVariavel(id=str(item["id"]), nome=item["nome"], unidade=item.get("unidade"))
        for item in data
    ]


def _parse_classificacoes(data: Any) -> list[SidraClassificacao]:
    if not isinstance(data, list):
        return []

    classificacoes: list[SidraClassificacao] = []
    for item in data:
        categorias = [
            SidraCategoria(id=str(categoria["id"]), nome=categoria["nome"])
            for categoria in item.get("categorias", [])
        ]
        classificacoes.append(
            SidraClassificacao(id=str(item["id"]), nome=item["nome"], categorias=categorias)
        )
    return classificacoes


def _montar_limitacoes(
    *,
    periodicidade: SidraPeriodicidade,
    niveis_territoriais: list[str],
    classificacoes: list[SidraClassificacao],
) -> list[str]:
    limitacoes: list[str] = []

    if periodicidade.inicio is not None and periodicidade.fim is not None:
        frequencia = periodicidade.frequencia or "periodicidade não informada"
        limitacoes.append(
            f"Dados disponíveis de {periodicidade.inicio} a {periodicidade.fim} ({frequencia})."
        )
    else:
        limitacoes.append("Periodicidade não informada pela API do SIDRA.")

    if niveis_territoriais:
        limitacoes.append(
            "Níveis territoriais disponíveis: " + ", ".join(niveis_territoriais) + "."
        )
    else:
        limitacoes.append("Nenhum nível territorial informado pela API do SIDRA.")

    if not classificacoes:
        limitacoes.append("Esta tabela não possui classificações adicionais (apenas variáveis).")

    return limitacoes


def parse_agregado_metadata(raw: dict[str, Any]) -> AgregadoMetadataParsed:
    """Converte o JSON de `/agregados/{id}/metadados` (`AgregadoMetadata.raw`) em
    `AgregadoMetadataParsed`.
    """
    periodicidade = _parse_periodicidade(raw.get("periodicidade"))
    niveis_territoriais = _parse_niveis_territoriais(raw.get("nivelTerritorial"))
    variaveis = _parse_variaveis(raw.get("variaveis"))
    classificacoes = _parse_classificacoes(raw.get("classificacoes"))

    return AgregadoMetadataParsed(
        id=str(raw["id"]),
        nome=raw["nome"],
        pesquisa=raw.get("pesquisa"),
        assunto=raw.get("assunto"),
        periodicidade=periodicidade,
        niveis_territoriais=niveis_territoriais,
        variaveis=variaveis,
        classificacoes=classificacoes,
        limitacoes=_montar_limitacoes(
            periodicidade=periodicidade,
            niveis_territoriais=niveis_territoriais,
            classificacoes=classificacoes,
        ),
    )
