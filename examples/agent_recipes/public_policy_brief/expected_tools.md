# Tools esperadas

1. **`gerar_perfil_municipal`** — identificação + população do período mais
   recente:

```python
gerar_perfil_municipal(nome="Maricá", uf="RJ")
```

> Da resposta, anote `data.municipio.codigo_ibge` (`3302700` para Maricá) —
> será usado no passo 3.

2. **`listar_periodos_agregado`** (opcional) — confirma quais períodos estão
   disponíveis no agregado de população antes de pedir a série histórica:

```python
listar_periodos_agregado(agregado_id="6579")
```

3. **`consultar_agregado`** — série histórica da população estimada (últimos
   5 períodos):

```python
consultar_agregado(
    agregado_id="6579",
    variaveis="9324",
    localidades="N6[3302700]",
    periodos="-5",
)
```

> Para um intervalo explícito (ex.: "entre 2020 e 2024"), use
> `periodos="2020-2024"` em vez de `"-5"`.

## Internamente (não precisa ser chamado de novo pelo agente)

`gerar_perfil_municipal` já chama `obter_codigo_municipio`,
`obter_municipio_por_codigo` e `consultar_populacao_municipio` — não repita
manualmente.

## Antes de montar a série/gráfico

Verifique cada item de `consultar_agregado(...)["data"]`: se algum `valor`
vier `null` (dado ausente/sigiloso no SIDRA), **não interpole nem estime** —
reporte a lacuna explicitamente no brief (ex.: "dado não disponível para
2021").

## Se o usuário pedir um indicador não suportado (ex.: "PIB per capita")

Não chame `consultar_agregado` "adivinhando" um agregado de PIB. Explique que
esse indicador não está implementado em `gerar_perfil_municipal`/
`comparar_municipios` nesta versão e, se o usuário quiser investigar,
encaminhe para [`sidra_query_discovery`](../sidra_query_discovery/) — sem
garantir de antemão que um agregado adequado exista.

## Para comparar múltiplos municípios no mesmo brief

Use [`comparar_municipios`](../../../packages/mcp_ibge/docs/tools.md#23-comparar_municipios)
(veja [`compare_municipalities`](../compare_municipalities/)) em vez de
chamar `gerar_perfil_municipal` várias vezes.
