# Module: mcp-tesouro (planned)

> **Status: planning / scaffold.** `packages/mcp_tesouro/` exists and runs
> (`uv run mcp-tesouro`), exposing only the shared `status` tool — no data tool is
> implemented yet. This page is the initial plan: data sources, planned
> tools and known challenges.

## Overview

`mcp-tesouro` will expose Brazilian National Treasury fiscal data (Tesouro Transparente / SICONFI) — federal, state and municipal finances as typed, traceable
[MCP](https://modelcontextprotocol.io/) tools, following the conventions
established by [`mcp-ibge`](ibge.md) (see
[Architecture](../architecture.md) and [Data Sources](../data_sources.md)).

## Planned data sources

- **API de Dados Abertos do SICONFI** — `https://apidatalake.tesouro.gov.br/ords/siconfi/tt/...` — RREO, RGF, dívida e finanças de União, estados e municípios.

## Planned tools

| # | Tool | Description |
| --- | --- | --- |
| 1 | `consultar_financas_municipio` | Consulta indicadores fiscais (RREO/RGF) de um município por ano. |
| 2 | `consultar_divida_estado` | Consulta a dívida pública de um estado por ano. |
| 3 | `listar_relatorios_disponiveis` | Lista relatórios fiscais (RREO/RGF) disponíveis por ente/período. |

None of these are implemented yet — the package currently exposes only the
shared `status` tool described in
[Architecture: adding a new module](../architecture.md#adding-a-new-module).

## Conventions

Like every module in `mcp-data-br`, `mcp-tesouro` will follow:

- The shared `{"ok", "data", "metadata", "warnings", "errors"}` response
  envelope (see [data_sources.md](../data_sources.md)).
- An allowlist of official domains for outbound requests (see
  [security.md](../security.md)).
- Configuration via `pydantic-settings`, env prefix `MCP_TESOURO_`.
- Portuguese tool-naming convention (`listar_`, `obter_`, `buscar_`,
  `consultar_`).

## See also

- [packages/mcp_tesouro/README.md](https://github.com/FilipePessoa30/mcp-data-br/blob/main/packages/mcp_tesouro/README.md)
- [docs/roadmap.md](../roadmap.md)
