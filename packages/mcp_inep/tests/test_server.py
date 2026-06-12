"""Testes do scaffold do `mcp-inep`.

Cobre apenas o que existe nesta versão: o servidor inicializa com a
instância `FastMCP` e nenhuma tool registrada. Os testes das *tools*
planejadas (ver `docs/modules/inep.md`) serão adicionados junto com cada
implementação.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_inep.server import mcp


def test_mcp_instance() -> None:
    assert isinstance(mcp, FastMCP)
    assert mcp.name == "mcp-inep"


async def test_no_tools_registered_yet() -> None:
    tools = await mcp.list_tools()
    assert tools == []
