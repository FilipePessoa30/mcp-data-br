# Prompt do usuário

> Qual é o código IBGE do município de Niterói, no Rio de Janeiro?

## Variações

- "Qual o código IBGE de Maricá, RJ?"
- "Liste os municípios do estado do Rio de Janeiro."
- "Busque municípios chamados 'Niterói' no Brasil."

Todas essas variações usam apenas tools de
[Localidades](../../../packages/mcp_ibge/docs/tools.md) (`obter_codigo_municipio`,
`listar_municipios`, `buscar_municipio`) — não dependem de SIDRA/Agregados,
então respondem rapidamente mesmo com modelos locais pequenos.
