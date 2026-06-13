# Module: mcp-transparencia (planned)

> **Status: planning / scaffold.** `packages/mcp_transparencia/` exists and runs
> (`uv run mcp-transparencia`), exposing only the shared `status` tool — no data tool is
> implemented yet. This page is the initial plan: data sources, planned
> tools and known challenges.

## Overview

`mcp-transparencia` will expose the Brazilian Federal Transparency Portal (Portal da Transparência / CGU) — public spending, contracts and sanctions as typed, traceable
[MCP](https://modelcontextprotocol.io/) tools, following the conventions
established by [`mcp-ibge`](ibge.md) (see
[Architecture](../architecture.md) and [Data Sources](../data_sources.md)).

## Planned data sources

- **API do Portal da Transparência** — `https://api.portaldatransparencia.gov.br/` — despesas, contratos, convênios, sanções (CEIS, CNEP, etc.).

## Planned tools

| # | Tool | Description |
| --- | --- | --- |
| 1 | `consultar_despesas_orgao` | Consulta despesas de um órgão público por ano/mês. |
| 2 | `consultar_sancoes` | Consulta sanções administrativas (CEIS/CNEP) por CPF/CNPJ. |
| 3 | `consultar_contratos_orgao` | Lista contratos de um órgão público por ano. |
| 4 | `listar_orgaos` | Lista órgãos cadastrados no Portal da Transparência. |

None of these are implemented yet — the package currently exposes only the
shared `status` tool described in
[Architecture: adding a new module](../architecture.md#adding-a-new-module).

## Atenção — chave de API

Diferente da maioria dos módulos do `mcp-data-br`, a API do Portal da Transparência exige uma chave de acesso pessoal (gratuita, cadastrada por e-mail). Quando este módulo for implementado, a chave deve ser configurada via variável de ambiente (`MCP_TRANSPARENCIA_API_KEY` ou similar) e nunca commitada — ver [docs/security.md](../security.md).


## Conventions

Like every module in `mcp-data-br`, `mcp-transparencia` will follow:

- The shared `{"ok", "data", "metadata", "warnings", "errors"}` response
  envelope (see [data_sources.md](../data_sources.md)).
- An allowlist of official domains for outbound requests (see
  [security.md](../security.md)).
- Configuration via `pydantic-settings`, env prefix `MCP_TRANSPARENCIA_`.
- Portuguese tool-naming convention (`listar_`, `obter_`, `buscar_`,
  `consultar_`).

## See also

- [packages/mcp_transparencia/README.md](https://github.com/FilipePessoa30/mcp-data-br/blob/main/packages/mcp_transparencia/README.md)
- [docs/roadmap.md](../roadmap.md)
