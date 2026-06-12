# mcp-ibge

Part of **[mcp-data-br](../../README.md)** — a collection of MCP servers for
Brazilian public data.

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

> **v0.2.0 status**: the **Localidades** tools (regions, states,
> municipalities, districts and code resolution) and the **Agregados/SIDRA**
> tools (generic discovery and query of any SIDRA aggregate) are the stable,
> fully tested core of this release. The **population indicator**
> (`consultar_populacao_municipio`) is included as an **experimental
> preview** — it works and is tested, but it depends on a fixed aggregate/
> variable that the IBGE may discontinue or rename after a new Census (see
> [Roadmap](#roadmap)).

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

## Features

- **Localidades API tools** (stable) — regions, states, municipalities and
  districts, with codes and hierarchy resolved.
- **Agregados/SIDRA tools** (stable) — generic discovery and query of any
  SIDRA aggregate: list aggregates, inspect metadata, variables, periods and
  locations, and query data.
- **SIDRA Query Builder** (new) — 7 tools to discover, explain, suggest and
  validate SIDRA queries against an aggregate's real metadata before
  querying, with **no LLM on the server** (keyword/metadata heuristics only).
- **Population indicator** (experimental) —
  `consultar_populacao_municipio`, built on top of Agregados/SIDRA.
- **Geospatial tools** (new, experimental) — municipality/state boundary
  meshes (`obter_malha_municipio`, `obter_malha_uf`) and bounding boxes
  (`obter_bbox_municipio`, `gerar_geojson_municipios`) as GeoJSON, from the
  IBGE Malhas API.
- **Municipality code resolution** — fuzzy, accent- and case-insensitive
  search from a name to the 7-digit IBGE code, with disambiguation warnings.
- **Typed JSON responses** — every tool is backed by Pydantic models.
- **Standard response envelope** — every tool returns `{"ok": ..., "data":
  ..., "metadata": {...}, "warnings": [...], "errors": [...]}`, on success and
  on failure.
- **Source metadata on every response** — `source_name`, `source_url`,
  `official_source`, `endpoint`, `params`, `retrieved_at`, `period`,
  `territorial_level`, `license_note`, `version` and `cache_hit` for full
  traceability.
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

`mcp-ibge` lives in the [`mcp-data-br`](../../README.md) uv workspace. Clone
the repository and sync the whole workspace from its root:

```bash
git clone https://github.com/FilipePessoa30/mcp-ibge.git mcp-data-br
cd mcp-data-br
uv sync --all-extras
```

Run it directly from the repository root:

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
        "/absolute/path/to/mcp-data-br",
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
      "args": ["--directory", "/absolute/path/to/mcp-data-br", "run", "mcp-ibge"]
    }
  }
}
```

### Local / development mode

Ready-to-use configs for Linux/macOS/Windows (and a list of test prompts) are
available in
[examples/claude_desktop/mcp_ibge.json](../../examples/claude_desktop/mcp_ibge.json),
[examples/cursor/mcp_ibge.json](../../examples/cursor/mcp_ibge.json) and
[docs/client_setup.md](docs/client_setup.md).

### Open WebUI

For HTTP-based clients (e.g. Open WebUI via [`mcpo`](https://github.com/open-webui/mcpo)),
start the server with the `streamable-http` transport:

```bash
MCP_IBGE_TRANSPORT=streamable-http uv run mcp-ibge
```

See [examples/open_webui/](../../examples/open_webui/) for a ready-to-use
`mcpo` config.

### Configuration

All settings have sensible defaults and can be overridden via environment
variables (prefix `MCP_IBGE_`) or a `.env` file — see
[.env.example](.env.example).

| Variable | Default | Description |
| --- | --- | --- |
| `MCP_IBGE_API_BASE_URL` | `https://servicodados.ibge.gov.br/api` | Base URL shared by the IBGE APIs. Restricted to official IBGE domains (`https://servicodados.ibge.gov.br`) — see [docs/security.md](docs/security.md). |
| `MCP_IBGE_SOURCE_NAME` | `IBGE - Instituto Brasileiro de Geografia e Estatística` | Name shown in `metadata.source_name`. |
| `MCP_IBGE_OFFICIAL_SOURCE_URL` | `https://www.ibge.gov.br/` | Institutional URL shown in `metadata.official_source`. |
| `MCP_IBGE_LICENSE_NOTE` | _(see `.env.example`)_ | License/usage note shown in `metadata.license_note`. |
| `MCP_IBGE_USER_AGENT` | `mcp-ibge/0.2.0` | `User-Agent` header used for IBGE requests. |
| `MCP_IBGE_TIMEOUT` | `30.0` | HTTP timeout (seconds) for each IBGE request. |
| `MCP_IBGE_MAX_RESPONSE_SIZE_BYTES` | `5000000` | Maximum response body size (bytes) accepted from the IBGE API. |
| `MCP_IBGE_CACHE_ENABLED` | `true` | Enable/disable the in-memory cache. |
| `MCP_IBGE_CACHE_TTL_SECONDS` | `3600.0` | Cache entry time-to-live (seconds). |
| `MCP_IBGE_CACHE_MAX_SIZE` | `256` | Maximum number of cached responses. |
| `MCP_IBGE_LOG_LEVEL` | `INFO` | Log level (`DEBUG`, `INFO`, ...); always written to stderr. |
| `MCP_IBGE_TRANSPORT` | `stdio` | MCP transport (`stdio` or `streamable-http`). |
| `MCP_IBGE_PORT` | `8000` | Port used by the `streamable-http` transport. |

## Available tools

Every tool returns the same envelope, on success or failure:
`{"ok": ..., "data": ..., "metadata": {...}, "warnings": [...], "errors": [...]}`.
`warnings`/`errors` are lists of `{"message": ..., "code": ...}` objects —
e.g. Localidades tools populate `warnings` when a search is ambiguous. See
[docs/data_sources.md](docs/data_sources.md) for the full envelope/metadata
reference, [docs/tools.md](docs/tools.md) for full argument reference, and
[examples/agent_recipes/mcp_ibge_queries.md](../../examples/agent_recipes/mcp_ibge_queries.md)
for more examples.

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

### Agregados / SIDRA

> Generic discovery and query tools for **any** SIDRA aggregate (table). See
> [docs/tools.md](docs/tools.md#como-descobrir-agregado-variável-período-e-localidade)
> for a step-by-step guide on how to discover an aggregate, its variables,
> periods and locations before calling `consultar_agregado`.

| Tool | Description | Example |
| --- | --- | --- |
| `listar_agregados` | List SIDRA aggregates (tables), filterable by survey, subject or text. | `listar_agregados(assunto="População")` |
| `obter_metadados_agregado` | Get metadata for an aggregate: survey, subject, periodicity, variables, classifications and territorial levels (full JSON in `raw`). | `obter_metadados_agregado(agregado_id="6579")` |
| `listar_variaveis_agregado` | List the variables available in an aggregate. | `listar_variaveis_agregado(agregado_id="6579")` |
| `listar_periodos_agregado` | List the periods available for an aggregate. | `listar_periodos_agregado(agregado_id="6579")` |
| `listar_localidades_agregado` | List the locations available for an aggregate at one or more territorial levels. | `listar_localidades_agregado(agregado_id="6579", niveis="N6")` |
| `consultar_agregado` | Query an aggregate's values for given variables, periods, locations and (optionally) classifications. | `consultar_agregado(agregado_id="7060", variaveis="63", localidades="N1[all]", periodos="-1", classificacao="315[7169]")` |

### Indicators (experimental)

| Tool | Description | Example |
| --- | --- | --- |
| `consultar_populacao_municipio` | Estimated resident population of a municipality, by name and state. | `consultar_populacao_municipio(nome="Niterói", uf="RJ")` |

### SIDRA Query Builder

> Discovery, suggestion and validation layer on top of Agregados/SIDRA — helps
> an agent figure out `agregado_id`, `variaveis`, `localidades`, `periodos`
> and `classificacao` without guessing. **No LLM is used on the server**:
> `sugerir_consulta_sidra` is a keyword/metadata heuristic and always returns
> a *proposal* plus `warnings` explaining it — it never executes a query. See
> [docs/tools.md](docs/tools.md#sidra-query-builder) for the full reference.

| Tool | Description | Example |
| --- | --- | --- |
| `buscar_tabelas_sidra` | Find SIDRA aggregates related to a topic, ranked by keyword match. | `buscar_tabelas_sidra(tema="população")` |
| `explicar_tabela_sidra` | Explain an aggregate: name, survey, subject, periodicity, variables, classifications and limitations. | `explicar_tabela_sidra(agregado_id="6579")` |
| `listar_variaveis_tabela_sidra` | List the variables of an aggregate (from its metadata). | `listar_variaveis_tabela_sidra(agregado_id="6579")` |
| `listar_classificacoes_tabela_sidra` | List the classifications of an aggregate (from its metadata). | `listar_classificacoes_tabela_sidra(agregado_id="7060")` |
| `sugerir_consulta_sidra` | Propose `agregado_id`/`variaveis`/`localidades` for a natural-language question, without executing it. | `sugerir_consulta_sidra(pergunta="população dos municípios em 2024")` |
| `validar_consulta_sidra` | Validate query parameters against an aggregate's real metadata before querying. | `validar_consulta_sidra(agregado_id="6579", variaveis="9324", localidades="N6[3550308]", periodos="2024")` |
| `executar_consulta_sidra_validada` | Validate, then call `consultar_agregado` only if validation passes. | `executar_consulta_sidra_validada(agregado_id="6579", variaveis="9324", localidades="N6[3550308]", periodos="2024")` |

### Perfil Municipal

| Tool | Description | Example |
| --- | --- | --- |
| `gerar_perfil_municipal` | Generate a basic municipality profile: identification (IBGE code, state, region, micro-region/intermediate region) plus available indicators (estimated population, when possible). Clearly separates obtained data (`data.indicadores`) from suggested-but-not-implemented indicators (`data.proximos_indicadores_sugeridos`). | `gerar_perfil_municipal(nome="Niterói", uf="RJ")` |

### Comparação de Municípios

| Tool | Description | Example |
| --- | --- | --- |
| `comparar_municipios` | Compare up to 10 municipalities (by name + state) on the indicators already implemented (currently, estimated population). Unresolved/ambiguous municipalities go to `data.municipios_nao_resolvidos`, and unsupported indicators go to `data.indicadores_nao_implementados` (name only, with a `warning`) — neither stops the comparison of the rest. | `comparar_municipios(municipios=[{"nome": "Rio de Janeiro", "uf": "RJ"}, {"nome": "Niterói", "uf": "RJ"}])` |

### Geoespacial (experimental)

> Municipality/state boundary meshes and bounding boxes as GeoJSON (RFC
> 7946), from the [IBGE API de Malhas](https://servicodados.ibge.gov.br/api/docs/malhas).
> By default (`simplificado=true`) tools use the simplified mesh quality
> (`qualidade=minima`) and return a `warning` noting the simplification; see
> [docs/tools.md](docs/tools.md#geoespacial) for details and response-size
> limits.

| Tool | Description | Example |
| --- | --- | --- |
| `obter_malha_municipio` | Get the GeoJSON mesh of a municipality by IBGE code. | `obter_malha_municipio(codigo_ibge=3303302)` |
| `obter_malha_uf` | Get the GeoJSON mesh of a state by abbreviation or IBGE code. | `obter_malha_uf(uf="RJ")` |
| `obter_bbox_municipio` | Get the bounding box (WGS84) of a municipality, computed from its simplified mesh. | `obter_bbox_municipio(codigo_ibge=3303302)` |
| `gerar_geojson_municipios` | Combine the simplified meshes of up to 10 municipalities into a single GeoJSON `FeatureCollection`. | `gerar_geojson_municipios(codigos_ibge=[3304557, 3303302])` |

**Resources & prompts**: `ibge://status` (server status: version, available
tools, query time) and `comparar_municipios` (a prompt that guides comparing
an indicator across municipalities using the `comparar_municipios` tool,
always citing source, period, territorial unit and limitations).

## Data sources

All data is fetched live, with no API key, from the **IBGE Serviços de
Dados** API:

- [IBGE Localidades API](https://servicodados.ibge.gov.br/api/docs/localidades)
  — regions, states, municipalities and districts.
- [IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados)
  — statistical aggregates, including censuses and population estimates.
- [IBGE API de Malhas](https://servicodados.ibge.gov.br/api/docs/malhas) —
  municipality/state boundary geometries (GeoJSON), used by the geospatial
  tools.

See [docs/data_sources.md](docs/data_sources.md) for the response envelope
format, [docs/architecture.md](docs/architecture.md) for the layered
architecture, [docs/security.md](docs/security.md) for security
considerations, and [docs/examples.md](docs/examples.md) for worked
end-to-end examples (with real JSON responses) of agents using these tools.

## Roadmap

- [x] **v0.1.0** — Localidades tools (regions, states, municipalities,
  districts, fuzzy search and code resolution): **stable**, with full test
  coverage, README, configuration examples and CI. Agregados/SIDRA tools, the
  population indicator and the `comparar_municipios` prompt were included as
  **experimental previews**.
- [x] **v0.2.0** (current) — Initial Agregados/SIDRA support promoted to
  **stable**: `listar_agregados`, `obter_metadados_agregado`,
  `listar_variaveis_agregado`, `listar_periodos_agregado`,
  `listar_localidades_agregado` and `consultar_agregado` cover generic
  discovery and query of any SIDRA aggregate, with a documented discovery
  workflow and real worked examples (see
  [docs/tools.md](docs/tools.md#como-descobrir-agregado-variável-período-e-localidade)).
  The population indicator (`consultar_populacao_municipio`) and the
  `comparar_municipios` prompt remain **experimental**.
- [ ] **v0.2.1** — Stabilize the population indicator
  (`consultar_populacao_municipio`) and the `comparar_municipios` prompt
  based on real-world usage and feedback.
- [ ] **v0.3.0** — Census helpers: dedicated tools for Census-specific
  aggregates and classifications.
- [x] **v0.4.0** — Geographic meshes: municipality/state boundary geometries
  (malhas territoriais) — included as an **experimental preview**
  (`obter_malha_municipio`, `obter_malha_uf`, `obter_bbox_municipio`,
  `gerar_geojson_municipios`), pending real-world feedback before being
  marked stable.
- [ ] **v1.0.0** — Stable MCP server: published package, stable tool
  contracts for all domains, and `streamable-http` hardened for remote
  deployments.

For the broader, multi-module roadmap, see
[docs/roadmap.md](../../docs/roadmap.md).

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

## 🇧🇷 Sobre o módulo (resumo em português)

O **mcp-ibge** é um servidor [MCP](https://modelcontextprotocol.io/), parte
do projeto [mcp-data-br](../../README.md), que expõe dados públicos e
oficiais do **IBGE** — localidades, agregados do **SIDRA** e indicadores de
**população** — como *tools* tipadas e rastreáveis para agentes de IA (Claude
Desktop, Cursor, etc.). Não requer chave de API, roda 100% local via stdio, e
toda resposta inclui metadados de fonte (`source_name`, `source_url`,
`endpoint`, `params`, `retrieved_at`) para conferência na fonte oficial. Veja
[docs/client_setup.md](docs/client_setup.md) para um guia de configuração com
perguntas de teste em português.

**Status na v0.2.0**: as *tools* de **Localidades** e o suporte inicial a
**Agregados/SIDRA** (descoberta e consulta genérica de qualquer agregado:
`listar_agregados`, `obter_metadados_agregado`, `listar_variaveis_agregado`,
`listar_periodos_agregado`, `listar_localidades_agregado` e
`consultar_agregado`) são o núcleo **estável** e totalmente testado desta
versão. O indicador de população (`consultar_populacao_municipio`) continua
**experimental** — funciona e tem testes, mas depende de um agregado e
variável fixos que o IBGE pode descontinuar/renomear após um novo Censo.

## Contributing

Contributions are welcome — bug reports, new tools, documentation and tests.
See [CONTRIBUTING.md](../../CONTRIBUTING.md) for the development setup
(uv workspace, lint/format/test commands) and guidelines.

## License

[MIT](LICENSE)

## Citation

If you use `mcp-ibge` in research, tooling or a derivative project, please
cite it and the underlying IBGE data:

```bibtex
@software{mcp_ibge,
  title   = {mcp-ibge: Model Context Protocol server for Brazilian IBGE public data},
  author  = {{mcp-data-br contributors}},
  year    = {2026},
  url     = {https://github.com/FilipePessoa30/mcp-ibge},
  license = {MIT}
}
```

Underlying data: **IBGE — Instituto Brasileiro de Geografia e Estatística**,
via [servicodados.ibge.gov.br](https://servicodados.ibge.gov.br/api/docs).
