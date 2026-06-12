"""Servidor MCP `mcp-inep` (scaffold/planejamento).

Status: nenhuma *tool* está registrada ainda — este módulo existe para que
o pacote seja executável e testável desde já (`uv run mcp-inep`), servindo
de base para as *tools* descritas em `docs/modules/inep.md`.

Quando as primeiras *tools* forem implementadas (ver plano de versões em
`docs/modules/inep.md`), siga o padrão do `mcp-ibge`
(`tools.<dominio>_tools.register_<dominio>_tools(mcp)`).

Execução:
    python -m mcp_inep.server

Por padrão usa o transporte stdio. O transporte pode ser trocado via a
variável de ambiente `MCP_INEP_TRANSPORT` (ex.: "streamable-http"); host e
porta usados nesse modo são configuráveis via `MCP_INEP_HOST`/`MCP_INEP_PORT`.

Importante: nunca usar `print()`. Em modo stdio, stdout é reservado para o
protocolo MCP — todo log vai para stderr via `logging`.
"""

from __future__ import annotations

import logging
import sys
from typing import Literal, cast

from mcp.server.fastmcp import FastMCP

from .config import get_settings

_settings = get_settings()

mcp = FastMCP(
    "mcp-inep",
    instructions=(
        "Servidor MCP (em planejamento) para dados públicos do INEP: Censo "
        "Escolar, Ideb, Saeb, Enem, escolas por município e indicadores "
        "educacionais. Nenhuma tool está disponível nesta versão — veja "
        "docs/modules/inep.md para o roadmap e o plano de versões."
    ),
    host=_settings.host,
    port=_settings.port,
)


def main() -> None:
    """Configura logging e inicia o servidor MCP."""
    logging.basicConfig(
        level=_settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stderr,
    )
    logging.getLogger(__name__).info(
        "Iniciando mcp-inep (transporte=%s) — nenhuma tool registrada (scaffold)",
        _settings.transport,
    )
    transport = cast("Literal['stdio', 'sse', 'streamable-http']", _settings.transport)
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
