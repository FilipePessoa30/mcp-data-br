# Module: mcp-rio (planned)

> **Status: planning / scaffold.** `packages/mcp_rio/` exists and runs
> (`uv run mcp-rio`), exposing only the shared `status` tool — no data tool is
> implemented yet. This page is the initial plan: data sources, planned
> tools and known challenges.

## Overview

`mcp-rio` will expose City of Rio de Janeiro open data (Data.Rio) — municipal datasets and indicators as typed, traceable
[MCP](https://modelcontextprotocol.io/) tools, following the conventions
established by [`mcp-ibge`](ibge.md) (see
[Architecture](../architecture.md) and [Data Sources](../data_sources.md)).

## Planned data sources

- **Data.Rio (CKAN)** — `https://www.data.rio/` — catálogo de datasets publicados pelas secretarias municipais do Rio de Janeiro.
- Integração futura com `mcp-ibge` (código IBGE do município do Rio de Janeiro: `3304557`) para cruzar indicadores municipais com dados do IBGE.

## Planned tools

| # | Tool | Description |
| --- | --- | --- |
| 1 | `buscar_datasets_rio` | Busca datasets no catálogo Data.Rio por termo ou secretaria. |
| 2 | `obter_dataset_rio` | Detalhes de um dataset do Data.Rio (recursos, formato, licença). |
| 3 | `listar_indicadores_municipais_rio` | Lista indicadores municipais já mapeados por este módulo. |

None of these are implemented yet — the package currently exposes only the
shared `status` tool described in
[Architecture: adding a new module](../architecture.md#adding-a-new-module).

## Conventions

Like every module in `mcp-data-br`, `mcp-rio` will follow:

- The shared `{"ok", "data", "metadata", "warnings", "errors"}` response
  envelope (see [data_sources.md](../data_sources.md)).
- An allowlist of official domains for outbound requests (see
  [security.md](../security.md)).
- Configuration via `pydantic-settings`, env prefix `MCP_RIO_`.
- Portuguese tool-naming convention (`listar_`, `obter_`, `buscar_`,
  `consultar_`).

## See also

- [packages/mcp_rio/README.md](https://github.com/FilipePessoa30/mcp-data-br/blob/main/packages/mcp_rio/README.md)
- [docs/roadmap.md](../roadmap.md)
