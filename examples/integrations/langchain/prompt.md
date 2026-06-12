# Prompt do usuário

> Compare a população estimada de Niterói e Maricá (RJ).

## Variações

- "Qual cidade é maior, Niterói ou Maricá?"
- "Compare Rio de Janeiro, Niterói e Maricá por população."
- "Qual a população estimada de Niterói em 2022?" (passa `ano=2022` para
  `comparar_municipios`)

Todas usam a tool
[`comparar_municipios`](../../../packages/mcp_ibge/docs/tools.md#23-comparar_municipios),
que aceita de 2 a 10 municípios e, por padrão, compara o indicador
`"populacao_estimada"`.
