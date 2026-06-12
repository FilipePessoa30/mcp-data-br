"""Utilitários transversais: cache, normalização, erros (planejado).

Seguindo `mcp_ibge.utils`, este pacote concentra helpers compartilhados
entre `clients`, `services` e `tools` — por exemplo, um cache em memória com
TTL (`mcp_ibge.utils.cache`), normalização de nomes/UFs e tipos de erro sem
stack trace (`mcp_ibge.security.safe_error_response`).

Nada implementado ainda; quando `mcp_inep.clients`/`services` existirem,
reaproveitar os utilitários de `mcp_ibge.utils` quando possível (extraindo
para um pacote compartilhado se a duplicação for significativa) em vez de
duplicar a lógica.
"""
