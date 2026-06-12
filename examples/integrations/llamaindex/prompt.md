# Prompt do usuário

> Quais são as grandes regiões do Brasil segundo o IBGE?

## Variações

- "Liste as regiões do Brasil com seus códigos IBGE."
- "Liste os estados da região Sul do Brasil." (combina `listar_regioes` e
  `listar_estados`)
- "Liste os municípios do estado do Rio de Janeiro." (`listar_municipios`)

Este exemplo usa a tool
[`listar_regioes`](../../../packages/mcp_ibge/docs/tools.md#11-listar_regioes),
que não recebe parâmetros e retorna sempre as mesmas 5 regiões — útil para
verificar rapidamente que o agente está conectado ao `mcp-ibge` e consultando
dados reais (e não "alucinando").
