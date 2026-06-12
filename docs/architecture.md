# Architecture

`mcp-data-br` is a [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/)
(monorepo): one repository, one shared virtual environment, multiple
independently publishable Python packages — one per MCP server.

```
mcp-data-br/
├── pyproject.toml          # Workspace root (virtual project, not published)
├── packages/
│   ├── mcp_ibge/            # mcp-ibge: IBGE Localidades + Agregados/SIDRA
│   │   ├── pyproject.toml    # Publishable package (PyPI: mcp-ibge)
│   │   ├── src/mcp_ibge/      # server.py, config.py, clients/, services/, schemas/, tools/, utils/
│   │   ├── tests/
│   │   ├── docs/               # Module-specific docs
│   │   └── README.md
│   └── mcp_inep/            # mcp-inep: INEP education data (planning, no tools yet)
│       ├── pyproject.toml    # Publishable package (PyPI: mcp-inep)
│       ├── src/mcp_inep/      # server.py, config.py, clients/, services/, schemas/, tools/, utils/
│       ├── tests/
│       └── README.md
├── docs/                    # Monorepo-level docs (this directory)
├── examples/                # MCP client configs and prompts, shared across modules
└── evals/                   # Evaluation datasets and reports, shared across modules
```

## The workspace root

The root `pyproject.toml` declares `mcp-data-br` as a **virtual project**
(`[tool.uv] package = false`): it is never built or published itself. Its
only jobs are:

1. List `packages/*` as workspace members (`[tool.uv.workspace]`).
2. Depend on those members (`[project.dependencies]`,
   `[tool.uv.sources]`) so `uv sync` installs every module — and its console
   scripts, like `mcp-ibge` — into one shared `.venv` at the repo root.

This means `uv run mcp-ibge` and `uv run python -m mcp_ibge.server` work
from the repository root without any `--package` flags, while each module
under `packages/` remains a normal, independently publishable Python package
with its own `pyproject.toml`, version, and PyPI entry.

## Anatomy of a module package

Every module under `packages/` is a self-contained MCP server. `mcp_ibge` is
the reference implementation — see
[packages/mcp_ibge/docs/architecture.md](https://github.com/FilipePessoa30/mcp-ibge/blob/main/packages/mcp_ibge/docs/architecture.md)
for its internal layering (`clients/` → `services/` → `tools/`, schemas,
utils). New modules (e.g. a future `mcp-sidra` or `mcp-inep`) are expected to
follow the same internal shape:

- **`clients/`** — thin HTTP layer for the upstream public API, with a
  validated host allowlist.
- **`schemas/`** — Pydantic models for the data and for the response
  envelope (see [data_sources.md](data_sources.md)).
- **`services/`** — business logic: validation, filtering, lookups —
  testable without the MCP protocol.
- **`tools/`** — `@mcp.tool()` registrations; the only layer that knows
  about FastMCP and the envelope format.
- **`utils/`** — cross-cutting helpers (cache, normalization, error types).
- **`tests/`** — `pytest` + `respx`, no real network access.
- **`docs/`** — module-specific tools reference, architecture, security and
  data source notes.
- **`README.md`** — what the module does, installation, available tools.

## Conventions shared across modules

- **Response envelope**: every tool returns
  `{"ok": ..., "data": ..., "metadata": {...}, "warnings": [...], "errors": [...]}`,
  the same shape on success or failure — see [data_sources.md](data_sources.md).
- **Security baseline**: no shell execution, no local file access beyond
  config loading, no arbitrary URLs, an allowlist of upstream API hosts,
  input validation before any network call, timeouts and response size
  limits — see [security.md](security.md).
- **stdio-safe logging**: all logs go to `stderr`; `stdout` is reserved for
  the MCP protocol.
- **Configuration via env vars**: `pydantic-settings`, prefixed per module
  (e.g. `MCP_IBGE_*`).

## Adding a new module

1. Create `packages/mcp_<name>/` following the layout above (it's
   automatically picked up by `[tool.uv.workspace] members = ["packages/*"]`).
2. Add it to the root `pyproject.toml` `dependencies` and
   `[tool.uv.sources]` so `uv sync` installs it.
3. Add module docs under `packages/mcp_<name>/docs/` and a module README.
4. Add example client configs under `examples/` and update
   [roadmap.md](roadmap.md).
