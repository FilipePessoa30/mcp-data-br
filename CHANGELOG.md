# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
