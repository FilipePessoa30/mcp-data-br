# Exemplo de resposta

## Chamada de tool esperada

```
obter_codigo_municipio(nome="Niterói", uf="RJ")
```

## Resposta da tool (envelope MCP)

```json
{
  "ok": true,
  "data": 3303302,
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios",
    "official_source": "https://www.ibge.gov.br/",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios",
    "params": { "nome": "Niterói", "uf": "RJ", "limite": 5 },
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "period": null,
    "territorial_level": null,
    "license_note": null,
    "version": "0.2.0",
    "cache_hit": false
  },
  "warnings": [],
  "errors": []
}
```

## Resposta final do agente (impressa por `agent.py`)

> O código IBGE do município de Niterói (RJ) é **3303302**.

## Exemplo com nome ambíguo

Se o usuário perguntar "Qual o código IBGE de São José, em SP?", a tool
retorna `ok: false` com `warnings`/`errors` listando os candidatos
encontrados (ex.: "São José dos Campos", "São José do Rio Preto"). O agente
deve repetir esses candidatos ao usuário e pedir para escolher, em vez de
adivinhar um código.

## Como verificar a fonte

- `data` é o código IBGE de 7 dígitos retornado diretamente pela API de
  Localidades do IBGE.
- Para conferir manualmente, acesse
  `https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3303302`
  e confira que `nome` é "Niterói" e `microrregiao.mesorregiao.UF.sigla` é
  "RJ".
