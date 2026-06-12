"""Clientes HTTP para as APIs/portais públicos do INEP (planejado).

Camada fina de acesso às fontes oficiais, seguindo o mesmo padrão do
`mcp_ibge.clients`: timeouts, allowlist de domínios
(`mcp_inep.config.ALLOWED_API_HOSTS`) e tratamento de erros sem stack trace
para o cliente MCP.

Nenhum cliente implementado ainda — ver "Fontes planejadas" e "Desafios" em
`docs/modules/inep.md` para as fontes candidatas (Censo Escolar, Ideb, Saeb,
Enem, catálogo de microdados) e as decisões pendentes sobre quais delas têm
uma API estável o suficiente para consulta direta, versus dados que
precisarão de pré-processamento (ver `mcp_inep.services`).
"""
