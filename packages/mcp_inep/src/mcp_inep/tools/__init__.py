"""Registro das *tools* MCP do `mcp-inep` (planejado).

Seguindo `mcp_ibge.tools`, cada arquivo deste pacote expõe uma função
`register_<dominio>_tools(mcp: FastMCP)` chamada por `mcp_inep.server`, e é
a única camada que conhece o `FastMCP` e o envelope de resposta
(`{"ok", "data", "metadata", "warnings", "errors"}`, ver
`docs/data_sources.md`).

Nenhuma tool registrada ainda — `mcp_inep.server` roda com uma instância
`FastMCP` vazia. As 5 tools planejadas (`buscar_escolas_municipio`,
`obter_indicadores_educacionais`, `comparar_ideb_municipios`,
`listar_microdados_disponiveis`, `gerar_perfil_educacional_municipal`) e o
plano de versões em que cada uma será implementada estão documentados em
`docs/modules/inep.md`.
"""
