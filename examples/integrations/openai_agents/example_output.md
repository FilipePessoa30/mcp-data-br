# Exemplo de resposta

## Chamada de tool esperada

```
gerar_perfil_municipal(nome="Maricá", uf="RJ")
```

## Resposta da tool (envelope MCP)

```json
{
  "ok": true,
  "data": {
    "municipio": {
      "codigo_ibge": 3302904,
      "nome": "Maricá",
      "uf_sigla": "RJ",
      "uf_nome": "Rio de Janeiro",
      "regiao_nome": "Sudeste",
      "microrregiao_ou_regiao_intermediaria": {
        "tipo": "microrregiao",
        "id": 33007,
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
      "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3302904",
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
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3302904",
    "official_source": "https://www.ibge.gov.br/",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3302904",
    "params": { "nome": "Maricá", "uf": "RJ", "municipio_id": 3302904 },
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

> Os valores acima (microrregião, população `187051`, período `2024`) são
> ilustrativos. Execute a tool para obter os valores atuais.

## Resposta final do agente (impressa por `agent.py`)

> **Maricá (RJ)** — código IBGE `3302904`
>
> - **Região**: Sudeste
> - **Microrregião**: Rio de Janeiro (código 33007)
> - **População estimada (2024)**: ~187.051 habitantes
>
> **Fonte**: IBGE — API de Localidades e Agregados/SIDRA (agregado 6579 —
> Estimativas de População), período 2024.
>
> **Limitações**: este perfil cobre apenas identificação básica e o
> indicador de população estimada (não inclui PIB, IDH ou área territorial).

## Exemplo de erro: município ambíguo

Se o usuário pedir `gerar_perfil_municipal(nome="São José", uf="SP")` e
houver mais de um município "São José..." em SP, a resposta é:

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

Nesse caso o agente deve **perguntar ao usuário** qual dos municípios
listados é o desejado, em vez de escolher um arbitrariamente.

## Como verificar a fonte

- Identificação do município:
  `https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3302904`
- População estimada:
  `https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324?localidades=N6[3302904]`
- Ambos acessíveis diretamente no navegador, sem autenticação.
