# Module: mcp-inep (planned)

`mcp-inep` is a **planned** future module — package scaffold exists at
[`packages/mcp_inep/`](https://github.com/FilipePessoa30/mcp-ibge/tree/main/packages/mcp_inep)
(see its [README](https://github.com/FilipePessoa30/mcp-ibge/blob/main/packages/mcp_inep/README.md)),
but **no tool is implemented yet**. This page is the technical roadmap: what
data it will expose, which tools are planned, the challenges that make INEP
data harder to serve than IBGE's, the limits of what's realistically
achievable, and a version-by-version implementation plan.

It follows the same conventions as every other `mcp-data-br` module — the
shared response envelope ([Data Sources](../data_sources.md)), the
[Security baseline](../security.md), `stdio`-safe logging, and
`pydantic-settings`-based configuration (`MCP_INEP_*`) — see
[Architecture](../architecture.md#anatomy-of-a-module-package).

## Why INEP

[INEP](https://www.gov.br/inep/pt-br) (Instituto Nacional de Estudos e
Pesquisas Educacionais Anísio Teixeira) is the Brazilian federal agency
responsible for the country's main education statistics and assessments:
the school census, the basic education development index, national learning
assessments, and the high school exit exam. Combined with
[`mcp-ibge`](ibge.md)'s municipality codes and population data, an
`mcp-inep` module would let an agent build **education profiles per
município** — e.g. "compare the Ideb and number of schools in Niterói,
Maricá and São Gonçalo" — extending `mcp-data-br` beyond demographics and
geography into education outcomes.

## Fontes planejadas

Unlike `mcp-ibge`, which has a single well-documented REST API
(`servicodados.ibge.gov.br`), INEP's open data is mostly published as
**downloadable microdata files** (CSV/zip, often several GB per year) rather
than a query API. The planned sources, roughly from "easiest to integrate"
to "hardest":

- **[Dados Abertos do INEP](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos)**
  — the catalog/landing page for all datasets below; used as the source of
  truth for `listar_microdados_disponiveis` (dataset names, years, download
  URLs, file sizes).
- **Ideb** (Índice de Desenvolvimento da Educação Básica) — published as
  spreadsheets per edition (biennial: 2017, 2019, 2021, 2023, ...) with
  results by escola/município/UF/Brasil. Relatively small, tabular,
  well-suited to pre-processing into a compact per-município dataset.
- **Censo Escolar** (school census) — annual microdata (schools,
  enrollments, infrastructure, teaching staff), one of the largest datasets;
  schools are identified by `co_entidade` (INEP school code) and located by
  `co_municipio` (IBGE municipality code), which is the integration point
  with `mcp-ibge`.
- **Saeb** (Sistema de Avaliação da Educação Básica) — learning assessment
  microdata, biennial, large (student-level records).
- **Enem** (Exame Nacional do Ensino Médio) — exam microdata, annual, the
  largest of all (multi-GB per year, student-level).
- **[Sinopses Estatísticas](https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/censo-escolar/resultados)**
  — pre-aggregated summary tables INEP itself publishes from the Censo
  Escolar, a candidate lighter-weight source for município-level counts
  (e.g. number of schools/enrollments by município) without processing raw
  microdata.

> No endpoint URLs are allowlisted yet (`mcp_inep.config.ALLOWED_API_HOSTS`
> is empty). Confirming which of the above have stable, linkable URLs
> suitable for `metadata.source_url`/`official_source` is part of v0.2 (see
> [Plano de implementação em versões](#plano-de-implementacao-em-versoes)).

## Tools planejadas

| # | Tool | Description | Primary source(s) |
| --- | --- | --- | --- |
| 1 | `buscar_escolas_municipio` | List schools in a município (name, `co_entidade`, dependência administrativa — federal/estadual/municipal/privada, localização urbana/rural). | Censo Escolar |
| 2 | `obter_indicadores_educacionais` | Get one or more education indicators (e.g. Ideb, approval/dropout rates) for a município, school or UF, for a given edition/year. | Ideb, Saeb, Sinopses |
| 3 | `comparar_ideb_municipios` | Compare Ideb scores (anos iniciais/finais, ensino médio) across a list of municípios for a given edition — same shape as `mcp-ibge`'s [`comparar_municipios`](../tools/localidades.md). | Ideb |
| 4 | `listar_microdados_disponiveis` | List INEP microdata datasets (Censo Escolar, Saeb, Enem, Ideb) with available years, formats and approximate sizes — discovery tool, no heavy processing. | Dados Abertos INEP catalog |
| 5 | `gerar_perfil_educacional_municipal` | Generate a municipal education profile: schools (count by network/location), Ideb, and other indicators available for that município — combines tools 1-2 and cross-references `mcp-ibge` municipality codes. | Censo Escolar, Ideb, `mcp-ibge` |

All five will return the shared envelope
(`{"ok", "data", "metadata", "warnings", "errors"}`, see
[Data Sources](../data_sources.md)), with `metadata.source_name` /
`source_url` / `official_source` pointing at the specific INEP dataset and
edition/year used, and `metadata.period` set to the census/assessment year.
Tools 1, 2 and 5 will accept a município either by IBGE code or by
name+UF (resolved the same way as `mcp-ibge`'s
[`obter_codigo_municipio`](../tools/localidades.md)), so an agent doesn't
need to look up codes in two different systems.

## Desafios

- **No unified query API.** Most data above is only published as microdata
  files, not a REST API — `mcp-inep` cannot simply proxy requests like
  `mcp-ibge` does for `servicodados.ibge.gov.br`. Tools will need to read
  from **pre-processed, derived datasets** (built offline from the official
  microdata) rather than the raw files directly.
- **File sizes incompatible with the security baseline.** The
  [Security](../security.md) model enforces per-request timeouts and
  response-size limits; raw Censo Escolar/Saeb/Enem microdata files (GBs,
  often `.zip` containing fixed-width or CSV files with hundreds of columns)
  cannot be downloaded or parsed within a single tool call.
- **Annual/biennial update cadence.** Censo Escolar is annual; Ideb and Saeb
  are biennial; Enem is annual but with results published months later.
  Derived datasets need a refresh process and `metadata.period` must clearly
  state which edition/year a result refers to (data can be 1-2 years old by
  nature, not due to a bug).
- **Format/dictionary drift across years.** Column names, codes and even
  municipal/school identifiers have changed between Censo Escolar editions;
  a stable internal schema (`mcp_inep.schemas`) needs to abstract this away
  from tool consumers.
- **Encoding and licensing.** Historic INEP CSVs are often Latin-1
  (`ISO-8859-1`) and ship with their own usage notes — `metadata.license_note`
  needs dataset-specific text, not a single project-wide string like
  `mcp-ibge`'s.
- **Cross-module identifier mapping.** INEP identifies municípios by
  `co_municipio` (the IBGE 7-digit code, so directly compatible) but schools
  by `co_entidade` (INEP-specific) — `buscar_escolas_municipio` needs to
  resolve município name/UF → `co_municipio` via the same logic as
  `mcp-ibge`'s `obter_codigo_municipio`, ideally by depending on
  `mcp-ibge`'s service layer rather than duplicating it.
- **No scraping.** Per the project's [security baseline](../security.md),
  tools cannot scrape HTML pages to discover download links — the catalog
  used by `listar_microdados_disponiveis` must be a stable, directly
  linkable resource (a documented page/API/JSON catalog), confirmed during
  v0.2 research.

## Limites

Given the challenges above, `mcp-inep`'s first versions will have narrower
scope than `mcp-ibge`:

- **Município-level aggregates first, not student/school microdata.** Tools
  will expose pre-aggregated indicators per município/UF/ano, not row-level
  Saeb/Enem student records — those are out of scope for the foreseeable
  future (privacy and size).
- **`buscar_escolas_municipio` may start with a curated subset.** Until a
  reliable, allowlistable source for "schools by município" is confirmed
  (Censo Escolar microdata vs. Sinopses aggregates), this tool may launch
  with limited fields (counts by network/location) before full per-school
  listings.
- **Refresh cadence tied to INEP's publication schedule**, not real-time —
  `metadata.period` and `warnings` will make this explicit (mirroring how
  `mcp-ibge`'s `consultar_populacao_municipio` documents its dependency on a
  fixed SIDRA aggregate, see [mcp-ibge roadmap](https://github.com/FilipePessoa30/mcp-ibge/blob/main/packages/mcp_ibge/README.md#roadmap)).
- **Enem and Saeb indicators are later-stage.** They depend on the same
  derived-dataset approach as Censo Escolar/Ideb but with larger source
  files, so they're scheduled after the município-level Ideb/Censo Escolar
  tools land and the approach is validated.
- **No commitments on dates** — like the rest of [roadmap.md](../roadmap.md),
  this is directional. The version numbers below describe **order and
  scope**, not a release schedule.

## Plano de implementação em versões

- **v0.1 — Scaffold (this page).** `packages/mcp_inep/` exists with the
  standard layout (`clients/`, `services/`, `schemas/`, `tools/`, `utils/`,
  `tests/`), a `FastMCP` server with **zero tools**, `pydantic-settings`
  config (`MCP_INEP_*`), and this roadmap. Included in the workspace
  (`uv sync`), so `uv run mcp-inep` runs (and does nothing) and
  `uv run --directory packages/mcp_inep pytest` passes.
- **v0.2 — Research spike + `listar_microdados_disponiveis`.** Confirm
  authoritative, allowlistable URLs for the INEP datasets catalog and Ideb
  results; populate `mcp_inep.config.ALLOWED_API_HOSTS`; define the shared
  schemas (`co_municipio` ↔ `mcp-ibge` integration, `metadata.license_note`
  per dataset). Implement `listar_microdados_disponiveis` first — it's pure
  catalog metadata, the lowest-risk tool, and validates the
  clients/services/tools layering end-to-end.
- **v0.3 — Ideb indicators.** Build the derived per-município Ideb dataset
  (from published spreadsheets) and implement
  `obter_indicadores_educacionais` (Ideb only, for now) and
  `comparar_ideb_municipios`.
- **v0.4 — Schools by município.** Build the derived Censo Escolar dataset
  (school counts/attributes by município) and implement
  `buscar_escolas_municipio`, starting with the curated subset described in
  [Limites](#limites).
- **v0.5 — Municipal education profile.** Implement
  `gerar_perfil_educacional_municipal`, combining Ideb (v0.3) and schools
  (v0.4) for a given município, plus a `gerar_perfil_municipal`-style prompt
  (see `mcp-ibge`'s `comparar_municipios` prompt) to guide agents through
  combining `mcp-ibge` and `mcp-inep` data.
- **v1.0 — Stable core.** `listar_microdados_disponiveis`,
  `obter_indicadores_educacionais`, `comparar_ideb_municipios`,
  `buscar_escolas_municipio` and `gerar_perfil_educacional_municipal` are
  documented, tested (`pytest` + `respx`, no real network access — see
  [Security](../security.md)), and added to
  [Data Sources](../data_sources.md) and `examples/`. Saeb and Enem
  indicators, if added, extend `obter_indicadores_educacionais` without
  breaking changes.

See [Roadmap](../roadmap.md) for how `mcp-inep` fits alongside the other
planned modules (`mcp-sidra`, `mcp-dados-gov-br`, `mcp-bcb`, `mcp-rio`).
