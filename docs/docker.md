# Docker

`mcp-ibge` ships a `Dockerfile` and `docker-compose.yml` at the repository
root so the server can run in an isolated environment without installing
Python or `uv` on the host.

## Image

The image is built in two stages:

1. **`builder`** (`ghcr.io/astral-sh/uv:python3.12-bookworm-slim`) installs
   the workspace dependencies and the `mcp-ibge` package with
   [`uv sync`](https://docs.astral.sh/uv/), using a build cache mount so
   repeated builds are fast.
2. **`runtime`** (`python:3.12-slim`) copies only the resulting virtualenv
   (`/app/.venv`) — no `uv`, build tools or source checkout end up in the
   final image — and runs the server as a dedicated, non-root user (`mcp`,
   uid/gid `1000`).

Build it from the repository root:

```bash
docker build -t mcp-ibge .
```

## Running in `stdio` mode (default, for local MCP clients)

`stdio` is the main transport — the server talks MCP over its
stdin/stdout, so it must run **attached and interactive** (`-i`), not
detached:

```bash
docker run -i --rm mcp-ibge
```

To point Claude Desktop, Cursor or another local MCP client at the
container, use `docker run -i --rm` as the client's `command`:

```json
{
  "mcpServers": {
    "ibge": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "mcp-ibge"]
    }
  }
}
```

> No ports need to be published for `stdio` — the container does not listen
> on the network in this mode.

## Running in `streamable-http` mode

Set `MCP_IBGE_TRANSPORT=streamable-http` and publish the port
(`MCP_IBGE_PORT`, default `8000`). The image already sets
`MCP_IBGE_HOST=0.0.0.0` by default, so the server accepts connections from
outside the container:

```bash
docker run --rm -p 8000:8000 \
  -e MCP_IBGE_TRANSPORT=streamable-http \
  mcp-ibge
```

Or with Docker Compose (`docker-compose.yml` is preconfigured for this
mode):

```bash
docker compose up -d
docker compose logs -f
```

`streamable-http` is intended for **local/trusted use** — treat it like any
other local network service and don't expose it publicly without
authentication/proxying (see
[Security — Transports](security.md#transports)). It is commonly used to
front the server with [`mcpo`](https://github.com/open-webui/mcpo) for
[Open WebUI](clients/open-webui.md).

## Healthcheck

The image declares a `HEALTHCHECK` that runs
[`docker/healthcheck.py`](https://github.com/FilipePessoa30/mcp-ibge/blob/main/docker/healthcheck.py):

- In `stdio` mode, there is no port to probe, so the healthcheck returns
  success immediately.
- In `streamable-http` mode, it opens a TCP connection to
  `MCP_IBGE_HOST:MCP_IBGE_PORT` and reports unhealthy if the server isn't
  accepting connections.

Check the container's health status with:

```bash
docker ps --format '{{.Names}}\t{{.Status}}'
```

## Environment variables

All settings from
[`packages/mcp_ibge/.env.example`](https://github.com/FilipePessoa30/mcp-ibge/blob/main/packages/mcp_ibge/.env.example)
work inside the container, either via `-e` flags, an `--env-file`, or
Compose's `environment`/`env_file`. The most relevant ones for Docker:

| Variable | Default in image | Description |
| --- | --- | --- |
| `MCP_IBGE_TRANSPORT` | `stdio` | `stdio` (default, for local MCP clients) or `streamable-http`. |
| `MCP_IBGE_HOST` | `0.0.0.0` | Bind address for `streamable-http`. The image overrides the library default (`127.0.0.1`) so the published port is reachable from outside the container. |
| `MCP_IBGE_PORT` | `8000` | Port for `streamable-http` — must match the `EXPOSE`d / published port. |
| `MCP_DATA_BR_ENABLE_CACHE` / `MCP_IBGE_CACHE_ENABLED` | `true` | Enable/disable the in-memory cache. |
| `MCP_DATA_BR_CACHE_TTL_SECONDS` / `MCP_IBGE_CACHE_TTL_SECONDS` | `3600.0` | Cache entry time-to-live (seconds). |
| `MCP_DATA_BR_LOG_LEVEL` / `MCP_IBGE_LOG_LEVEL` | `INFO` | Log level; always written to `stderr` as structured JSON lines. |

See [Installation — Configuration](installation.md#configuration) for the
full list of `MCP_IBGE_*` variables (API base URL, timeouts, metadata
strings, etc.).

To override variables without editing `docker-compose.yml`, create a `.env`
file in the repository root (Compose reads it automatically) or pass
`--env-file` to `docker run`:

```bash
docker run -i --rm --env-file .env mcp-ibge
```

## Trying the CLI in the container

The [`mcp-data-br` CLI](https://github.com/FilipePessoa30/mcp-ibge/blob/main/packages/mcp_ibge/README.md#cli-mcp-data-br)
is also installed in the image. Override the entrypoint to run a one-off
command instead of the server:

```bash
docker run --rm --entrypoint mcp-data-br mcp-ibge ibge estados --pretty
```
