# Module: mcp-saude (planned)

> **Status: planning / scaffold.** `packages/mcp_saude/` exists and runs
> (`uv run mcp-saude`), exposing only the shared `status` tool — no data tool is
> implemented yet. This page is the initial plan: data sources, planned
> tools and known challenges.

## Overview

`mcp-saude` will expose Brazilian public health data (DataSUS / Ministério da Saúde) — facilities and indicators by município/UF as typed, traceable
[MCP](https://modelcontextprotocol.io/) tools, following the conventions
established by [`mcp-ibge`](ibge.md) (see
[Architecture](../architecture.md) and [Data Sources](../data_sources.md)).

## Planned data sources

- **CNES — Cadastro Nacional de Estabelecimentos de Saúde** — `https://cnes.datasus.gov.br/` — estabelecimentos de saúde por município/UF.
- **DataSUS / TabNet / OpenDataSUS** — indicadores agregados de saúde; sem API REST simples e estável, exige avaliação de formato (TabNet exporta CSV/TabWin) — ver Desafios abaixo.

## Planned tools

| # | Tool | Description |
| --- | --- | --- |
| 1 | `buscar_estabelecimentos_saude` | Lista estabelecimentos de saúde (CNES) por município/UF. |
| 2 | `obter_indicadores_saude_municipio` | Retorna indicadores de saúde agregados para um município. |
| 3 | `listar_indicadores_disponiveis` | Lista indicadores de saúde catalogados por este módulo. |

None of these are implemented yet — the package currently exposes only the
shared `status` tool described in
[Architecture: adding a new module](../architecture.md#adding-a-new-module).

## Desafios

Ao contrário do `mcp-ibge` (`servicodados.ibge.gov.br`), a maior parte dos indicadores do DataSUS é publicada via TabNet (interface web/TabWin), sem uma API REST simples e estável. A implementação real provavelmente dependerá de datasets derivados/pré-processados (ver `services/`), seguindo a estratégia já prevista para `mcp-inep` em [docs/modules/inep.md](inep.md).


## Conventions

Like every module in `mcp-data-br`, `mcp-saude` will follow:

- The shared `{"ok", "data", "metadata", "warnings", "errors"}` response
  envelope (see [data_sources.md](../data_sources.md)).
- An allowlist of official domains for outbound requests (see
  [security.md](../security.md)).
- Configuration via `pydantic-settings`, env prefix `MCP_SAUDE_`.
- Portuguese tool-naming convention (`listar_`, `obter_`, `buscar_`,
  `consultar_`).

## See also

- [packages/mcp_saude/README.md](https://github.com/FilipePessoa30/mcp-data-br/blob/main/packages/mcp_saude/README.md)
- [docs/roadmap.md](../roadmap.md)
