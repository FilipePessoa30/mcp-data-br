# Exemplo de resposta

## 1. Resposta da tool `gerar_perfil_municipal(nome="Maricá", uf="RJ")`

```json
{
  "ok": true,
  "data": {
    "municipio": {
      "codigo_ibge": 3302700,
      "nome": "Maricá",
      "uf_sigla": "RJ",
      "uf_nome": "Rio de Janeiro",
      "regiao_nome": "Sudeste",
      "microrregiao_ou_regiao_intermediaria": {
        "tipo": "microrregiao",
        "id": 33018,
        "nome": "Rio de Janeiro"
      }
    },
    "indicadores": [
      {
        "indicador": "populacao_estimada",
        "valor": 187051.0,
        "unidade": "Pessoas",
        "periodo": "2024",
        "agregado_id": "6579",
        "variavel_id": "9324"
      }
    ],
    "fontes": [
      "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3302700",
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
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3302700",
    "official_source": "https://www.ibge.gov.br/",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3302700",
    "params": { "nome": "Maricá", "uf": "RJ", "municipio_id": 3302700 },
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

## 2. Resposta da tool `listar_periodos_agregado(agregado_id="6579")` (opcional, lista truncada)

```json
{
  "ok": true,
  "data": [
    { "id": "2020", "nome": "2020" },
    { "id": "2021", "nome": "2021" },
    { "id": "2022", "nome": "2022" },
    { "id": "2023", "nome": "2023" },
    { "id": "2024", "nome": "2024" }
  ],
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos",
    "params": { "agregado_id": "6579" },
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "license_note": null
  },
  "warnings": [],
  "errors": []
}
```

> Lista ilustrativa e truncada — o agregado 6579 normalmente cobre uma série
> mais longa que 5 anos.

## 3. Resposta da tool `consultar_agregado(agregado_id="6579", variaveis="9324", localidades="N6[3302700]", periodos="-5")`

```json
{
  "ok": true,
  "data": [
    {
      "agregado_id": "6579",
      "variavel_id": "9324",
      "localidade_id": "3302700",
      "localidade_nome": "Maricá",
      "periodo": "2020",
      "valor": 161226.0,
      "unidade": "Pessoas",
      "raw": { "...": "..." }
    },
    {
      "agregado_id": "6579",
      "variavel_id": "9324",
      "localidade_id": "3302700",
      "localidade_nome": "Maricá",
      "periodo": "2021",
      "valor": 168066.0,
      "unidade": "Pessoas",
      "raw": { "...": "..." }
    },
    {
      "agregado_id": "6579",
      "variavel_id": "9324",
      "localidade_id": "3302700",
      "localidade_nome": "Maricá",
      "periodo": "2022",
      "valor": 175268.0,
      "unidade": "Pessoas",
      "raw": { "...": "..." }
    },
    {
      "agregado_id": "6579",
      "variavel_id": "9324",
      "localidade_id": "3302700",
      "localidade_nome": "Maricá",
      "periodo": "2023",
      "valor": 181458.0,
      "unidade": "Pessoas",
      "raw": { "...": "..." }
    },
    {
      "agregado_id": "6579",
      "variavel_id": "9324",
      "localidade_id": "3302700",
      "localidade_nome": "Maricá",
      "periodo": "2024",
      "valor": 187051.0,
      "unidade": "Pessoas",
      "raw": { "...": "..." }
    }
  ],
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-5/variaveis/9324",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-5/variaveis/9324",
    "params": {
      "agregado_id": "6579",
      "variaveis": "9324",
      "localidades": "N6[3302700]",
      "periodos": "-5"
    },
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "license_note": null
  },
  "warnings": [],
  "errors": []
}
```

> Todos os valores de população acima (perfil e série histórica) são
> ilustrativos. Execute as tools para obter os valores atuais. O campo `raw`
> foi abreviado (`{"...": "..."}`) apenas para este exemplo — na resposta
> real, contém o item de série original retornado pela API do IBGE.

## Resposta final do agente ao usuário

> **Nota técnica: crescimento populacional de Maricá (RJ)**
>
> **Município**: Maricá (RJ) — código IBGE `3302700`, região Sudeste,
> microrregião Rio de Janeiro (código 33018).
>
> **População estimada (2024)**: 187.051 habitantes.
>
> **Evolução da população estimada (2020–2024)**:
>
> | Ano | População estimada |
> | --- | --- |
> | 2020 | 161.226 |
> | 2021 | 168.066 |
> | 2022 | 175.268 |
> | 2023 | 181.458 |
> | 2024 | 187.051 |
>
> No período, a população estimada de Maricá cresceu cerca de 16% (de
> 161.226 para 187.051), um ritmo de crescimento acima da média de municípios
> do Rio de Janeiro — relevante para o planejamento de infraestrutura e
> serviços públicos.
>
> **Fonte**: IBGE — API de Localidades e Agregados/SIDRA (agregado 6579 —
> Estimativas de População).
>
> **Limitações**: os valores são estimativas anuais (não o resultado direto
> do último Censo) e o agregado pode ser descontinuado/renomeado pelo IBGE
> após um novo Censo. Este resumo não inclui PIB, IDH ou outros indicadores
> socioeconômicos — apenas população.

## Como verificar a fonte

- Perfil básico:
  `https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3302700`
- População mais recente:
  `https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324?localidades=N6[3302700]`
- Série histórica (2020–2024):
  `https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2020-2024/variaveis/9324?localidades=N6[3302700]`
- Todos esses endpoints são públicos e podem ser abertos diretamente no
  navegador para conferência.
