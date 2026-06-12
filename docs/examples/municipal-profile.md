# Example: Municipal Profile

Generate a basic profile of a Brazilian municipality — identification (IBGE
code), state, region, micro-region/intermediate region, and the most recent
estimated resident population — in a single call.

## When to use

When the user asks for "a profile", "a summary", or "basic information"
about a specific municipality (e.g. *"tell me about Niterói"*).

## The prompt

> *Give me a basic profile of the municipality of Niterói, in Rio de Janeiro
> (RJ): IBGE code, region, micro-region and the most recent estimated
> population, with the source.*

**Variations**:

- *"I want a summary of São Paulo (SP): where it is, which region it's in,
  and how many inhabitants it has today, according to IBGE."*
- *"Make a profile for the municipality with IBGE code 3302700."* — the agent
  must first discover the name/state
  ([`obter_municipio_por_codigo`](../tools/localidades.md#6-obter_municipio_por_codigo))
  before it can call `gerar_perfil_municipal(nome=..., uf=...)`.
- *"Does Niterói have more inhabitants than Maricá?"* — this is a
  **comparison**, not a profile; see
  [Compare Municipalities](compare-municipalities.md).

## Expected tool call

[`gerar_perfil_municipal`](../tools/agregados.md#perfil-municipal-comparacao)
is the dedicated tool for this case — it already combines identification and
population in a single response:

```python
gerar_perfil_municipal(nome="Niterói", uf="RJ")
```

Internally, `gerar_perfil_municipal` already calls:

- `obter_codigo_municipio(nome="Niterói", uf="RJ")` → resolves to IBGE code `3303302`.
- `obter_municipio_por_codigo(codigo_ibge=3303302)` → name, state, region and micro-region.
- `consultar_populacao_municipio(nome="Niterói", uf="RJ")` → most recent estimated population.

The agent does **not** need to call these three tools separately — calling
`gerar_perfil_municipal` directly avoids duplicate requests.

!!! tip "When NOT to use `gerar_perfil_municipal`"
    - If the user asks **only** for the IBGE code → use
      [`obter_codigo_municipio`](../tools/localidades.md#5-obter_codigo_municipio).
    - If the user asks **only** for the population, without the rest of the
      profile → use
      [`consultar_populacao_municipio`](../tools/agregados.md#14-consultar_populacao_municipio).
    - If the user asks for a **map** or the **geometry** of the municipality
      → see [Education Activity](education-activity.md) (uses
      `obter_malha_municipio`/`obter_bbox_municipio`).
    - If the user asks to **compare** several municipalities → use
      [`comparar_municipios`](../tools/agregados.md#perfil-municipal-comparacao)
      (see [Compare Municipalities](compare-municipalities.md)).

## Example response

```json title='gerar_perfil_municipal(nome="Niterói", uf="RJ")'
{
  "ok": true,
  "data": {
    "municipio": {
      "codigo_ibge": 3303302,
      "nome": "Niterói",
      "uf_sigla": "RJ",
      "uf_nome": "Rio de Janeiro",
      "regiao_nome": "Sudeste",
      "microrregiao_ou_regiao_intermediaria": {
        "tipo": "microrregiao",
        "id": 33014,
        "nome": "Niterói"
      }
    },
    "indicadores": [
      {
        "indicador": "populacao_estimada",
        "valor": 516981.0,
        "unidade": "Pessoas",
        "periodo": "2024",
        "agregado_id": "6579",
        "variavel_id": "9324"
      }
    ],
    "fontes": [
      "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3303302",
      "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324"
    ],
    "limitacoes": [
      "Este perfil cobre apenas identificação básica do município e o indicador de população estimada; não inclui PIB, IDH, área territorial ou outros indicadores socioeconômicos.",
      "O indicador de população usa o agregado SIDRA 6579 (Estimativas de população residente), que pode ser descontinuado ou renomeado pelo IBGE após um novo Censo."
    ],
    "proximos_indicadores_sugeridos": [
      "Área territorial e densidade demográfica",
      "PIB municipal e PIB per capita",
      "IDH municipal",
      "Distritos do município (via `listar_distritos`)",
      "Indicadores educacionais e de saúde"
    ]
  },
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3303302",
    "official_source": "https://www.ibge.gov.br/",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3303302",
    "params": { "nome": "Niterói", "uf": "RJ", "municipio_id": 3303302 },
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "period": null,
    "territorial_level": null,
    "license_note": null,
    "version": "0.2.0",
    "cache_hit": false
  },
  "warnings": [
    {
      "message": "Nenhum \"ano\" foi informado para a população: retornado o período mais recente disponível no SIDRA (\"2024\").",
      "code": null
    }
  ],
  "errors": []
}
```

> 🇧🇷 **Nota**: os campos de `data` (`municipio`, `indicadores`, `fontes`,
> `limitacoes`, `proximos_indicadores_sugeridos`) e as mensagens de
> `warnings`/`errors` permanecem em português. The population value
> (`516981`) and period (`"2024"`) above are illustrative — run the tool to
> get the current value.

## Suggested final answer to the user

> **Niterói (RJ)** — IBGE code `3303302`
>
> - **Region**: Sudeste (Southeast)
> - **Micro-region**: Niterói (code 33014)
> - **Estimated population (2024)**: ~516,981 inhabitants
>
> **Source**: IBGE — Localidades API and Agregados/SIDRA (aggregate 6579 —
> Population Estimates), period 2024.
>
> **Limitations**: this profile covers only basic identification and the
> estimated population indicator (does not include GDP, HDI or land area).
> The population indicator may be discontinued/renamed by IBGE after a new
> Census. Since no `ano` was given, the value corresponds to the most recent
> period available in SIDRA at the time of the query.

## Error example: ambiguous municipality

If the user asks for `gerar_perfil_municipal(nome="São José", uf="SP")` and
there is more than one "São José..." municipality in SP, the response is:

```json
{
  "ok": false,
  "data": null,
  "warnings": [
    {
      "message": "Encontrados 2 municípios para \"São José\": São José dos Campos, São José do Rio Preto. Refine a busca com \"uf\" ou um nome mais específico.",
      "code": null
    }
  ],
  "errors": [
    {
      "message": "Encontrados 2 municípios para \"São José\": São José dos Campos, São José do Rio Preto. Refine a busca com \"uf\" ou um nome mais específico.",
      "code": null
    }
  ]
}
```

In this case the agent should **ask the user** which of the listed
municipalities they meant, instead of picking one arbitrarily.

## Checking the source

- Identification endpoint:
  `https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3303302`
- Population endpoint:
  `https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324?localidades=N6[3303302]`
- Compare the values in `data` against the content of these endpoints — both
  accessible directly in a browser, with no authentication.
