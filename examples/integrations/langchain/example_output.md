# Exemplo de resposta

## Chamada de tool esperada

```
comparar_municipios(
    municipios=[{"nome": "Niterói", "uf": "RJ"}, {"nome": "Maricá", "uf": "RJ"}],
    indicadores=["populacao_estimada"],
)
```

## Resposta da tool (envelope MCP)

```json
{
  "ok": true,
  "data": {
    "municipios": [
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
      "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3303302",
      "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324",
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

> Os valores de população acima são ilustrativos. Execute a tool para obter
> os valores atuais.

## Resposta final do agente (impressa por `agent.py`)

> | Município | UF | População estimada (2024) |
> | --- | --- | --- |
> | Niterói | RJ | 516.981 |
> | Maricá | RJ | 187.051 |
>
> Niterói é mais populosa que Maricá, com cerca de 330 mil habitantes a mais.
>
> **Fonte**: IBGE — agregado SIDRA 6579 (Estimativas de População), período
> 2024.

## Como verificar a fonte

- `data.fontes` lista todos os endpoints do IBGE usados — abra cada um no
  navegador para conferir os valores brutos.
- Para a população de um município específico, use o `codigo_ibge` e o
  `periodo` de `data.municipios[].indicadores[]`:
  `https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/<periodo>/variaveis/9324?localidades=N6[<codigo_ibge>]`
