"""Healthcheck do container `mcp-ibge`, usado pelo `HEALTHCHECK` do Dockerfile.

Em modo `stdio` (o padrão) não há porta TCP para verificar — o transporte
fala o protocolo MCP via stdin/stdout do processo, então o healthcheck
retorna sucesso imediatamente (o container roda em foreground e qualquer
falha real do processo já é reportada pelo próprio Docker).

Em modo `streamable-http` (`MCP_IBGE_TRANSPORT=streamable-http`), verifica se
o servidor está aceitando conexões TCP em `MCP_IBGE_HOST:MCP_IBGE_PORT`.
"""

from __future__ import annotations

import os
import socket
import sys


def main() -> int:
    transport = os.environ.get("MCP_IBGE_TRANSPORT", "stdio")
    if transport != "streamable-http":
        return 0

    host = os.environ.get("MCP_IBGE_HOST", "127.0.0.1")
    port = int(os.environ.get("MCP_IBGE_PORT", "8000"))

    try:
        with socket.create_connection((host, port), timeout=3):
            return 0
    except OSError:
        return 1


if __name__ == "__main__":
    sys.exit(main())
