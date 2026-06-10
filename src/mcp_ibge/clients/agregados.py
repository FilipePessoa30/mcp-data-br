"""Cliente "fino" para a API de Agregados (SIDRA) do IBGE (sem regras de negócio).

Documentação oficial: https://servicodados.ibge.gov.br/api/docs/agregados

Conceitos principais:
    - "Agregado": uma tabela/pesquisa estatística (ex.: Censo, PNAD, estimativas
      populacionais), identificada por um ID numérico.
    - "Variável": uma grandeza medida dentro de um agregado (ex.: população,
      PIB), identificada por um ID numérico.
    - "Período": ano ou trimestre de referência dos dados (ex.: "2021",
      "2021-2022", ou "-1" para o período mais recente disponível).
    - "Localidade": unidade territorial consultada, no formato
      ``N<nivel>[<ids>]``, ex.: ``N1[all]`` (Brasil), ``N3[all]`` (todos os
      estados), ``N6[3550308]`` (município de São Paulo).
    - "Nível": nível territorial (ex.: "N1", "N3", "N6"), usado por
      `get_agregado_localidades` para listar as localidades disponíveis para
      um agregado em um ou mais níveis (ex.: "N1|N3").

Cada método devolve o JSON bruto retornado pela API (em `IBGEResult.data`),
sem assumir que diferentes agregados compartilham a mesma estrutura de
variáveis, classificações ou localidades. Filtros, aliases e regras de
negócio ficam em `mcp_ibge.services.agregados_service`.
"""

from __future__ import annotations

from typing import Any

from ..utils.errors import IBGENotFoundError, IBGEValidationError
from ..utils.validation import validate_agregado_id, validate_niveis, validate_periodos
from .base import AsyncIBGEClient, IBGEResult

AGREGADOS_PATH = "/v3/agregados"


def _validar_obrigatorio(valor: str, nome: str, *, url: str) -> str:
    """Garante que `valor` é uma string não vazia.

    Levanta `IBGEValidationError` (sem fazer requisição) caso `valor` seja
    vazio ou contenha apenas espaços.
    """
    texto = str(valor).strip()
    if not texto:
        raise IBGEValidationError(
            f'Parâmetro "{nome}" não pode ser vazio.', url=url, status_code=422
        )
    return texto


def _garantir_resposta_nao_vazia(data: Any, *, url: str, mensagem: str) -> None:
    """Trata respostas vazias (`[]`, `{}` ou `None`) como recurso não encontrado.

    A API de Agregados costuma responder `200` com corpo vazio (em vez de
    404) quando o agregado, a variável, a localidade ou o período não
    existem.
    """
    if data is None or (isinstance(data, list | dict) and not data):
        raise IBGENotFoundError(mensagem, url=url, status_code=404)


class AgregadosClient(AsyncIBGEClient):
    """Cliente HTTP para `/agregados` (tabelas, metadados e dados do SIDRA)."""

    def __init__(self) -> None:
        super().__init__(AGREGADOS_PATH)

    async def list_agregados(
        self, pesquisa: str | None = None, assunto: str | None = None
    ) -> IBGEResult:
        """`GET /agregados` — lista de pesquisas e seus agregados (tabelas)."""
        params: dict[str, Any] = {}
        if pesquisa:
            params["pesquisa"] = pesquisa
        if assunto:
            params["assunto"] = assunto

        data = await self.get_json("", params=params or None)
        return IBGEResult(data=data, endpoint=self.base_url, params=params)

    async def get_agregado_metadata(self, agregado_id: str) -> IBGEResult:
        """`GET /agregados/{agregado_id}/metadados` — variáveis, períodos e níveis territoriais."""
        agregado_id = validate_agregado_id(agregado_id, url=self.base_url)
        path = f"/{agregado_id}/metadados"
        url = f"{self.base_url}{path}"

        data = await self.get_json(path)
        _garantir_resposta_nao_vazia(
            data, url=url, mensagem=f'Agregado "{agregado_id}" não encontrado.'
        )
        return IBGEResult(data=data, endpoint=url, params={"agregado_id": agregado_id})

    async def get_agregado_localidades(self, agregado_id: str, niveis: str) -> IBGEResult:
        """`GET /agregados/{agregado_id}/localidades/{niveis}` — localidades disponíveis."""
        agregado_id = validate_agregado_id(agregado_id, url=self.base_url)
        niveis = validate_niveis(niveis, url=self.base_url)
        path = f"/{agregado_id}/localidades/{niveis}"
        url = f"{self.base_url}{path}"

        data = await self.get_json(path)
        _garantir_resposta_nao_vazia(
            data,
            url=url,
            mensagem=(
                f'Nenhuma localidade encontrada para o agregado "{agregado_id}" '
                f'no(s) nível(is) "{niveis}".'
            ),
        )
        return IBGEResult(
            data=data, endpoint=url, params={"agregado_id": agregado_id, "niveis": niveis}
        )

    async def get_agregado_periodos(self, agregado_id: str) -> IBGEResult:
        """`GET /agregados/{agregado_id}/periodos` — períodos disponíveis."""
        agregado_id = validate_agregado_id(agregado_id, url=self.base_url)
        path = f"/{agregado_id}/periodos"
        url = f"{self.base_url}{path}"

        data = await self.get_json(path)
        _garantir_resposta_nao_vazia(
            data, url=url, mensagem=f'Agregado "{agregado_id}" não encontrado.'
        )
        return IBGEResult(data=data, endpoint=url, params={"agregado_id": agregado_id})

    async def get_agregado_variaveis(self, agregado_id: str) -> IBGEResult:
        """`GET /agregados/{agregado_id}/variaveis` — variáveis disponíveis."""
        agregado_id = validate_agregado_id(agregado_id, url=self.base_url)
        path = f"/{agregado_id}/variaveis"
        url = f"{self.base_url}{path}"

        data = await self.get_json(path)
        _garantir_resposta_nao_vazia(
            data, url=url, mensagem=f'Agregado "{agregado_id}" não encontrado.'
        )
        return IBGEResult(data=data, endpoint=url, params={"agregado_id": agregado_id})

    async def query_agregado(
        self,
        agregado_id: str,
        variaveis: str,
        localidades: str,
        periodos: str = "-6",
        classificacao: str | None = None,
        view: str | None = None,
    ) -> IBGEResult:
        """`GET /agregados/{agregado_id}/periodos/{periodos}/variaveis/{variaveis}`."""
        agregado_id = validate_agregado_id(agregado_id, url=self.base_url)
        variaveis = _validar_obrigatorio(variaveis, "variaveis", url=self.base_url)
        localidades = _validar_obrigatorio(localidades, "localidades", url=self.base_url)
        periodos = validate_periodos(periodos, url=self.base_url)

        path = f"/{agregado_id}/periodos/{periodos}/variaveis/{variaveis}"
        url = f"{self.base_url}{path}"

        query: dict[str, Any] = {"localidades": localidades}
        if classificacao:
            query["classificacao"] = classificacao
        if view:
            query["view"] = view

        data = await self.get_json(path, params=query)
        _garantir_resposta_nao_vazia(
            data,
            url=url,
            mensagem=(
                f'Nenhum dado encontrado para o agregado "{agregado_id}", variável(is) '
                f'"{variaveis}" em "{localidades}" no(s) período(s) "{periodos}".'
            ),
        )

        params = {
            "agregado_id": agregado_id,
            "variaveis": variaveis,
            "periodos": periodos,
            **query,
        }
        return IBGEResult(data=data, endpoint=url, params=params)
