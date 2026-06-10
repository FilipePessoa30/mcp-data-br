# Fontes de dados e formato de resposta

## APIs do IBGE utilizadas

Todas as fontes são públicas, gratuitas e **não exigem chave de API**. Os
clientes compartilham uma URL base comum (`MCP_IBGE_API_BASE_URL`, padrão
`https://servicodados.ibge.gov.br/api`) e cada um acrescenta seu próprio
prefixo de versão/recurso:

| API | Caminho | URL completa (padrão) | Usada por |
| --- | --- | --- | --- |
| Localidades | `/v1/localidades` | `https://servicodados.ibge.gov.br/api/v1/localidades` | `clients/localidades.py` |
| Agregados (SIDRA) | `/v3/agregados` | `https://servicodados.ibge.gov.br/api/v3/agregados` | `clients/agregados.py` |

Documentação oficial: <https://servicodados.ibge.gov.br/api/docs>.

## Formato do envelope de resposta

Toda tool retorna um objeto JSON com dois campos: `metadata` e, dependendo
do resultado, `data` (sucesso) ou `error` (falha).

### Sucesso

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/regioes",
    "retrieved_at": "2026-06-10T12:00:00Z",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/regioes",
    "params": {}
  },
  "data": [
    { "id": 1, "sigla": "N", "nome": "Norte" }
  ]
}
```

### Erro

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/0000000",
    "retrieved_at": "2026-06-10T12:00:00Z",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/0000000",
    "params": { "municipio_id": 0 }
  },
  "error": "Erro HTTP 404 ao consultar https://servicodados.ibge.gov.br/api/v1/localidades/municipios/0000000"
}
```

### Campos de `metadata`

| Campo | Descrição |
| --- | --- |
| `source_name` | Nome da fonte oficial dos dados (configurável via `MCP_IBGE_SOURCE_NAME`). |
| `source_url` | URL efetivamente consultada para obter os dados/erro. |
| `retrieved_at` | Timestamp ISO 8601 (UTC, sufixo `Z`) do momento da consulta. |
| `endpoint` | URL do endpoint da API do IBGE utilizado. |
| `params` | Parâmetros usados na consulta (após resolução de aliases, filtros, etc.). |

Esse formato garante que qualquer dado retornado por uma tool possa ser
**rastreado até a fonte oficial**, com data/hora da consulta e os parâmetros
exatos utilizados — importante para auditoria e para o usuário verificar a
informação na fonte original.

### Campo opcional `warnings`

As tools de Localidades que envolvem busca aproximada (ex.:
`buscar_municipio`, `obter_codigo_municipio`) podem incluir um campo adicional
`warnings` (lista de strings) na resposta de sucesso, sinalizando ambiguidades
— por exemplo, quando mais de um município corresponde ao nome buscado. Nesse
caso, `data` traz os candidatos encontrados e o aviso sugere refinar a busca
(ex.: informando `uf`).

## Cache

As respostas das APIs do IBGE são opcionalmente cacheadas em memória
(`utils/cache.py`, TTL configurável via `MCP_IBGE_CACHE_TTL_SECONDS`). O
cache é local ao processo, não persiste entre execuções e serve apenas para
evitar chamadas repetidas durante a mesma sessão.
