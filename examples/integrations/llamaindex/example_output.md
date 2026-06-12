# Exemplo de resposta

## Chamada de tool esperada

```
listar_regioes()
```

## Resposta da tool (envelope MCP)

```json
{
  "ok": true,
  "data": [
    { "id": 1, "sigla": "N", "nome": "Norte" },
    { "id": 2, "sigla": "NE", "nome": "Nordeste" },
    { "id": 3, "sigla": "SE", "nome": "Sudeste" },
    { "id": 4, "sigla": "S", "nome": "Sul" },
    { "id": 5, "sigla": "CO", "nome": "Centro-Oeste" }
  ],
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/regioes",
    "official_source": "https://www.ibge.gov.br/",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/regioes",
    "params": {},
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "period": null,
    "territorial_level": "N2",
    "license_note": null,
    "version": "0.2.0",
    "cache_hit": false
  },
  "warnings": [],
  "errors": []
}
```

## Resposta final do agente (impressa por `agent.py`)

> O Brasil é dividido em 5 grandes regiões, segundo o IBGE:
>
> | Código | Sigla | Região |
> | --- | --- | --- |
> | 1 | N | Norte |
> | 2 | NE | Nordeste |
> | 3 | SE | Sudeste |
> | 4 | S | Sul |
> | 5 | CO | Centro-Oeste |
>
> **Fonte**: IBGE — API de Localidades
> (`https://servicodados.ibge.gov.br/api/v1/localidades/regioes`).

## Como verificar a fonte

- Acesse `https://servicodados.ibge.gov.br/api/v1/localidades/regioes`
  diretamente no navegador (sem autenticação) e compare com `data` — a lista
  e os códigos (1-5) são estáveis e raramente mudam.
