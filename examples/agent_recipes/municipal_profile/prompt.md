# Prompt do usuário

> Me dá um perfil básico do município de Niterói, no Rio de Janeiro (RJ):
> código IBGE, região, microrregião e população estimada mais recente, com a
> fonte.

## Variações

- "Quero um resumo sobre São Paulo (SP): onde fica, qual a região e quantos
  habitantes tem hoje, segundo o IBGE."
- "Faça uma ficha do município de código IBGE 3302700." — o agente precisa
  primeiro descobrir o nome/UF (`obter_municipio_por_codigo`) antes de poder
  chamar `gerar_perfil_municipal(nome=..., uf=...)`.
- "Niterói tem mais habitantes que Maricá?" — esta pergunta é uma
  **comparação**, não um perfil; veja a receita
  [`compare_municipalities`](../compare_municipalities/).
