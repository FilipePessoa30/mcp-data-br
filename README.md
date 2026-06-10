# mcp-ibge

**Model Context Protocol server for Brazilian IBGE public data.**

![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-6A5ACD)
[![CI](https://github.com/FilipePessoa30/mcp-ibge/actions/workflows/ci.yml/badge.svg)](https://github.com/FilipePessoa30/mcp-ibge/actions/workflows/ci.yml)
![License](https://img.shields.io/badge/license-MIT-green)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
![pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC?logo=pytest&logoColor=white)

**mcp-ibge** exposes official, public data from the **IBGE** (Instituto
Brasileiro de Geografia e Estatística — Brazilian Institute of Geography and
Statistics) as typed, traceable [MCP](https://modelcontextprotocol.io/) tools:
locations (regions, states, municipalities, districts), **SIDRA** statistical
aggregates, and **population** indicators — ready to be called by Claude
Desktop, Cursor and any other MCP-compatible agent.

> **v0.1.0 status**: the **Localidades** tools (regions, states,
> municipalities, districts and code resolution) are the stable, fully
> tested core of this release. **Agregados/SIDRA** tools and the population
> indicator are included as **experimental previews** — they work and are
> tested, but their interface may still change before being marked stable
> (see [Roadmap](#roadmap)).

## Quick demo

Once configured in an MCP client, just ask in natural language:

- *"What is the IBGE code for Niterói, RJ?"*
- *"List all municipalities in Rio de Janeiro state."*
- *"Search municipalities named São José."*
- *"Get metadata for an IBGE aggregate."*
- *"Query an IBGE aggregate with variables, periods and locations."*

The agent picks the right tool (`obter_codigo_municipio`,
`listar_municipios`, `buscar_municipio`, `obter_metadados_agregado`,
`consultar_agregado`, ...), calls the public IBGE API, and returns a typed
JSON response with full source metadata so the answer can be verified.

## Why this project?

- **Brazilian public data is valuable but fragmented.** IBGE publishes rich,
  free, no-API-key datasets — geographic codes, censuses, population
  estimates and hundreds of SIDRA tables — but spread across multiple
  endpoints, undocumented for LLMs, with inconsistent shapes and encodings.
- **Agents need typed, traceable and safe tools.** An LLM calling a raw HTTP
  API has no guarantee about the response shape, units, or where the data
  came from — and an ambiguous lookup (e.g. "São José") can silently return
  the wrong place.
- **This server turns IBGE APIs into MCP tools.** Every tool returns a
  validated, typed envelope with `data`/`error`, source metadata
  (`source_name`, `source_url`, `endpoint`, `params`, `retrieved_at`), and
  `warnings` for ambiguous results — so agents, and the humans reading their
  answers, can trust and verify the numbers.

## Features

- **Localidades API tools** (stable) — regions, states, municipalities and
  districts, with codes and hierarchy resolved.
- **Agregados/SIDRA tools** (experimental) — list aggregates, inspect
  metadata, variables, periods and locations, and query data.
- **Population indicator** (experimental) —
  `consultar_populacao_municipio`, built on top of Agregados/SIDRA.
- **Municipality code resolution** — fuzzy, accent- and case-insensitive
  search from a name to the 7-digit IBGE code, with disambiguation warnings.
- **Typed JSON responses** — every tool is backed by Pydantic models.
- **Source metadata on every response** — `source_name`, `source_url`,
  `endpoint`, `params` and `retrieved_at` for full traceability.
- **In-memory TTL cache** — avoids repeated calls to the IBGE API within a
  session (configurable, can be disabled).
- **Tests** — full `pytest` + `respx` suite, no network access required.
- **Local-first** — runs over stdio, no API key, no external services beyond
  the public IBGE API.

## Installation

Requires **Python 3.11+**. [uv](https://docs.astral.sh/uv/) is recommended.

### With uvx

```bash
uvx mcp-ibge
```

> While the package is not yet published to an index, use the development
> setup below and point your MCP client at the local checkout (see
> [Usage with MCP clients](#usage-with-mcp-clients)).

### Development mode

```bash
git clone https://github.com/FilipePessoa30/mcp-ibge.git
cd mcp-ibge

# Create the virtualenv and install the project + dev dependencies
uv venv
uv pip install -e ".[dev]"
# or, equivalently:
uv sync --all-extras
```

Run it directly:

```bash
uv run mcp-ibge
# or, equivalent:
uv run python -m mcp_ibge.server
```

This starts the server over **stdio** (the recommended transport for Claude
Desktop, Cursor and other local MCP clients). Logs go to **stderr** — stdout
is reserved exclusively for the MCP protocol.

## Usage with MCP clients

### Claude Desktop

Edit `claude_desktop_config.json`
(`%APPDATA%\Claude\claude_desktop_config.json` on Windows,
`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS)
and add:

```json
{
  "mcpServers": {
    "ibge": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/mcp-ibge",
        "run",
        "python",
        "-m",
        "mcp_ibge.server"
      ]
    }
  }
}
```

Restart Claude Desktop. Tools like `listar_estados`,
`obter_municipio_por_codigo` and `consultar_agregado` become available in
conversations.

### Cursor

In `Settings -> MCP -> Add new MCP Server`, or by editing
`~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "ibge": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/mcp-ibge", "run", "mcp-ibge"]
    }
  }
}
```

### Local / development mode

Ready-to-use configs for Linux/macOS/Windows (and a list of test prompts) are
available in [examples/claude_desktop_config.json](examples/claude_desktop_config.json),
[examples/cursor_config.json](examples/cursor_config.json) and
[docs/client_setup.md](docs/client_setup.md).

For HTTP-based clients (e.g. Open WebUI via [`mcpo`](https://github.com/open-webui/mcpo)),
start the server with the `streamable-http` transport:

```bash
MCP_IBGE_TRANSPORT=streamable-http uv run mcp-ibge
```

### Configuration

All settings have sensible defaults and can be overridden via environment
variables (prefix `MCP_IBGE_`) or a `.env` file — see
[.env.example](.env.example).

| Variable | Default | Description |
| --- | --- | --- |
| `MCP_IBGE_API_BASE_URL` | `https://servicodados.ibge.gov.br/api` | Base URL shared by the IBGE APIs. Restricted to official IBGE domains (`https://servicodados.ibge.gov.br`) — see [docs/security.md](docs/security.md). |
| `MCP_IBGE_SOURCE_NAME` | `IBGE - Instituto Brasileiro de Geografia e Estatística` | Name shown in `metadata.source_name`. |
| `MCP_IBGE_USER_AGENT` | `mcp-ibge/0.1.0` | `User-Agent` header used for IBGE requests. |
| `MCP_IBGE_TIMEOUT` | `30.0` | HTTP timeout (seconds) for each IBGE request. |
| `MCP_IBGE_MAX_RESPONSE_SIZE_BYTES` | `5000000` | Maximum response body size (bytes) accepted from the IBGE API. |
| `MCP_IBGE_CACHE_ENABLED` | `true` | Enable/disable the in-memory cache. |
| `MCP_IBGE_CACHE_TTL_SECONDS` | `3600.0` | Cache entry time-to-live (seconds). |
| `MCP_IBGE_CACHE_MAX_SIZE` | `256` | Maximum number of cached responses. |
| `MCP_IBGE_LOG_LEVEL` | `INFO` | Log level (`DEBUG`, `INFO`, ...); always written to stderr. |
| `MCP_IBGE_TRANSPORT` | `stdio` | MCP transport (`stdio` or `streamable-http`). |
| `MCP_IBGE_PORT` | `8000` | Port used by the `streamable-http` transport. |

## Available tools

Every tool returns `{"metadata": {...}, "data": ...}` on success or
`{"metadata": {...}, "error": "..."}` on failure. Localidades tools may also
include a `warnings` list when a search is ambiguous. See
[docs/tools.md](docs/tools.md) for full argument reference and
[examples/queries.md](examples/queries.md) for more examples.

### Localidades

| Tool | Description | Example |
| --- | --- | --- |
| `listar_regioes` | List Brazil's 5 geographic regions. | `listar_regioes()` |
| `listar_estados` | List all 26 states + the Federal District, sorted by name. | `listar_estados()` |
| `obter_estado` | Get details of a state by abbreviation or IBGE code. | `obter_estado(uf="RJ")` |
| `listar_municipios` | List the municipalities of a state, with state and region resolved. | `listar_municipios(uf="RJ")` |
| `buscar_municipio` | Fuzzy, accent/case-insensitive municipality search; returns `warnings` if ambiguous. | `buscar_municipio(nome="São José")` |
| `obter_codigo_municipio` | Get the 7-digit IBGE code for a municipality by name and state. | `obter_codigo_municipio(nome="Niterói", uf="RJ")` |
| `obter_municipio_por_codigo` | Get municipality details by IBGE code, with state and region resolved. | `obter_municipio_por_codigo(codigo_ibge=3303302)` |
| `listar_distritos` | List the districts of a municipality by IBGE code. | `listar_distritos(codigo_municipio=3304557)` |

### Agregados / SIDRA (experimental)

> These tools are functional and tested, but their interface may still
> change in a future release before being marked stable.

| Tool | Description | Example |
| --- | --- | --- |
| `listar_agregados` | List SIDRA aggregates (tables), filterable by survey, subject or text. | `listar_agregados(assunto="População")` |
| `obter_metadados_agregado` | Get metadata for an aggregate: survey, subject, periodicity (full JSON in `raw`). | `obter_metadados_agregado(agregado_id="6579")` |
| `listar_variaveis_agregado` | List the variables available in an aggregate. | `listar_variaveis_agregado(agregado_id="6579")` |
| `listar_periodos_agregado` | List the periods available for an aggregate. | `listar_periodos_agregado(agregado_id="6579")` |
| `listar_localidades_agregado` | List the locations available for an aggregate at one or more territorial levels. | `listar_localidades_agregado(agregado_id="6579", niveis="N6")` |
| `consultar_agregado` | Query an aggregate's values for given variables, periods and locations. | `consultar_agregado(agregado_id="6579", variaveis="9324", periodos="-1", localidades="N6[3303302]")` |

### Indicators (experimental)

| Tool | Description | Example |
| --- | --- | --- |
| `consultar_populacao_municipio` | Estimated resident population of a municipality, by name and state. | `consultar_populacao_municipio(nome="Niterói", uf="RJ")` |

**Resources & prompts**: `ibge://status` (server status: version, available
tools, query time) and `comparar_municipios` (a prompt that guides comparing
an indicator across municipalities, always citing source, period, territorial
unit and limitations).

## Data sources

All data is fetched live, with no API key, from the **IBGE Serviços de
Dados** API:

- [IBGE Localidades API](https://servicodados.ibge.gov.br/api/docs/localidades)
  — regions, states, municipalities and districts.
- [IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados)
  — statistical aggregates, including censuses and population estimates.

See [docs/data_sources.md](docs/data_sources.md) for the response envelope
format, [docs/architecture.md](docs/architecture.md) for the layered
architecture, and [docs/security.md](docs/security.md) for security
considerations.

## Roadmap

- [x] **v0.1.0** (current) — Localidades tools (regions, states,
  municipalities, districts, fuzzy search and code resolution): **stable**,
  with full test coverage, README, configuration examples and CI.
  Agregados/SIDRA tools, the population indicator and the
  `comparar_municipios` prompt are included as **experimental previews**.
- [ ] **v0.2.0** — Stabilize Agregados/SIDRA tools and the population
  indicator (promote from experimental to stable) based on real-world usage
  and feedback.
- [ ] **v0.3.0** — Census helpers: dedicated tools for Census-specific
  aggregates and classifications.
- [ ] **v0.4.0** — Geographic meshes: municipality/state boundary geometries
  (malhas territoriais).
- [ ] **v1.0.0** — Stable MCP server: published package, stable tool
  contracts for all domains, and `streamable-http` hardened for remote
  deployments.

## Limitations

- **Does not replace official validation.** Always check `metadata` (source,
  endpoint, retrieval time, parameters) and any `warnings` against the
  official IBGE sources before using the data in reports or decisions.
- **Some aggregates require SIDRA knowledge.** `consultar_agregado` mirrors
  the SIDRA query syntax (variables, periods, locations, classifications);
  use `listar_agregados`, `obter_metadados_agregado`,
  `listar_variaveis_agregado`, `listar_periodos_agregado` and
  `listar_localidades_agregado` to discover valid IDs first.
- **Changes to the IBGE API may require adjustments.** This server depends on
  `servicodados.ibge.gov.br`; outages, schema changes, or aggregates
  discontinued/renamed after a new Census can affect responses and may
  require updates to this project.

## 🇧🇷 Sobre o projeto (resumo em português)

O **mcp-ibge** é um servidor [MCP](https://modelcontextprotocol.io/) que
expõe dados públicos e oficiais do **IBGE** — localidades, agregados do
**SIDRA** e indicadores de **população** — como *tools* tipadas e
rastreáveis para agentes de IA (Claude Desktop, Cursor, etc.). Não requer
chave de API, roda 100% local via stdio, e toda resposta inclui metadados de
fonte (`source_name`, `source_url`, `endpoint`, `params`, `retrieved_at`) para
conferência na fonte oficial. Veja [docs/client_setup.md](docs/client_setup.md)
para um guia de configuração com perguntas de teste em português.

**Status na v0.1.0**: as *tools* de **Localidades** são o núcleo estável e
totalmente testado desta versão. As *tools* de **Agregados/SIDRA** e o
indicador de população são entregues como **experimentais** — funcionam e
têm testes, mas a interface ainda pode mudar antes de serem marcadas como
estáveis.

## Contributing

Contributions are welcome — bug reports, new tools, documentation and tests.

```bash
git clone https://github.com/FilipePessoa30/mcp-ibge.git
cd mcp-ibge
uv sync --all-extras

# Lint & format
uv run ruff check .
uv run ruff format .

# Tests (no network required — IBGE responses are mocked with respx)
uv run pytest

# Optional type checking
uv run mypy
```

CI ([.github/workflows/ci.yml](.github/workflows/ci.yml)) runs `uv sync`,
`ruff check`, `ruff format --check` and `pytest` on every push/PR; `mypy`
runs as an optional, non-blocking step.

### Project layout

```
mcp-ibge/
├── src/mcp_ibge/
│   ├── server.py        # FastMCP wiring, tool registration, `main()` entrypoint
│   ├── config.py         # Settings (pydantic-settings): URLs, timeouts, cache
│   ├── logging_config.py # stderr logging (stdio-safe)
│   ├── clients/           # Thin HTTP layer (base, localidades, agregados)
│   ├── schemas/           # Pydantic models and the response envelope
│   ├── services/          # Business logic (filters, aliases, indicators)
│   ├── tools/              # FastMCP tools (`@mcp.tool()`)
│   └── utils/              # cache, text normalization, exceptions
├── tests/                  # Unit tests (pytest + respx)
├── examples/               # Example MCP client configs and queries
└── docs/                   # Architecture, tools reference, data sources, security
```

See [docs/architecture.md](docs/architecture.md) for a detailed description
of each layer and the request flow.

## License

[MIT](LICENSE)

## Citation

If you use `mcp-ibge` in research, tooling or a derivative project, please
cite it and the underlying IBGE data:

```bibtex
@software{mcp_ibge,
  title   = {mcp-ibge: Model Context Protocol server for Brazilian IBGE public data},
  author  = {{mcp-ibge contributors}},
  year    = {2026},
  url     = {https://github.com/FilipePessoa30/mcp-ibge},
  license = {MIT}
}
```

Underlying data: **IBGE — Instituto Brasileiro de Geografia e Estatística**,
via [servicodados.ibge.gov.br](https://servicodados.ibge.gov.br/api/docs).
