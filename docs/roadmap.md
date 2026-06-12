# Roadmap

`mcp-data-br` aims to grow into a collection of focused MCP servers for
Brazilian public data sources, each independently installable and following
the same conventions (see [architecture.md](architecture.md),
[data_sources.md](data_sources.md), [security.md](security.md)).

This page tracks **modules** (new packages). For the detailed,
version-by-version roadmap of an individual module's tools, see that
module's own README (e.g.
[packages/mcp_ibge/README.md](https://github.com/FilipePessoa30/mcp-ibge/blob/main/packages/mcp_ibge/README.md#roadmap)).

## Available

- **`mcp-ibge`** — IBGE data: Localidades (regions, states, municipalities,
  districts) and Agregados/SIDRA (statistical aggregates, population
  estimates). Stable. See [Module: mcp-ibge](modules/ibge.md) and
  [packages/mcp_ibge/](https://github.com/FilipePessoa30/mcp-ibge/tree/main/packages/mcp_ibge).

## Planned

- **`mcp-sidra`** — Today, Agregados/SIDRA tools live inside `mcp-ibge`.
  As SIDRA-specific functionality grows (more aggregates, classifications,
  geographic meshes), it may be split into its own `mcp-sidra` package so
  `mcp-ibge` can stay focused on Localidades while SIDRA gets dedicated,
  more specialized tooling. No breaking changes are planned for existing
  `mcp-ibge` tools as part of this — if/when a split happens, it will be
  additive (new package, with `mcp-ibge` either re-exporting or deprecating
  gradually). See [Module: mcp-sidra (planned)](modules/sidra.md).
- **`mcp-inep`** — education data from INEP: Censo Escolar, Ideb, Saeb,
  Enem, schools by município and education indicators, combined with
  `mcp-ibge` municipality codes for municipal education profiles. A package
  scaffold (no tools yet) already exists at
  [`packages/mcp_inep/`](https://github.com/FilipePessoa30/mcp-ibge/tree/main/packages/mcp_inep)
  — see [Module: mcp-inep (planned)](modules/inep.md) for the planned tools,
  data sources, challenges and version-by-version implementation plan.
- **`mcp-dados-gov-br`** — generic access to datasets published on
  [dados.gov.br](https://dados.gov.br/), future.
- **`mcp-bcb`** — economic/financial indicators from the Banco Central do
  Brasil (e.g. SGS series, exchange rates, Selic), future.
- **`mcp-rio`** — open data from the city/state of Rio de Janeiro, future.

These are directional, not commitments with dates. The workspace structure
(see [architecture.md](architecture.md#adding-a-new-module)) is designed so
each of these can be added as a new `packages/mcp_<name>/` package without
touching existing modules.

## Cross-cutting

- **`evals/`** — build out a shared evaluation framework (datasets +
  reports) so tool quality and regressions can be tracked across modules as
  they're added. See [Evals](evals.md).
- **`examples/`** — keep client configs (Claude Desktop, Cursor, Open WebUI)
  and prompt recipes up to date as new modules land.
