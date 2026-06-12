# syntax=docker/dockerfile:1.7

# Imagem para o servidor MCP `mcp-ibge`, construída com `uv` em duas etapas:
# a etapa `builder` instala as dependências (com cache do uv) e o pacote
# `mcp-ibge` em um virtualenv; a etapa final copia apenas esse virtualenv
# para uma imagem `python:3.12-slim` enxuta, rodando como usuário não-root.
#
# Build:
#   docker build -t mcp-ibge .
#
# Uso (stdio, modo principal para clientes MCP locais):
#   docker run -i --rm mcp-ibge
#
# Uso (streamable-http, para acesso via rede/HTTP):
#   docker run --rm -p 8000:8000 \
#     -e MCP_IBGE_TRANSPORT=streamable-http \
#     mcp-ibge
#
# Veja docs/docker.md para detalhes e variáveis de ambiente.

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Copia primeiro apenas os manifests do workspace: o cache desta camada
# (e do cache do uv) é reaproveitado enquanto as dependências não mudam,
# mesmo que o código-fonte em `src/` mude.
COPY pyproject.toml ./
COPY packages/mcp_ibge/pyproject.toml packages/mcp_ibge/README.md packages/mcp_ibge/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-editable --no-install-project

# Agora copia o código-fonte e instala o pacote `mcp-ibge` em si. `--no-editable`
# grava o pacote como um wheel normal dentro de `.venv` (em vez de um link
# para `/app/packages/.../src`), já que apenas `.venv` é copiado para a
# imagem final.
COPY packages/mcp_ibge/src packages/mcp_ibge/src

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-editable


FROM python:3.12-slim AS runtime

# Usuário/grupo dedicados e não privilegiados para executar o servidor.
RUN groupadd --system --gid 1000 mcp \
    && useradd --system --uid 1000 --gid mcp --home-dir /app --shell /usr/sbin/nologin mcp

WORKDIR /app

COPY --from=builder --chown=mcp:mcp /app/.venv /app/.venv
COPY --chown=mcp:mcp docker/healthcheck.py docker/healthcheck.py

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    MCP_IBGE_TRANSPORT=stdio \
    MCP_IBGE_HOST=0.0.0.0 \
    MCP_IBGE_PORT=8000

USER mcp

# Só é usada quando MCP_IBGE_TRANSPORT=streamable-http; em stdio o container
# não escuta em nenhuma porta.
EXPOSE 8000

# Em modo stdio, o healthcheck retorna sucesso imediatamente; em modo
# streamable-http, verifica se MCP_IBGE_HOST:MCP_IBGE_PORT aceita conexões.
# Veja docker/healthcheck.py.
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["python", "docker/healthcheck.py"]

ENTRYPOINT ["mcp-ibge"]
