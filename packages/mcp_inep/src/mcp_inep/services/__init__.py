"""Lógica de negócio: validação, filtragem, agregação e cruzamento de dados (planejado).

Seguindo `mcp_ibge.services`, esta camada é testável sem o protocolo MCP e
não conhece `FastMCP` — recebe parâmetros já validados de `mcp_inep.tools` e
devolve dados tipados (`mcp_inep.schemas`) usando `mcp_inep.clients` e/ou
datasets derivados.

Nenhum serviço implementado ainda. Dado que boa parte dos dados do INEP é
publicada como microdados grandes (Censo Escolar, Saeb, Enem) sem uma API de
consulta direta, esta camada é onde a estratégia de
pré-processamento/agregação (ver "Desafios" e "Limites" em
`docs/modules/inep.md`) será concentrada — por exemplo, carregando datasets
derivados (indicadores por município/ano) já agregados offline, em vez de
processar microdados em tempo de requisição.
"""
