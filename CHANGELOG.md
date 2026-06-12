# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **SIDRA Query Builder** (`mcp_ibge.sidra` + `services/sidra_service.py` +
  `tools/sidra_tools.py`): 7 new tools to discover, explain, suggest and
  validate SIDRA queries against an aggregate's real metadata before
  spending a data request — `buscar_tabelas_sidra`, `explicar_tabela_sidra`,
  `listar_variaveis_tabela_sidra`, `listar_classificacoes_tabela_sidra`,
  `sugerir_consulta_sidra`, `validar_consulta_sidra` and
  `executar_consulta_sidra_validada`. They reuse `AgregadosClient`/
  `AgregadosService` (no duplicated HTTP logic) and the existing
  `mcp_ibge.utils.validators`.
  - `sugerir_consulta_sidra` **never executes a query** and **uses no LLM**:
    it ranks aggregates/variables by keyword overlap with the question
    (`mcp_ibge.sidra.suggestions`) and always returns `warnings` explaining
    the heuristic, plus alternative aggregates when relevant.
  - `validar_consulta_sidra` checks parameter *format* (existing validators)
    and then whether `variaveis`/`localidades`/`periodos`/`classificacao`
    actually exist in the aggregate's metadata
    (`mcp_ibge.sidra.query_builder.validar_consulta`), returning `avisos` for
    non-fatal issues (e.g. a period outside the known range).
  - `executar_consulta_sidra_validada` runs the same validation and only
    calls `consultar_agregado` if it passes — no data request is made for an
    invalid query.
  - Every response includes `metadata.source_url`/`endpoint`/`params`, same
    as all other tools. See
    [docs/tools.md](packages/mcp_ibge/docs/tools.md#sidra-query-builder).

- **Stronger input validation** (`mcp_ibge.utils.validators`, renamed from
  `utils.validation`): `validate_variaveis` (SIDRA variable IDs, e.g.
  `"93"`, `"93|1000093"`, or `"all"`) and `validate_limit` (pagination limit,
  1-100) are new; `validate_periodos` now also accepts `"|"`-separated
  periods (e.g. `"2020|2021|2022"`) in addition to `","`, and
  `validate_niveis` now accepts territorial-level compositions like
  `"N3[33]"` or `"N3[33,35]"`. All validators raise `IBGEValidationError`
  with clear messages before any network call. `AgregadosClient.query_agregado`
  now validates `variaveis`, and `LocalidadesService.buscar_municipio` now
  validates `limite` (1-100), on top of the existing tool-level
  `Field(ge=1, le=50)`. See [docs/security.md](packages/mcp_ibge/docs/security.md#5-validação-de-entrada-uf-município-agregado-variável-período-nível-limite).

### Changed

- **BREAKING: standardized response envelope for all `mcp-ibge` tools.**
  Every tool (Localidades and Agregados/SIDRA) now returns the same JSON
  shape on success **and** on failure:
  `{"ok": ..., "data": ..., "metadata": {...}, "warnings": [...], "errors": [...]}`.
  Previously, success responses were `{"metadata": {...}, "data": ...}` and
  error responses were `{"metadata": {...}, "error": "..."}`.
  - `metadata` (`SourceMetadata`) gained four new fields:
    `official_source`, `period`, `territorial_level`, `license_note`,
    `version` and `cache_hit` (in addition to the existing `source_name`,
    `source_url`, `endpoint`, `params`, `retrieved_at`).
  - `warnings` and `errors` are now lists of `{"message": ..., "code": ...}`
    objects (instead of a list of strings / a single string), and are always
    present (even when empty).
  - New settings `MCP_IBGE_OFFICIAL_SOURCE_URL` and `MCP_IBGE_LICENSE_NOTE`
    control `metadata.official_source` and `metadata.license_note`.
  - See [docs/data_sources.md](docs/data_sources.md) for the full envelope
    reference.
- **Repository restructured as `mcp-data-br`**, a uv workspace (monorepo)
  for a growing collection of MCP servers for Brazilian public data. The
  `mcp-ibge` server itself is unchanged (no version bump) — only its
  location and surrounding docs/examples moved:
  - Source, tests, and the package's `pyproject.toml` moved to
    `packages/mcp_ibge/`.
  - Module-specific docs moved to `packages/mcp_ibge/docs/`; new
    monorepo-level docs added under `docs/` (architecture, roadmap,
    security, data sources — shared conventions for all current and future
    modules).
  - Example MCP client configs reorganized under `examples/` into
    `claude_desktop/`, `cursor/`, `open_webui/` (new) and `agent_recipes/`.
  - Added `evals/` as a placeholder for future evaluation datasets/reports.
  - `uv run mcp-ibge` and `uv run python -m mcp_ibge.server` continue to
    work unchanged from the repository root.

## [0.2.0] - 2026-06-10

Initial **Agregados/SIDRA** support, promoted to stable. Focus: generic
discovery and query of any SIDRA aggregate, with documentation on how to find
the right IDs and real worked examples.

### Added

- **Agregados/SIDRA tools promoted to stable**: `listar_agregados`,
  `obter_metadados_agregado`, `listar_variaveis_agregado`,
  `listar_periodos_agregado`, `listar_localidades_agregado` and
  `consultar_agregado` are now considered stable, with full test coverage
  (clients, services, tools and schemas, all mocked with `respx`).
- **Discovery guide** in `docs/tools.md`
  ("Como descobrir agregado, variável, período e localidade"): a step-by-step
  workflow (`listar_agregados` → `obter_metadados_agregado` →
  `listar_variaveis_agregado` → `listar_periodos_agregado` →
  `listar_localidades_agregado` → `consultar_agregado`), including how to
  read `nivelTerritorial` and `classificacoes` from `obter_metadados_agregado`.
- **Real worked example**: end-to-end discovery and query of the IPCA
  monthly variation (aggregate `7060`, variable `63`, classification
  `315[7169]`, level `N1`) added to `docs/tools.md` and
  `examples/queries.md`, alongside the existing population estimates example
  (aggregate `6579`).

### Changed

- README and `docs/tools.md` updated: the 6 core Agregados/SIDRA tools are no
  longer marked "experimental". `consultar_populacao_municipio` and the
  `comparar_municipios` prompt remain **experimental**, since they depend on
  a fixed aggregate/variable that the IBGE may discontinue or rename after a
  new Census.
- `User-Agent` default bumped to `mcp-ibge/0.2.0`.

### Known limitations

- `consultar_populacao_municipio` and the `comparar_municipios` prompt remain
  **experimental** (see [Roadmap](README.md#roadmap)).
- The `streamable-http` transport is suitable for local/trusted use; it has
  not yet been hardened for public/remote deployments (see
  [docs/security.md](docs/security.md)).

## [0.1.0] - 2026-06-10

Initial public release. Focus: a stable, fully tested **Localidades** MCP
server, with **Agregados/SIDRA** tools and a population indicator included
as experimental previews.

### Added

- **Localidades tools (stable)**:
  - `listar_regioes` — list Brazil's 5 geographic regions.
  - `listar_estados` — list all 26 states + the Federal District.
  - `obter_estado` — get a state by abbreviation or IBGE code.
  - `listar_municipios` — list the municipalities of a state, with state and
    region resolved.
  - `buscar_municipio` — fuzzy, accent- and case-insensitive municipality
    search, with `warnings` for ambiguous results.
  - `obter_codigo_municipio` — resolve a municipality name + UF to its
    7-digit IBGE code.
  - `obter_municipio_por_codigo` — get municipality details by IBGE code.
  - `listar_distritos` — list the districts of a municipality by IBGE code.
- **Agregados/SIDRA tools (experimental)**: `listar_agregados`,
  `obter_metadados_agregado`, `listar_variaveis_agregado`,
  `listar_periodos_agregado`, `listar_localidades_agregado`,
  `consultar_agregado`.
- **Population indicator (experimental)**: `consultar_populacao_municipio`.
- **`comparar_municipios` prompt** and **`ibge://status`** resource.
- **Typed response envelope** (`{"metadata": {...}, "data": ...}` /
  `{"metadata": {...}, "error": "..."}`) with full source metadata
  (`source_name`, `source_url`, `endpoint`, `params`, `retrieved_at`) on
  every tool response.
- **In-memory TTL cache** to avoid repeated calls to the IBGE API
  (configurable via `MCP_IBGE_CACHE_*`, can be disabled).
- **Input validation module** (`utils/validation.py`) with `validate_uf`,
  `validate_municipality_code`, `validate_agregado_id`, `validate_periodos`
  and `validate_niveis` — all parameters are validated before any network
  call.
- **Domain allowlist** for `MCP_IBGE_API_BASE_URL`: only `https://` URLs to
  `servicodados.ibge.gov.br` are accepted; the server refuses to start
  otherwise.
- **Response size limit** (`MCP_IBGE_MAX_RESPONSE_SIZE_BYTES`, default 5 MB):
  oversized IBGE responses are aborted instead of being fully buffered.
- **Configurable timeout** (`MCP_IBGE_TIMEOUT`) for every IBGE request.
- **stdio-safe logging**: all logs go to `stderr`, never `stdout`, so the MCP
  protocol channel is never corrupted.
- **Structured error handling**: network/HTTP errors are translated into
  `IBGEClientError` subclasses and surfaced to the MCP client as informative
  messages, without leaking stack traces.
- **Documentation**: complete `README.md`, `docs/tools.md` (full reference
  for all 14 tools), `docs/architecture.md`, `docs/data_sources.md`,
  `docs/security.md`, `docs/client_setup.md`, and example MCP client configs
  in `examples/`.
- **Test suite**: `pytest` + `respx` (no network access required), covering
  clients, services, tools, schemas, validation, configuration and error
  handling.
- **CI**: GitHub Actions workflow running `ruff check`, `ruff format --check`,
  `pytest`, and an optional `mypy` step on every push/PR.
- **MIT license** and a `pyproject.toml` ready for publication to PyPI.

### Known limitations

- Agregados/SIDRA tools and `consultar_populacao_municipio` are
  **experimental**: they are functional and tested, but their parameters and
  output shape may still change in a future release before being marked
  stable.
- The `streamable-http` transport is suitable for local/trusted use; it has
  not yet been hardened for public/remote deployments (see
  [docs/security.md](docs/security.md)).
