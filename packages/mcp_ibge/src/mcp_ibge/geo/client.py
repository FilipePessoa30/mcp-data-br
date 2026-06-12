"""Cliente "fino" para a API de Malhas Geográficas do IBGE (sem regras de negócio).

Documentação oficial: https://servicodados.ibge.gov.br/api/docs/malhas

Cada método mapeia (quase) diretamente um endpoint da API e solicita
explicitamente GeoJSON (`formato=application/vnd.geo+json`), preservando o
corpo da resposta em `IBGEResult.data`. Filtros e transformações (extração de
geometria, bounding box, etc.) ficam em `mcp_ibge.geo.service`.
"""

from __future__ import annotations

from ..clients.base import AsyncIBGEClient, IBGEResult
from ..utils.validators import validate_municipality_code, validate_uf

MALHAS_PATH = "/v3/malhas"

# Formato GeoJSON aceito pela API de Malhas (RFC 7946 / `application/vnd.geo+json`).
_GEOJSON_FORMATO = "application/vnd.geo+json"

__all__ = ["MALHAS_PATH", "MalhasClient"]


class MalhasClient(AsyncIBGEClient):
    """Cliente HTTP para `/malhas` (malhas geográficas de municípios e UFs em GeoJSON)."""

    def __init__(self) -> None:
        super().__init__(MALHAS_PATH)

    async def get_malha_municipio(self, codigo_ibge: int, qualidade: str) -> IBGEResult:
        """`GET /municipios/{id}?formato=application/vnd.geo+json&qualidade=...`"""
        codigo = validate_municipality_code(
            codigo_ibge, url=f"{self.base_url}/municipios/{codigo_ibge}"
        )
        path = f"/municipios/{codigo}"
        params = {"formato": _GEOJSON_FORMATO, "qualidade": qualidade}
        data, cache_hit = await self.get_json(path, params=params)
        return IBGEResult(
            data=data,
            endpoint=f"{self.base_url}{path}",
            params={"codigo_ibge": codigo, "qualidade": qualidade},
            cache_hit=cache_hit,
        )

    async def get_malha_uf(self, uf: str, qualidade: str) -> IBGEResult:
        """`GET /estados/{uf}?formato=application/vnd.geo+json&qualidade=...`"""
        uf_validada = validate_uf(uf, url=f"{self.base_url}/estados/{uf}")
        path = f"/estados/{uf_validada}"
        params = {"formato": _GEOJSON_FORMATO, "qualidade": qualidade}
        data, cache_hit = await self.get_json(path, params=params)
        return IBGEResult(
            data=data,
            endpoint=f"{self.base_url}{path}",
            params={"uf": uf_validada, "qualidade": qualidade},
            cache_hit=cache_hit,
        )
