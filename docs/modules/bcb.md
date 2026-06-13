# Module: mcp-bcb (planned)

> **Status: planning / scaffold.** `packages/mcp_bcb/` exists and runs
> (`uv run mcp-bcb`), exposing only the shared `status` tool — no data tool is
> implemented yet. This page is the initial plan: data sources, planned
> tools and known challenges.

## Overview

`mcp-bcb` will expose Banco Central do Brasil economic and financial indicators (SGS time series, exchange rates, Selic) as typed, traceable
[MCP](https://modelcontextprotocol.io/) tools, following the conventions
established by [`mcp-ibge`](ibge.md) (see
[Architecture](../architecture.md) and [Data Sources](../data_sources.md)).

## Planned data sources

- **SGS — Sistema Gerenciador de Séries Temporais** — `https://api.bcb.gov.br/dados/serie/bcdata.sgs.<codigo>/dados` — séries históricas (Selic, IPCA, câmbio, etc.), sem chave de API.
- **PTAX** — `https://olinda.bcb.gov.br/olinda/servico/PTAX/...` — cotações diárias de câmbio.

## Planned tools

| # | Tool | Description |
| --- | --- | --- |
| 1 | `obter_serie_temporal` | Retorna uma série temporal do SGS por código, com filtro de período. |
| 2 | `consultar_taxa_selic` | Retorna a taxa Selic (meta ou efetiva) em um período. |
| 3 | `consultar_cotacao_cambio` | Retorna a cotação de uma moeda (ex.: USD) em uma data. |
| 4 | `listar_series_disponiveis` | Lista séries do SGS conhecidas/catalogadas por este módulo. |

None of these are implemented yet — the package currently exposes only the
shared `status` tool described in
[Architecture: adding a new module](../architecture.md#adding-a-new-module).

## Conventions

Like every module in `mcp-data-br`, `mcp-bcb` will follow:

- The shared `{"ok", "data", "metadata", "warnings", "errors"}` response
  envelope (see [data_sources.md](../data_sources.md)).
- An allowlist of official domains for outbound requests (see
  [security.md](../security.md)).
- Configuration via `pydantic-settings`, env prefix `MCP_BCB_`.
- Portuguese tool-naming convention (`listar_`, `obter_`, `buscar_`,
  `consultar_`).

## See also

- [packages/mcp_bcb/README.md](https://github.com/FilipePessoa30/mcp-data-br/blob/main/packages/mcp_bcb/README.md)
- [docs/roadmap.md](../roadmap.md)
