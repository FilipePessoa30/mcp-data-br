"""Cliente "fino" para a API de Localidades do IBGE (sem regras de negócio).

Documentação oficial: https://servicodados.ibge.gov.br/api/docs/localidades

Cada método mapeia (quase) diretamente um endpoint da API e preserva o JSON
bruto sempre que faz sentido (campo `raw` de `IBGEResult`). Filtros e
transformações adicionais ficam em `mcp_ibge.services.localidades_service`.
"""

from __future__ import annotations

from typing import Any

from ..utils.normalization import normalize_text
from ..utils.validation import (
    UF_CODIGO_POR_SIGLA,
    UF_SIGLA_POR_CODIGO,
    validate_municipality_code,
    validate_uf,
)
from .base import AsyncIBGEClient, IBGEResult

LOCALIDADES_PATH = "/v1/localidades"

__all__ = [
    "LOCALIDADES_PATH",
    "UF_CODIGO_POR_SIGLA",
    "UF_SIGLA_POR_CODIGO",
    "LocalidadesClient",
]


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
        uf = validate_uf(uf_or_id, url=f"{self.base_url}/estados/{uf_or_id}")
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
        uf = validate_uf(uf_or_id, url=f"{self.base_url}/estados/{uf_or_id}/municipios")
        path = f"/estados/{uf}/municipios"
        data = await self.get_json(path)
        return IBGEResult(data=data, endpoint=f"{self.base_url}{path}", params={"uf": uf_or_id})

    async def get_municipio(self, municipio_id: int) -> IBGEResult:
        """`GET /municipios/{id}` — detalhes de um município pelo código IBGE."""
        codigo = validate_municipality_code(
            municipio_id, url=f"{self.base_url}/municipios/{municipio_id}"
        )
        path = f"/municipios/{codigo}"
        data = await self.get_json(path)
        return IBGEResult(
            data=data, endpoint=f"{self.base_url}{path}", params={"municipio_id": codigo}
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
        codigo = validate_municipality_code(
            municipio_id, url=f"{self.base_url}/municipios/{municipio_id}/distritos"
        )
        path = f"/municipios/{codigo}/distritos"
        data = await self.get_json(path)
        return IBGEResult(
            data=data, endpoint=f"{self.base_url}{path}", params={"municipio_id": codigo}
        )
