# Example: Compare Municipalities

Compare Rio de Janeiro, Niterói and Maricá (RJ) using official IBGE data —
in this example, estimated resident population — in a single table, with
source and period cited.

## When to use

When the user asks to compare 2 to 10 municipalities on one or more
indicators (e.g. *"which city is bigger, Niterói or Maricá?"*).

## The prompt

> *Compare the estimated population of Rio de Janeiro, Niterói and Maricá
> (RJ), with the source and the reference year.*

**Variations**:

- *"Which of these three municipalities in Rio de Janeiro has more
  inhabitants: Rio de Janeiro, Niterói or Maricá?"*
- *"Compare the population and GDP of Rio de Janeiro, Niterói and Maricá."*
  — GDP is not yet supported; the agent should explain that only population
  was compared, listing `"pib"` in `data.indicadores_nao_implementados`.
- *"Compare the population of Niterói (RJ) and a city called 'Itaboraí' that
  might not exist."* — exercises the `municipios_nao_resolvidos` path.

## Expected tool call

[`comparar_municipios`](../tools/agregados.md#perfil-municipal-comparacao)
resolves each municipality (name + state) independently and queries the
supported indicators (today, only estimated population). Municipalities that
aren't found/are ambiguous, and indicators that aren't supported, don't stop
the comparison — they appear in separate lists
(`municipios_nao_resolvidos`, `indicadores_nao_implementados`).

```python
comparar_municipios(
    municipios=[
        {"nome": "Rio de Janeiro", "uf": "RJ"},
        {"nome": "Niterói", "uf": "RJ"},
        {"nome": "Maricá", "uf": "RJ"},
    ],
    indicadores=["populacao_estimada"],
)
```

`indicadores` is optional — without it, `comparar_municipios` already uses
the basic indicators available (`["populacao"]`).

Internally, for each municipality, `comparar_municipios` calls:

- `obter_codigo_municipio(nome=..., uf="RJ")` → IBGE code.
- `obter_municipio_por_codigo(codigo_ibge=...)` → name, state, region.
- `consultar_populacao_municipio(nome=..., uf="RJ")` → estimated population.

The agent should **not** call these tools again manually.

## Example response

```json title="comparar_municipios(...)"
{
  "ok": true,
  "data": {
    "municipios": [
      {
        "codigo_ibge": 3304557,
        "nome": "Rio de Janeiro",
        "uf_sigla": "RJ",
        "uf_nome": "Rio de Janeiro",
        "regiao_nome": "Sudeste",
        "indicadores": [
          {
            "indicador": "populacao_estimada",
            "valor": 6211423.0,
            "unidade": "Pessoas",
            "periodo": "2024",
            "agregado_id": "6579",
            "variavel_id": "9324"
          }
        ]
      },
      {
        "codigo_ibge": 3303302,
        "nome": "Niterói",
        "uf_sigla": "RJ",
        "uf_nome": "Rio de Janeiro",
        "regiao_nome": "Sudeste",
        "indicadores": [
          {
            "indicador": "populacao_estimada",
            "valor": 516981.0,
            "unidade": "Pessoas",
            "periodo": "2024",
            "agregado_id": "6579",
            "variavel_id": "9324"
          }
        ]
      },
      {
        "codigo_ibge": 3302700,
        "nome": "Maricá",
        "uf_sigla": "RJ",
        "uf_nome": "Rio de Janeiro",
        "regiao_nome": "Sudeste",
        "indicadores": [
          {
            "indicador": "populacao_estimada",
            "valor": 187051.0,
            "unidade": "Pessoas",
            "periodo": "2024",
            "agregado_id": "6579",
            "variavel_id": "9324"
          }
        ]
      }
    ],
    "municipios_nao_resolvidos": [],
    "indicadores_consultados": ["populacao_estimada"],
    "indicadores_nao_implementados": [],
    "fontes": [
      "https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios",
      "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3304557",
      "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324",
      "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3303302",
      "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3302700"
    ],
    "limitacoes": [
      "Esta comparação cobre apenas os indicadores listados em `indicadores_consultados`; indicadores em `indicadores_nao_implementados` são apenas sugestões de nomes, não dados.",
      "O indicador de população usa o agregado SIDRA 6579 (Estimativas de população residente), que pode ser descontinuado ou renomeado pelo IBGE após um novo Censo.",
      "Sem o parâmetro \"ano\", cada município retorna o período mais recente disponível no SIDRA para esse indicador, que pode diferir entre municípios se algum não tiver dados para o período mais recente."
    ]
  },
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324",
    "params": {
      "municipios": [
        {"nome": "Rio de Janeiro", "uf": "RJ"},
        {"nome": "Niterói", "uf": "RJ"},
        {"nome": "Maricá", "uf": "RJ"}
      ],
      "indicadores": ["populacao_estimada"],
      "ano": null
    },
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "license_note": null
  },
  "warnings": [],
  "errors": []
}
```

> 🇧🇷 **Nota**: os campos de `data` e as mensagens de `warnings`/`errors`
> permanecem em português. The population values above are illustrative —
> run the tool to get current values.

## Suggested final answer to the user

> | Municipality | State | Estimated population (2024) |
> | --- | --- | --- |
> | Rio de Janeiro | RJ | 6,211,423 |
> | Niterói | RJ | 516,981 |
> | Maricá | RJ | 187,051 |
>
> Rio de Janeiro is by far the most populous of the three, followed by
> Niterói and then Maricá.
>
> **Source**: IBGE — SIDRA aggregate 6579 (Population Estimates), period
> 2024.
>
> **Limitations**: values are annual estimates (not the Census); the
> aggregate may be discontinued/renamed by IBGE after a new Census. Since no
> `ano` was given, the period could vary between municipalities if one of
> them had no data for the most recent period — in this case, all returned
> "2024".

## Example with an unimplemented indicator

For `comparar_municipios(municipios=[...], indicadores=["populacao_estimada", "pib"])`:

```json
{
  "data": {
    "indicadores_consultados": ["populacao_estimada"],
    "indicadores_nao_implementados": ["pib"]
  },
  "warnings": [
    {
      "message": "Indicador \"pib\" não está implementado e foi ignorado. Indicadores disponíveis atualmente: \"populacao\" (população residente estimada).",
      "code": null
    }
  ]
}
```

The agent should tell the user that **GDP is not available** in this
version, instead of estimating a value.

## Example with an unresolved municipality

For `comparar_municipios(municipios=[{"nome": "Niterói", "uf": "RJ"}, {"nome": "Itaboraí Fictícia", "uf": "RJ"}])`:

```json
{
  "data": {
    "municipios": [
      { "codigo_ibge": 3303302, "nome": "Niterói", "...": "..." }
    ],
    "municipios_nao_resolvidos": [
      { "nome": "Itaboraí Fictícia", "uf": "RJ", "motivo": "Nenhum município encontrado para \"Itaboraí Fictícia\" na UF \"RJ\"." }
    ]
  },
  "warnings": [
    {
      "message": "Nenhum município encontrado para \"Itaboraí Fictícia\" na UF \"RJ\".",
      "code": null
    }
  ]
}
```

The comparison proceeds normally for Niterói; the agent should mention that
"Itaboraí Fictícia" was not found, instead of silently ignoring it.

## If the user asks for more than 10 municipalities

`comparar_municipios` returns `ok=false` with the error `"No máximo 10
municípios por chamada (recebidos N)."` — the agent should ask the user to
shorten the list, rather than silently splitting it into multiple calls
(each call already covers up to 10 municipalities).

## Checking the source

- `data.fontes` lists every IBGE endpoint used — open each one in a browser
  to check the raw values returned by the IBGE API.
- For the population of a specific municipality, use the `codigo_ibge` and
  `periodo` from `data.municipios[].indicadores[]`:
  `https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/<periodo>/variaveis/9324?localidades=N6[<codigo_ibge>]`
