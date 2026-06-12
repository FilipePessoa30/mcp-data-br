"""Tools MCP do SIDRA Query Builder: descoberta, explicação, sugestão, validação e execução."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ..services.sidra_service import SidraService
from . import run_typed_tool

_sidra_service = SidraService()

_AGREGADO_ID_DESCRIPTION = 'ID do agregado do SIDRA (ex.: "6579" = "População residente estimada").'

_VARIAVEIS_DESCRIPTION = (
    'ID de variável do agregado, lista separada por "|" (ex.: "93|1000093") ou "all" para todas.'
)

_LOCALIDADES_DESCRIPTION = (
    'Unidade territorial no formato N<nivel>[<ids>], ex.: "N1[all]" (Brasil), '
    '"N3[all]" (todos os estados), "N6[3550308]" (município de São Paulo).'
)

_PERIODOS_DESCRIPTION = (
    'Período(s): um ano ("2021"), intervalo ("2010-2020"), lista '
    '("2020|2021|2022") ou relativo ("-6" = últimos 6 períodos, "-1" = último '
    "período disponível)."
)

_CLASSIFICACAO_DESCRIPTION = (
    'Classificação opcional no formato "<id_classificacao>[<id_categoria>,...]" '
    '(ex.: "2[6794]"). Use `listar_classificacoes_tabela_sidra` para ver as '
    "classificações disponíveis."
)


def register_sidra_tools(mcp: FastMCP) -> None:
    """Registra as tools do SIDRA Query Builder na instância FastMCP fornecida."""

    @mcp.tool()
    async def buscar_tabelas_sidra(
        tema: Annotated[
            str, Field(description='Tema/assunto de interesse (ex.: "população", "inflação").')
        ],
        limite: Annotated[
            int, Field(description="Número máximo de agregados retornados (1-100).", ge=1, le=100)
        ] = 10,
    ) -> dict[str, Any]:
        """Busca agregados (tabelas) do SIDRA relacionados a `tema`.

        A busca é feita por palavras-chave: os termos de `tema` são comparados
        com o nome de cada agregado disponível em `/agregados`. Cada item
        retornado inclui `id`, `nome` e `pontuacao` (quantas palavras-chave
        casaram). Use o `id` de um agregado em `explicar_tabela_sidra`,
        `listar_variaveis_tabela_sidra` ou `validar_consulta_sidra`.
        """
        return await run_typed_tool(_sidra_service.buscar_tabelas_sidra(tema, limite))

    @mcp.tool()
    async def explicar_tabela_sidra(
        agregado_id: Annotated[str, Field(description=_AGREGADO_ID_DESCRIPTION)],
    ) -> dict[str, Any]:
        """Explica um agregado do SIDRA: nome, pesquisa, assunto, periodicidade,
        variáveis, classificações e limitações.

        `limitacoes` resume em texto o intervalo de períodos disponível, os
        níveis territoriais suportados e se a tabela possui classificações
        adicionais — use isso para montar uma consulta válida antes de
        chamar `validar_consulta_sidra` ou `executar_consulta_sidra_validada`.
        """
        return await run_typed_tool(_sidra_service.explicar_tabela_sidra(agregado_id))

    @mcp.tool()
    async def listar_variaveis_tabela_sidra(
        agregado_id: Annotated[str, Field(description=_AGREGADO_ID_DESCRIPTION)],
    ) -> dict[str, Any]:
        """Lista as variáveis disponíveis em um agregado do SIDRA.

        Cada variável retornada inclui `id`, `nome` e `unidade`. Use o `id`
        de uma variável no parâmetro `variaveis` de `validar_consulta_sidra`
        ou `executar_consulta_sidra_validada`.
        """
        return await run_typed_tool(_sidra_service.listar_variaveis_tabela_sidra(agregado_id))

    @mcp.tool()
    async def listar_classificacoes_tabela_sidra(
        agregado_id: Annotated[str, Field(description=_AGREGADO_ID_DESCRIPTION)],
    ) -> dict[str, Any]:
        """Lista as classificações disponíveis em um agregado do SIDRA.

        Cada classificação retornada inclui `id`, `nome` e `categorias`
        (cada uma com `id` e `nome`). Use `"<id_classificacao>[<id_categoria>]"`
        no parâmetro `classificacao` de `validar_consulta_sidra` ou
        `executar_consulta_sidra_validada`. Uma lista vazia indica que o
        agregado não possui classificações adicionais (apenas variáveis).
        """
        return await run_typed_tool(_sidra_service.listar_classificacoes_tabela_sidra(agregado_id))

    @mcp.tool()
    async def sugerir_consulta_sidra(
        pergunta: Annotated[
            str,
            Field(
                description=(
                    'Pergunta em linguagem natural (ex.: "qual a população '
                    'estimada dos municípios em 2024?").'
                )
            ),
        ],
    ) -> dict[str, Any]:
        """Sugere uma consulta SIDRA (agregado, variável e localidades) para `pergunta`.

        **Não executa nenhuma consulta** — apenas propõe `agregado_id`,
        `variaveis` e `localidades` com base em busca por palavras-chave nos
        metadados (sem uso de modelos de linguagem). `warnings` sempre
        explica a heurística usada e, quando houver, lista agregados
        alternativos em `data.alternativas`. Revise a sugestão com
        `explicar_tabela_sidra` e confirme com `validar_consulta_sidra` antes
        de executar.
        """
        return await run_typed_tool(_sidra_service.sugerir_consulta_sidra(pergunta))

    @mcp.tool()
    async def validar_consulta_sidra(
        agregado_id: Annotated[str, Field(description=_AGREGADO_ID_DESCRIPTION)],
        variaveis: Annotated[str, Field(description=_VARIAVEIS_DESCRIPTION)],
        localidades: Annotated[str, Field(description=_LOCALIDADES_DESCRIPTION)],
        periodos: Annotated[str, Field(description=_PERIODOS_DESCRIPTION)],
        classificacao: Annotated[str | None, Field(description=_CLASSIFICACAO_DESCRIPTION)] = None,
    ) -> dict[str, Any]:
        """Valida `variaveis`, `localidades`, `periodos` e `classificacao` para um
        agregado do SIDRA.

        Verifica primeiro o formato de cada parâmetro e depois se os valores
        existem de fato nos metadados do agregado (`obter_metadados_agregado`).
        `ok=False` (com `errors`) se algo for inválido; `avisos` em `data`
        apontam problemas que não impedem a consulta (ex.: período fora do
        intervalo conhecido). Use antes de `executar_consulta_sidra_validada`
        para entender por que uma consulta seria rejeitada.
        """
        return await run_typed_tool(
            _sidra_service.validar_consulta_sidra(
                agregado_id, variaveis, localidades, periodos, classificacao
            )
        )

    @mcp.tool()
    async def executar_consulta_sidra_validada(
        agregado_id: Annotated[str, Field(description=_AGREGADO_ID_DESCRIPTION)],
        variaveis: Annotated[str, Field(description=_VARIAVEIS_DESCRIPTION)],
        localidades: Annotated[str, Field(description=_LOCALIDADES_DESCRIPTION)],
        periodos: Annotated[str, Field(description=_PERIODOS_DESCRIPTION)] = "-6",
        classificacao: Annotated[str | None, Field(description=_CLASSIFICACAO_DESCRIPTION)] = None,
        view: Annotated[
            str | None,
            Field(description='Formato alternativo de resposta da API (ex.: "flat").'),
        ] = None,
    ) -> dict[str, Any]:
        """Valida a consulta contra os metadados do agregado e só a executa se for válida.

        Equivale a chamar `validar_consulta_sidra` e, apenas se
        `data.valido=True`, `consultar_agregado`. Se a validação falhar,
        retorna `ok=False` com os mesmos `errors`/`warnings` de
        `validar_consulta_sidra` e **nenhuma requisição adicional é feita**.
        """
        return await run_typed_tool(
            _sidra_service.executar_consulta_sidra_validada(
                agregado_id, variaveis, localidades, periodos, classificacao, view
            )
        )
