"""Validação de consultas ao SIDRA contra os metadados de um agregado.

`validar_consulta` verifica se `variaveis`, `localidades` (níveis
territoriais), `periodos` e `classificacao` — já validados em *formato* por
`mcp_ibge.utils.validators` — existem de fato nos metadados de um agregado
(`AgregadoMetadataParsed`, de `metadata_parser.parse_agregado_metadata`). Não
faz nenhuma requisição: é uma validação puramente local, contra metadados já
obtidos.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

from .metadata_parser import AgregadoMetadataParsed

# Extrai o número de cada nível territorial de uma expressão `localidades`
# (ex.: "N3[33]|N6[3550308]" -> ["3", "6"]).
_NIVEL_LOCALIDADE = re.compile(r"N(\d{1,3})(?:\[[^\]]*\])?")

# Expressão de classificação: "<id_classificacao>[<id_categoria>,...]" ou
# apenas "<id_classificacao>".
_CLASSIFICACAO = re.compile(r"^(\d+)(?:\[([^\]]*)\])?$")

# Token de período começando por um ano de 4 dígitos (ex.: "2021", "202101").
_ANO = re.compile(r"^\d{4}")

_SEPARADOR_PERIODOS = re.compile(r"[,|]")


class ValidacaoConsulta(BaseModel):
    """Resultado da validação de uma consulta SIDRA contra os metadados de um agregado."""

    valido: bool
    agregado_id: str
    variaveis_validas: list[str] = Field(default_factory=list)
    variaveis_invalidas: list[str] = Field(default_factory=list)
    niveis_territoriais: list[str] = Field(default_factory=list)
    niveis_invalidos: list[str] = Field(default_factory=list)
    classificacao_valida: bool | None = None
    erros: list[str] = Field(default_factory=list)
    avisos: list[str] = Field(default_factory=list)


def _validar_variaveis(
    metadata: AgregadoMetadataParsed, variaveis: str
) -> tuple[list[str], list[str]]:
    if variaveis.strip().lower() == "all":
        return ["all"], []

    ids_validos = {v.id for v in metadata.variaveis}
    tokens = [token.strip() for token in variaveis.split("|")]

    validas = [token for token in tokens if token in ids_validos]
    invalidas = [token for token in tokens if token not in ids_validos]
    return validas, invalidas


def _validar_niveis(
    metadata: AgregadoMetadataParsed, localidades: str
) -> tuple[list[str], list[str]]:
    niveis_informados = dict.fromkeys(
        f"N{numero}" for numero in _NIVEL_LOCALIDADE.findall(localidades)
    )
    niveis_validos = set(metadata.niveis_territoriais)

    validos = [nivel for nivel in niveis_informados if nivel in niveis_validos]
    invalidos = [nivel for nivel in niveis_informados if nivel not in niveis_validos]
    return validos, invalidos


def _validar_classificacao(
    metadata: AgregadoMetadataParsed, classificacao: str | None, erros: list[str]
) -> bool | None:
    if classificacao is None:
        return None

    match = _CLASSIFICACAO.match(classificacao.strip())
    if not match:
        erros.append(
            f'Classificação inválida: "{classificacao}". Use o formato '
            '"<id_classificacao>[<id_categoria>,...]" (ex.: "2[6794]").'
        )
        return False

    classificacao_id, categorias_str = match.group(1), match.group(2)
    classificacoes_por_id = {c.id: c for c in metadata.classificacoes}

    classificacao_meta = classificacoes_por_id.get(classificacao_id)
    if classificacao_meta is None:
        erros.append(
            f'Classificação "{classificacao_id}" não existe no agregado "{metadata.id}". '
            "Use `listar_classificacoes_tabela_sidra` para ver as classificações "
            "disponíveis."
        )
        return False

    if categorias_str is None:
        return True

    categorias_validas = {c.id for c in classificacao_meta.categorias}
    categorias_informadas = [c.strip() for c in categorias_str.split(",") if c.strip()]
    categorias_invalidas = [c for c in categorias_informadas if c not in categorias_validas]

    if categorias_invalidas:
        erros.append(
            f'Categoria(s) "{", ".join(categorias_invalidas)}" não existe(m) na '
            f'classificação "{classificacao_id}" do agregado "{metadata.id}".'
        )
        return False

    return True


def _validar_periodos(metadata: AgregadoMetadataParsed, periodos: str, avisos: list[str]) -> None:
    inicio, fim = metadata.periodicidade.inicio, metadata.periodicidade.fim
    if inicio is None or fim is None:
        return

    for token in _SEPARADOR_PERIODOS.split(periodos):
        match = _ANO.match(token.strip())
        if not match:
            continue

        ano = int(match.group(0))
        if ano < inicio or ano > fim:
            avisos.append(
                f'Período "{token.strip()}" está fora do intervalo informado pela API '
                f"para o agregado {metadata.id} ({inicio}-{fim})."
            )


def validar_consulta(
    metadata: AgregadoMetadataParsed,
    *,
    variaveis: str,
    localidades: str,
    periodos: str,
    classificacao: str | None = None,
) -> ValidacaoConsulta:
    """Valida `variaveis`, `localidades`, `periodos` e `classificacao` contra `metadata`.

    `valido=True` exige ao menos uma variável e um nível territorial válidos,
    e nenhuma classificação inválida. Variáveis/níveis inválidos não impedem
    a validação por si só (geram `avisos`), mas se *nenhum* for válido o
    resultado é inválido. Períodos fora do intervalo conhecido pela API geram
    apenas `avisos` (a API pode aceitar períodos não listados em metadados).
    """
    erros: list[str] = []
    avisos: list[str] = []

    variaveis_validas, variaveis_invalidas = _validar_variaveis(metadata, variaveis)
    niveis_validos, niveis_invalidos = _validar_niveis(metadata, localidades)
    classificacao_valida = _validar_classificacao(metadata, classificacao, erros)
    _validar_periodos(metadata, periodos, avisos)

    if not variaveis_validas:
        erros.append(
            f'Nenhuma das variáveis "{variaveis}" existe no agregado "{metadata.id}". '
            "Use `listar_variaveis_tabela_sidra` para ver as variáveis disponíveis."
        )
    elif variaveis_invalidas:
        avisos.append(
            f'Variável(is) "{", ".join(variaveis_invalidas)}" não encontrada(s) no '
            f'agregado "{metadata.id}" e será(ão) ignorada(s).'
        )

    if not niveis_validos:
        disponiveis = ", ".join(metadata.niveis_territoriais) or "nenhum"
        erros.append(
            f'Nenhum dos níveis territoriais de "{localidades}" está disponível no '
            f'agregado "{metadata.id}" (disponíveis: {disponiveis}).'
        )
    elif niveis_invalidos:
        avisos.append(
            f'Nível(is) territorial(is) "{", ".join(niveis_invalidos)}" não disponível(is) '
            f'no agregado "{metadata.id}".'
        )

    valido = not erros

    return ValidacaoConsulta(
        valido=valido,
        agregado_id=metadata.id,
        variaveis_validas=variaveis_validas,
        variaveis_invalidas=variaveis_invalidas,
        niveis_territoriais=niveis_validos,
        niveis_invalidos=niveis_invalidos,
        classificacao_valida=classificacao_valida,
        erros=erros,
        avisos=avisos,
    )
