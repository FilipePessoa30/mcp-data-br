"""Regras de negócio do domínio de Agregados/SIDRA: filtros e indicadores.

Esta camada usa `AgregadosClient` para falar com a API do IBGE e adiciona
conveniências como filtro textual sobre a lista de agregados, aliases de
localidade (ex.: "BR") e indicadores derivados (população estimada).
"""

from __future__ import annotations

from ..clients.agregados import AgregadosClient
from ..clients.base import IBGEResult

# Agregado 6579 = "População residente estimada"; variável 9324 = "População
# residente estimada". Referência: https://sidra.ibge.gov.br/tabela/6579
AGREGADO_POPULACAO_ESTIMADA = 6579
VARIAVEL_POPULACAO_ESTIMADA = 9324

# Alias amigável para o nível territorial "Brasil" (N1) no SIDRA.
_LOCALIDADE_ALIASES = {
    "brasil": "N1[all]",
    "br": "N1[all]",
}


def _resolver_localidades(localidades: str) -> str:
    """Resolve aliases simples (ex.: "BR") para a sintaxe N<nivel>[<ids>] do SIDRA."""
    return _LOCALIDADE_ALIASES.get(localidades.strip().lower(), localidades)


class AgregadosService:
    """Operações de alto nível sobre tabelas (agregados) do SIDRA."""

    def __init__(self, client: AgregadosClient | None = None) -> None:
        self._client = client or AgregadosClient()

    async def listar_agregados(
        self,
        pesquisa: str | None = None,
        assunto: str | None = None,
        texto: str | None = None,
    ) -> IBGEResult:
        """Lista agregados do SIDRA, com filtro textual local opcional pelo nome."""
        result = await self._client.list_agregados(pesquisa=pesquisa, assunto=assunto)
        data = result.data

        if texto:
            termo = texto.strip().lower()
            filtrado = []
            for grupo in data:
                agregados_filtrados = [
                    agregado
                    for agregado in grupo.get("agregados", [])
                    if termo in agregado.get("nome", "").lower()
                ]
                if agregados_filtrados:
                    filtrado.append({**grupo, "agregados": agregados_filtrados})
            data = filtrado

        params = dict(result.params)
        if texto:
            params["texto"] = texto

        return IBGEResult(data=data, endpoint=result.endpoint, params=params)

    async def obter_metadados(self, agregado_id: int) -> IBGEResult:
        """Obtém os metadados completos de um agregado."""
        return await self._client.get_agregado_metadata(str(agregado_id))

    async def consultar_dados(
        self,
        agregado_id: int,
        variaveis: str = "all",
        periodos: str = "-1",
        localidades: str = "N1[all]",
        classificacoes: str | None = None,
    ) -> IBGEResult:
        """Consulta valores de um agregado, resolvendo aliases de localidade."""
        return await self._client.query_agregado(
            str(agregado_id),
            variaveis=variaveis,
            localidades=_resolver_localidades(localidades),
            periodos=periodos,
            classificacao=classificacoes,
        )

    async def obter_populacao_municipio(self, codigo_municipio: str) -> IBGEResult:
        """Obtém a população residente estimada mais recente de um município.

        Usa o agregado 6579 (Estimativas de população) do SIDRA, variável
        9324, para o período mais recente disponível.
        """
        result = await self._client.query_agregado(
            str(AGREGADO_POPULACAO_ESTIMADA),
            variaveis=str(VARIAVEL_POPULACAO_ESTIMADA),
            periodos="-1",
            localidades=f"N6[{codigo_municipio}]",
        )
        params = {"codigo_municipio": codigo_municipio, **result.params}
        return IBGEResult(data=result.data, endpoint=result.endpoint, params=params)
