"""Cliente "fino" para a API de Localidades do IBGE (sem regras de negócio).

Documentação oficial: https://servicodados.ibge.gov.br/api/docs/localidades

Cada método mapeia (quase) diretamente um endpoint da API e preserva o JSON
bruto sempre que faz sentido (campo `raw` de `IBGEResult`). Filtros e
transformações adicionais ficam em `mcp_ibge.services.localidades_service`.
"""

from __future__ import annotations

from typing import Any

from ..utils.errors import IBGEValidationError
from ..utils.normalization import normalize_text
from .base import AsyncIBGEClient, IBGEResult

LOCALIDADES_PATH = "/v1/localidades"

# Sigla <-> código numérico IBGE das 26 unidades federativas + Distrito Federal.
UF_SIGLA_POR_CODIGO: dict[str, str] = {
    "11": "RO",
    "12": "AC",
    "13": "AM",
    "14": "RR",
    "15": "PA",
    "16": "AP",
    "17": "TO",
    "21": "MA",
    "22": "PI",
    "23": "CE",
    "24": "RN",
    "25": "PB",
    "26": "PE",
    "27": "AL",
    "28": "SE",
    "29": "BA",
    "31": "MG",
    "32": "ES",
    "33": "RJ",
    "35": "SP",
    "41": "PR",
    "42": "SC",
    "43": "RS",
    "50": "MS",
    "51": "MT",
    "52": "GO",
    "53": "DF",
}
UF_CODIGO_POR_SIGLA: dict[str, str] = {
    sigla: codigo for codigo, sigla in UF_SIGLA_POR_CODIGO.items()
}


def validar_uf(uf_or_id: str) -> str:
    """Valida uma UF, aceitando sigla (ex.: "RJ") ou código IBGE (ex.: "33").

    Retorna o valor normalizado (maiúsculas, sem espaços nas pontas) — o
    formato original (sigla ou código) é preservado. Levanta
    `IBGEValidationError` se o valor não corresponder a uma UF válida.
    """
    valor = uf_or_id.strip().upper()
    if valor in UF_CODIGO_POR_SIGLA or valor in UF_SIGLA_POR_CODIGO:
        return valor

    raise IBGEValidationError(
        f'UF inválida: "{uf_or_id}". Use a sigla (ex.: "RJ") ou o código IBGE (ex.: "33").',
        url=f"{LOCALIDADES_PATH}/estados/{uf_or_id}",
        status_code=422,
    )


class LocalidadesClient(AsyncIBGEClient):
    """Cliente HTTP para `/localidades` (regiões, estados, municípios e distritos)."""

    def __init__(self) -> None:
        super().__init__(LOCALIDADES_PATH)

    async def get_regioes(self) -> IBGEResult:
        """`GET /regioes` — as 5 grandes regiões geográficas do Brasil."""
        path = "/regioes"
        data = await self.get_json(path)
        return IBGEResult(data=data, endpoint=f"{self.base_url}{path}", params={})

    async def get_estados(self) -> IBGEResult:
        """`GET /estados` — os 26 estados e o Distrito Federal."""
        path = "/estados"
        data = await self.get_json(path)
        return IBGEResult(data=data, endpoint=f"{self.base_url}{path}", params={})

    async def get_estado(self, uf_or_id: str) -> IBGEResult:
        """`GET /estados/{uf}` — detalhes de um estado (sigla ou código IBGE)."""
        uf = validar_uf(uf_or_id)
        path = f"/estados/{uf}"
        data = await self.get_json(path)
        return IBGEResult(data=data, endpoint=f"{self.base_url}{path}", params={"uf": uf_or_id})

    async def get_municipios(self) -> IBGEResult:
        """`GET /municipios` — todos os municípios do Brasil."""
        path = "/municipios"
        data = await self.get_json(path)
        return IBGEResult(data=data, endpoint=f"{self.base_url}{path}", params={})

    async def get_municipios_by_uf(self, uf_or_id: str) -> IBGEResult:
        """`GET /estados/{uf}/municipios` — municípios de uma UF (sigla ou código)."""
        uf = validar_uf(uf_or_id)
        path = f"/estados/{uf}/municipios"
        data = await self.get_json(path)
        return IBGEResult(data=data, endpoint=f"{self.base_url}{path}", params={"uf": uf_or_id})

    async def get_municipio(self, municipio_id: int) -> IBGEResult:
        """`GET /municipios/{id}` — detalhes de um município pelo código IBGE."""
        path = f"/municipios/{municipio_id}"
        data = await self.get_json(path)
        return IBGEResult(
            data=data, endpoint=f"{self.base_url}{path}", params={"municipio_id": municipio_id}
        )

    async def search_municipios(self, nome: str, uf: str | None = None) -> IBGEResult:
        """Busca municípios cujo nome contenha `nome`, ignorando acentos e caixa.

        Consulta `/municipios` (Brasil todo) ou `/estados/{uf}/municipios`
        (quando `uf` é informado) e filtra localmente pelo nome. O resultado
        traz os municípios filtrados em `data` e a lista completa retornada
        pela API em `raw`.
        """
        result = await self.get_municipios_by_uf(uf) if uf else await self.get_municipios()

        termo = normalize_text(nome)
        encontrados = [
            municipio
            for municipio in result.data
            if termo in normalize_text(municipio.get("nome", ""))
        ]

        params: dict[str, Any] = {"nome": nome}
        if uf:
            params["uf"] = uf

        return IBGEResult(
            data=encontrados, endpoint=result.endpoint, params=params, raw=result.data
        )

    async def get_distritos_by_municipio(self, municipio_id: int) -> IBGEResult:
        """`GET /municipios/{id}/distritos` — distritos de um município."""
        path = f"/municipios/{municipio_id}/distritos"
        data = await self.get_json(path)
        return IBGEResult(
            data=data, endpoint=f"{self.base_url}{path}", params={"municipio_id": municipio_id}
        )
