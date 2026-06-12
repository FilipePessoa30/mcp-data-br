"""SIDRA Query Builder: descoberta, explicação, sugestão, validação e execução de consultas.

Orquestra `AgregadosService`/`AgregadosClient` (já com cache e validação de
formato) com `mcp_ibge.sidra` (`metadata_parser`, `query_builder`,
`suggestions`) para ajudar agentes a montar consultas corretas ao SIDRA sem
adivinhar `agregado`, `variavel`, `periodo`, `localidade` ou `classificacao`.

Nenhuma etapa usa modelos de linguagem: `sugerir_consulta_sidra` é baseada em
busca de metadados, palavras-chave e regras simples (`sidra.suggestions`).
"""

from __future__ import annotations

from typing import Any

from ..clients.agregados import AgregadosClient
from ..schemas.agregados import AgregadoQueryResult
from ..schemas.common import SourceMetadata, TypedToolResult, build_metadata
from ..sidra.metadata_parser import (
    AgregadoMetadataParsed,
    SidraClassificacao,
    SidraVariavel,
    parse_agregado_metadata,
)
from ..sidra.query_builder import ValidacaoConsulta, validar_consulta
from ..sidra.suggestions import (
    AgregadoSugerido,
    SugestaoConsulta,
    extrair_palavras_chave,
    ranquear_agregados,
    sugerir_localidade,
    sugerir_variavel,
)
from ..utils.errors import IBGEClientError
from ..utils.validators import (
    validate_agregado_id,
    validate_limit,
    validate_niveis,
    validate_periodos,
    validate_variaveis,
)
from .agregados_service import AgregadosService


def _metadata(
    *,
    endpoint: str,
    params: dict[str, Any],
    period: str | None = None,
    territorial_level: str | None = None,
    cache_hit: bool = False,
) -> SourceMetadata:
    return build_metadata(
        source_url=endpoint,
        endpoint=endpoint,
        params=params,
        period=period,
        territorial_level=territorial_level,
        cache_hit=cache_hit,
    )


class SidraService:
    """Operações de alto nível para descobrir, explicar, sugerir, validar e executar
    consultas SIDRA.
    """

    def __init__(
        self,
        client: AgregadosClient | None = None,
        agregados_service: AgregadosService | None = None,
    ) -> None:
        self._client = client or AgregadosClient()
        self._agregados_service = agregados_service or AgregadosService(self._client)

    async def buscar_tabelas_sidra(
        self, tema: str, limite: int = 10
    ) -> TypedToolResult[list[AgregadoSugerido]]:
        """Busca agregados do SIDRA relacionados a `tema`, por palavras-chave no nome."""
        params: dict[str, Any] = {"tema": tema, "limite": limite}

        try:
            limite = validate_limit(limite, url=self._client.base_url)
        except IBGEClientError as exc:
            return TypedToolResult(
                ok=False,
                data=[],
                metadata=_metadata(endpoint=exc.url, params=params),
                errors=[str(exc)],
            )

        resultado = await self._agregados_service.listar_agregados()
        if not resultado.ok:
            return TypedToolResult(
                ok=False,
                data=[],
                metadata=_metadata(endpoint=resultado.metadata.endpoint, params=params),
                errors=resultado.errors,
            )

        palavras_chave = extrair_palavras_chave(tema)
        sugestoes = ranquear_agregados(palavras_chave, resultado.data)[:limite]

        warnings: list[str] = []
        if not sugestoes:
            warnings.append(
                f'Nenhum agregado encontrado para o tema "{tema}". Tente palavras-chave '
                "diferentes ou use `listar_agregados` para ver todos os agregados."
            )

        return TypedToolResult(
            ok=True,
            data=sugestoes,
            metadata=_metadata(
                endpoint=resultado.metadata.endpoint,
                params=params,
                cache_hit=resultado.metadata.cache_hit,
            ),
            warnings=warnings,
        )

    async def _obter_metadata_parseada(
        self, agregado_id: str
    ) -> TypedToolResult[AgregadoMetadataParsed | None]:
        """Obtém e converte `/agregados/{id}/metadados` em `AgregadoMetadataParsed`."""
        resultado = await self._agregados_service.obter_metadados_agregado(agregado_id)
        if not resultado.ok or resultado.data is None:
            return TypedToolResult(
                ok=False, data=None, metadata=resultado.metadata, errors=resultado.errors
            )

        return TypedToolResult(
            ok=True,
            data=parse_agregado_metadata(resultado.data.raw),
            metadata=resultado.metadata,
        )

    async def explicar_tabela_sidra(
        self, agregado_id: str
    ) -> TypedToolResult[AgregadoMetadataParsed | None]:
        """Explica um agregado: nome, pesquisa, assunto, periodicidade, variáveis,
        classificações e limitações.
        """
        return await self._obter_metadata_parseada(agregado_id)

    async def listar_variaveis_tabela_sidra(
        self, agregado_id: str
    ) -> TypedToolResult[list[SidraVariavel]]:
        """Lista as variáveis de um agregado, a partir dos metadados
        (`/agregados/{id}/metadados`).
        """
        resultado = await self._obter_metadata_parseada(agregado_id)
        if not resultado.ok or resultado.data is None:
            return TypedToolResult(
                ok=False, data=[], metadata=resultado.metadata, errors=resultado.errors
            )
        return TypedToolResult(ok=True, data=resultado.data.variaveis, metadata=resultado.metadata)

    async def listar_classificacoes_tabela_sidra(
        self, agregado_id: str
    ) -> TypedToolResult[list[SidraClassificacao]]:
        """Lista as classificações de um agregado, a partir dos metadados
        (`/agregados/{id}/metadados`).
        """
        resultado = await self._obter_metadata_parseada(agregado_id)
        if not resultado.ok or resultado.data is None:
            return TypedToolResult(
                ok=False, data=[], metadata=resultado.metadata, errors=resultado.errors
            )
        return TypedToolResult(
            ok=True, data=resultado.data.classificacoes, metadata=resultado.metadata
        )

    async def sugerir_consulta_sidra(
        self, pergunta: str
    ) -> TypedToolResult[SugestaoConsulta | None]:
        """Sugere uma consulta SIDRA (agregado, variável, localidades) para `pergunta`,
        sem executá-la.

        A sugestão é por busca de palavras-chave nos metadados já obtidos
        (sem uso de modelos de linguagem): conta quantas palavras de
        `pergunta` aparecem no nome de cada agregado/variável, e usa um
        pequeno dicionário de palavras-chave para sugerir o nível
        territorial. Sempre retorna `warnings` explicando a heurística usada
        e, quando houver, agregados alternativos.
        """
        params: dict[str, Any] = {"pergunta": pergunta}

        resultado = await self._agregados_service.listar_agregados()
        if not resultado.ok:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=_metadata(endpoint=resultado.metadata.endpoint, params=params),
                errors=resultado.errors,
            )

        palavras_chave = extrair_palavras_chave(pergunta)
        candidatos = ranquear_agregados(palavras_chave, resultado.data)

        if not candidatos:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=_metadata(endpoint=resultado.metadata.endpoint, params=params),
                errors=[
                    f'Não foi possível identificar um agregado para a pergunta "{pergunta}". '
                    "Tente reformular com termos mais específicos (ex.: o nome de um "
                    "indicador) ou use `buscar_tabelas_sidra`/`listar_agregados`."
                ],
            )

        melhor = candidatos[0]
        metadata_resultado = await self._obter_metadata_parseada(melhor.id)
        if not metadata_resultado.ok or metadata_resultado.data is None:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=metadata_resultado.metadata,
                errors=metadata_resultado.errors,
            )

        metadata_agregado = metadata_resultado.data
        variavel = sugerir_variavel(palavras_chave, metadata_agregado.variaveis)
        localidades = sugerir_localidade(palavras_chave)

        warnings = [
            "Sugestão gerada por busca de palavras-chave em metadados (sem uso de "
            "modelos de linguagem); revise os parâmetros antes de executar, com "
            "`validar_consulta_sidra` ou `explicar_tabela_sidra`."
        ]
        if len(candidatos) > 1:
            alternativas = ", ".join(f"{c.id} ({c.nome})" for c in candidatos[1:4])
            warnings.append(f"Outros agregados também correspondem à pergunta: {alternativas}.")
        if variavel is None:
            warnings.append(f'O agregado "{melhor.id}" não possui variáveis informadas.')

        sugestao = SugestaoConsulta(
            agregado_id=melhor.id,
            agregado_nome=melhor.nome,
            variaveis=variavel.id if variavel else "all",
            variavel_nome=variavel.nome if variavel else None,
            localidades=localidades,
            alternativas=candidatos[1:6],
        )

        metadata = metadata_resultado.metadata.model_copy(
            update={"params": {**params, **metadata_resultado.metadata.params}}
        )

        return TypedToolResult(ok=True, data=sugestao, metadata=metadata, warnings=warnings)

    async def validar_consulta_sidra(
        self,
        agregado_id: str,
        variaveis: str,
        localidades: str,
        periodos: str,
        classificacao: str | None = None,
    ) -> TypedToolResult[ValidacaoConsulta | None]:
        """Valida `variaveis`, `localidades`, `periodos` e `classificacao` contra os
        metadados de `agregado_id`.

        Primeiro valida o *formato* de cada parâmetro (`mcp_ibge.utils.validators`);
        depois obtém os metadados do agregado e verifica se os valores
        informados de fato existem nesse agregado (`sidra.query_builder.validar_consulta`).
        `ok=False` se o formato for inválido, os metadados não puderem ser
        obtidos, ou a consulta não passar na validação (`data.valido=False`).
        """
        params: dict[str, Any] = {
            "agregado_id": agregado_id,
            "variaveis": variaveis,
            "localidades": localidades,
            "periodos": periodos,
        }
        if classificacao:
            params["classificacao"] = classificacao

        try:
            agregado_id = validate_agregado_id(agregado_id, url=self._client.base_url)
            variaveis = validate_variaveis(variaveis, url=self._client.base_url)
            localidades = validate_niveis(localidades, url=self._client.base_url)
            periodos = validate_periodos(periodos, url=self._client.base_url)
        except IBGEClientError as exc:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=_metadata(endpoint=exc.url, params=params),
                errors=[str(exc)],
            )

        metadata_resultado = await self._obter_metadata_parseada(agregado_id)
        if not metadata_resultado.ok or metadata_resultado.data is None:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=metadata_resultado.metadata,
                errors=metadata_resultado.errors,
            )

        validacao = validar_consulta(
            metadata_resultado.data,
            variaveis=variaveis,
            localidades=localidades,
            periodos=periodos,
            classificacao=classificacao,
        )

        return TypedToolResult(
            ok=validacao.valido,
            data=validacao,
            metadata=metadata_resultado.metadata,
            warnings=list(validacao.avisos),
            errors=[] if validacao.valido else list(validacao.erros),
        )

    async def executar_consulta_sidra_validada(
        self,
        agregado_id: str,
        variaveis: str,
        localidades: str,
        periodos: str = "-6",
        classificacao: str | None = None,
        view: str | None = None,
    ) -> TypedToolResult[list[AgregadoQueryResult]]:
        """Valida a consulta contra os metadados do agregado e só a executa se for válida."""
        validacao_resultado = await self.validar_consulta_sidra(
            agregado_id, variaveis, localidades, periodos, classificacao
        )

        if validacao_resultado.data is None or not validacao_resultado.data.valido:
            return TypedToolResult(
                ok=False,
                data=[],
                metadata=validacao_resultado.metadata,
                warnings=validacao_resultado.warnings,
                errors=validacao_resultado.errors
                or ["A consulta não passou na validação; veja `errors`/`warnings`."],
            )

        resultado = await self._agregados_service.consultar_agregado(
            agregado_id,
            variaveis=variaveis,
            localidades=localidades,
            periodos=periodos,
            classificacao=classificacao,
            view=view,
        )

        return TypedToolResult(
            ok=resultado.ok,
            data=resultado.data,
            metadata=resultado.metadata,
            warnings=list(validacao_resultado.warnings) + list(resultado.warnings),
            errors=resultado.errors,
        )
