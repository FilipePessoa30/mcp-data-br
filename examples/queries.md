# Exemplos de uso das tools

Exemplos de chamadas às tools do `mcp-ibge`, com os argumentos esperados.
Em um cliente MCP (Claude Desktop, Cursor, etc.) basta pedir em linguagem
natural — o modelo escolhe a tool e os argumentos. Os exemplos abaixo
mostram o `name` da tool e o `arguments` equivalente, úteis para depuração
ou para chamadas diretas via `mcp.call_tool`.

## Localidades

### Listar as grandes regiões do Brasil

```json
{ "name": "listar_regioes", "arguments": {} }
```

### Listar estados de uma região

```json
{ "name": "listar_estados", "arguments": { "regiao": "NE" } }
```

### Detalhes de um estado

```json
{ "name": "obter_estado", "arguments": { "uf": "SP" } }
```

### Listar municípios de um estado

```json
{ "name": "listar_municipios", "arguments": { "uf": "SP" } }
```

### Detalhes de um município pelo código IBGE

```json
{ "name": "obter_municipio", "arguments": { "codigo": "3550308" } }
```

### Buscar municípios pelo nome (ignora acentos/caixa)

```json
{
  "name": "buscar_municipios_por_nome",
  "arguments": { "nome": "sao jose", "uf": "SP", "limit": 5 }
}
```

### Listar os distritos de um município

```json
{ "name": "obter_distritos_municipio", "arguments": { "codigo": "3550308" } }
```

## Agregados / SIDRA

### Listar agregados disponíveis com filtro textual

```json
{
  "name": "listar_agregados",
  "arguments": { "assunto": "População", "texto": "estimada" }
}
```

### Metadados de um agregado (variáveis, períodos, níveis territoriais)

```json
{ "name": "obter_metadados_agregado", "arguments": { "agregado_id": 6579 } }
```

### Consultar dados de um agregado para o Brasil

```json
{
  "name": "consultar_dados_agregado",
  "arguments": {
    "agregado_id": 6579,
    "variaveis": "9324",
    "periodos": "-1",
    "localidades": "BR"
  }
}
```

### Consultar dados de um agregado para um município específico

```json
{
  "name": "consultar_dados_agregado",
  "arguments": {
    "agregado_id": 6579,
    "variaveis": "9324",
    "localidades": "N6[3550308]"
  }
}
```

## Indicadores

### População estimada de um município

```json
{ "name": "obter_populacao_municipio", "arguments": { "codigo_municipio": "3550308" } }
```
