# mcp-inep

Part of **[mcp-data-br](../../README.md)** — a collection of MCP servers for
Brazilian public data.

**Model Context Protocol server for Brazilian INEP education data —
planning stage.**

![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-6A5ACD)
![Status](https://img.shields.io/badge/status-planning-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

> **Status: planning / scaffold.** This package exists so the workspace
> layout, docs and roadmap are visible from day one — **no tool is
> implemented yet**. The server runs (`uv run mcp-inep`) but exposes zero
> tools. See **[docs/modules/inep.md](../../docs/modules/inep.md)** for the
> full plan: data sources, planned tools, challenges, limits and the
> version-by-version implementation roadmap.

## What will mcp-inep be?

**mcp-inep** will expose official, public data from **INEP** (Instituto
Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira — the Brazilian
institute responsible for education statistics and assessments) as typed,
traceable [MCP](https://modelcontextprotocol.io/) tools, following the same
conventions as [`mcp-ibge`](../mcp_ibge/README.md): the shared
`{"ok", "data", "metadata", "warnings", "errors"}` response envelope (see
[docs/data_sources.md](../../docs/data_sources.md)), an allowlist of
official domains, input validation before any network call, `stdio`-safe
logging, and configuration via `pydantic-settings` (`MCP_INEP_*` env vars).

## Planned data sources

- **Censo Escolar** (annual school census) — schools, enrollments,
  infrastructure.
- **Ideb** (Índice de Desenvolvimento da Educação Básica) — basic education
  development index, by school/município/UF.
- **Saeb** (Sistema de Avaliação da Educação Básica) — learning assessment
  results.
- **Enem** (Exame Nacional do Ensino Médio) — high school exam results and
  participation.
- **Catálogo de microdados do INEP** — metadata about the open microdata
  files (years, formats, sizes, URLs) for the datasets above.

See [docs/modules/inep.md](../../docs/modules/inep.md#fontes-planejadas) for
details, including why most of these don't have a simple REST API like
`servicodados.ibge.gov.br` and how that shapes the implementation plan.

## Planned tools

| # | Tool | Description |
| --- | --- | --- |
| 1 | `buscar_escolas_municipio` | List schools in a município (Censo Escolar). |
| 2 | `obter_indicadores_educacionais` | Get education indicators (e.g. Ideb) for a município/school. |
| 3 | `comparar_ideb_municipios` | Compare Ideb scores across municípios, like `mcp-ibge`'s `comparar_municipios`. |
| 4 | `listar_microdados_disponiveis` | List available INEP microdata datasets (Censo Escolar, Saeb, Enem) and years. |
| 5 | `gerar_perfil_educacional_municipal` | Generate a municipal education profile combining the indicators above. |

None of these are implemented yet — see
[docs/modules/inep.md](../../docs/modules/inep.md#tools-planejadas) for the
detailed design and [#plano-de-implementação-em-versões](../../docs/modules/inep.md#plano-de-implementação-em-versões)
for which version each tool targets.

## Package layout

```
packages/mcp_inep/
├── pyproject.toml
├── README.md            # this file
├── src/mcp_inep/
│   ├── server.py          # FastMCP instance, no tools registered yet
│   ├── config.py          # pydantic-settings (MCP_INEP_*)
│   ├── clients/            # planned: HTTP clients for INEP sources
│   ├── services/           # planned: business logic / data aggregation
│   ├── schemas/             # planned: Pydantic models
│   ├── tools/               # planned: @mcp.tool() registrations
│   └── utils/               # planned: shared helpers (cache, etc.)
└── tests/
    └── test_server.py     # scaffold test: server boots, zero tools
```

This mirrors [`mcp_ibge`](../mcp_ibge/)'s internal layering — see
[docs/architecture.md](../../docs/architecture.md#anatomy-of-a-module-package).

## Roadmap

See **[docs/modules/inep.md](../../docs/modules/inep.md)** for the full,
version-by-version plan, and
[docs/roadmap.md](../../docs/roadmap.md) for how `mcp-inep` fits into the
overall `mcp-data-br` roadmap.
