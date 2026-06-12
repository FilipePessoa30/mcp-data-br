# Tools disponíveis

Referência completa de todas as tools MCP expostas por `mcp-ibge`. Para cada
uma: nome, descrição, parâmetros, um exemplo de chamada, um exemplo de
resposta JSON, possíveis `warnings`, erros comuns e a fonte (endpoint da API
do IBGE) usada.

## Sumário

**Localidades**

1. [`listar_regioes`](#1-listar_regioes)
2. [`listar_estados`](#2-listar_estados)
3. [`listar_municipios`](#3-listar_municipios)
4. [`buscar_municipio`](#4-buscar_municipio)
5. [`obter_codigo_municipio`](#5-obter_codigo_municipio)
6. [`obter_municipio_por_codigo`](#6-obter_municipio_por_codigo)
7. [`listar_distritos`](#7-listar_distritos)

**Agregados / SIDRA** (estável a partir da v0.2.0 — veja
[Como descobrir agregado, variável, período e localidade](#como-descobrir-agregado-variável-período-e-localidade)
antes de usar)

8. [`listar_agregados`](#8-listar_agregados)
9. [`obter_metadados_agregado`](#9-obter_metadados_agregado)
10. [`listar_variaveis_agregado`](#10-listar_variaveis_agregado)
11. [`listar_periodos_agregado`](#11-listar_periodos_agregado)
12. [`listar_localidades_agregado`](#12-listar_localidades_agregado)
13. [`consultar_agregado`](#13-consultar_agregado)

**Indicadores** (experimental)

14. [`consultar_populacao_municipio`](#14-consultar_populacao_municipio)

**SIDRA Query Builder** (novo — descoberta, sugestão e validação de
consultas, sem uso de LLM no servidor)

15. [`buscar_tabelas_sidra`](#15-buscar_tabelas_sidra)
16. [`explicar_tabela_sidra`](#16-explicar_tabela_sidra)
17. [`listar_variaveis_tabela_sidra`](#17-listar_variaveis_tabela_sidra)
18. [`listar_classificacoes_tabela_sidra`](#18-listar_classificacoes_tabela_sidra)
19. [`sugerir_consulta_sidra`](#19-sugerir_consulta_sidra)
20. [`validar_consulta_sidra`](#20-validar_consulta_sidra)
21. [`executar_consulta_sidra_validada`](#21-executar_consulta_sidra_validada)

**Perfil Municipal** (novo — combina Localidades e Indicadores)

22. [`gerar_perfil_municipal`](#22-gerar_perfil_municipal)

**Comparação de Municípios** (novo — compara múltiplos municípios)

23. [`comparar_municipios`](#23-comparar_municipios)

**Geoespacial** (novo — malhas geográficas em GeoJSON e bounding boxes)

24. [`obter_malha_municipio`](#24-obter_malha_municipio)
25. [`obter_malha_uf`](#25-obter_malha_uf)
26. [`obter_bbox_municipio`](#26-obter_bbox_municipio)
27. [`gerar_geojson_municipios`](#27-gerar_geojson_municipios)

## Formato da resposta

Toda tool retorna um envelope JSON com `metadata` e (`data` ou `error`):

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/...",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/...",
    "params": { "...": "..." },
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": "...",
  "warnings": ["..."]
}
```

- `data` está presente em caso de sucesso; `error` (string) em caso de falha
  — uma tool nunca retorna ambos.
- `warnings` é opcional e só aparece quando há avisos não fatais (ex.: busca
  ambígua, dado ausente no SIDRA, período inferido automaticamente).
- `metadata.params` reflete os parâmetros efetivamente usados na consulta
  (após resolver aliases como `"BR"` → `"N1[all]"`).
- Veja [data_sources.md](data_sources.md) para mais detalhes sobre o
  envelope e a proveniência dos dados.

## Erros comuns a todas as tools

Estes erros podem ocorrer em qualquer tool, independentemente dos erros
específicos listados em cada seção:

| Situação | Mensagem (`error`) |
| --- | --- |
| Timeout na API do IBGE | `Tempo limite excedido (30.0s) ao consultar <url>` |
| Falha de conexão (DNS, rede) | `Falha de conexão ao consultar <url>: <detalhe>` |
| Resposta não é JSON válido | `Resposta inválida (JSON malformado) de <url>` |
| IBGE retorna HTTP 429 (rate limit) | `IBGE retornou HTTP 429 para <url>` |
| IBGE retorna HTTP 5xx | `IBGE retornou HTTP <status> para <url>` |
| Exceção inesperada (bug/rede de segurança) | `Erro inesperado: <detalhe>` |

Em todos os casos, a resposta mantém o envelope `{"metadata": {...}, "error":
"..."}` — `metadata.endpoint`/`metadata.params` indicam qual chamada falhou.

---

## Localidades

### 1. `listar_regioes`

**Descrição**: lista as 5 grandes regiões geográficas do Brasil (Norte,
Nordeste, Sudeste, Sul, Centro-Oeste).

**Parâmetros**: nenhum.

**Exemplo de chamada**:

```python
listar_regioes()
```

**Exemplo de resposta JSON**:

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/regioes",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/regioes",
    "params": {},
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": [
    { "id": 1, "sigla": "N", "nome": "Norte" },
    { "id": 2, "sigla": "NE", "nome": "Nordeste" },
    { "id": 3, "sigla": "SE", "nome": "Sudeste" },
    { "id": 4, "sigla": "S", "nome": "Sul" },
    { "id": 5, "sigla": "CO", "nome": "Centro-Oeste" }
  ]
}
```

**Possíveis warnings**: nenhum.

**Erros comuns**: apenas os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools)
(timeout, falha de conexão, HTTP 5xx/429 do IBGE).

**Fonte usada**: [IBGE Localidades API](https://servicodados.ibge.gov.br/api/docs/localidades)
— `GET /localidades/regioes`.

---

### 2. `listar_estados`

**Descrição**: lista os 26 estados e o Distrito Federal, ordenados por nome
(ordenação local, ignorando acentos/caixa). Cada item inclui `id` (código
IBGE da UF), `sigla`, `nome` e a `regiao` (`id`, `sigla`, `nome`) a que
pertence.

**Parâmetros**: nenhum.

**Exemplo de chamada**:

```python
listar_estados()
```

**Exemplo de resposta JSON** (lista truncada):

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/estados",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/estados",
    "params": {},
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": [
    {
      "id": 12,
      "sigla": "AC",
      "nome": "Acre",
      "regiao": { "id": 1, "sigla": "N", "nome": "Norte" }
    },
    {
      "id": 33,
      "sigla": "RJ",
      "nome": "Rio de Janeiro",
      "regiao": { "id": 3, "sigla": "SE", "nome": "Sudeste" }
    },
    {
      "id": 35,
      "sigla": "SP",
      "nome": "São Paulo",
      "regiao": { "id": 3, "sigla": "SE", "nome": "Sudeste" }
    }
  ]
}
```

**Possíveis warnings**: nenhum.

**Erros comuns**: apenas os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**: [IBGE Localidades API](https://servicodados.ibge.gov.br/api/docs/localidades)
— `GET /localidades/estados`.

---

### 3. `listar_municipios`

**Descrição**: lista os municípios de uma unidade federativa (UF), com a UF
e a região resolvidas em cada item (`uf_sigla`, `uf_nome`, `regiao_nome`,
extraídos da estrutura aninhada da API). O JSON original de cada município
fica disponível em `raw`.

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `uf` | `string` | sim | Sigla da UF (ex.: `"RJ"`, `"SP"`, `"MG"`) ou código IBGE da UF (ex.: `"33"`). |

**Exemplo de chamada**:

```python
listar_municipios(uf="RJ")
```

**Exemplo de resposta JSON** (lista truncada):

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios",
    "params": { "uf": "RJ" },
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": [
    {
      "id": 3303302,
      "nome": "Niterói",
      "uf_id": 33,
      "uf_sigla": "RJ",
      "uf_nome": "Rio de Janeiro",
      "regiao_nome": "Sudeste",
      "raw": { "...": "JSON original do IBGE, com microrregiao/mesorregiao/UF" }
    },
    {
      "id": 3304557,
      "nome": "Rio de Janeiro",
      "uf_id": 33,
      "uf_sigla": "RJ",
      "uf_nome": "Rio de Janeiro",
      "regiao_nome": "Sudeste",
      "raw": { "...": "..." }
    }
  ]
}
```

**Possíveis warnings**: nenhum.

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| `uf` não corresponde a nenhuma sigla/código válido | `UF inválida: "XX". Use a sigla (ex.: "RJ") ou o código IBGE (ex.: "33").` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**: [IBGE Localidades API](https://servicodados.ibge.gov.br/api/docs/localidades)
— `GET /localidades/estados/{uf}/municipios`.

---

### 4. `buscar_municipio`

**Descrição**: busca municípios pelo nome com correspondência aproximada
(*fuzzy*), ignorando acentos e maiúsculas/minúsculas. A busca tenta, nesta
ordem: (1) correspondência exata do nome normalizado, (2) nome que "contém"
o termo buscado e, por fim, (3) similaridade textual (`difflib`). Sem `uf`,
busca em todos os municípios do Brasil; com `uf`, busca apenas dentro dessa
UF. Quando há mais de um candidato, a resposta inclui um aviso em `warnings`
com a lista de candidatos e sugerindo refinar a busca.

**Parâmetros**:

| Nome | Tipo | Obrigatório | Padrão | Descrição |
| --- | --- | --- | --- | --- |
| `nome` | `string` | sim | — | Nome (ou parte do nome) do município a buscar. |
| `uf` | `string \| null` | não | `null` | Restringe a busca aos municípios desta UF (sigla ou código). |
| `limite` | `integer` | não | `10` | Número máximo de candidatos retornados (entre `1` e `50`). |

**Exemplo de chamada**:

```python
buscar_municipio(nome="São José")
```

**Exemplo de resposta JSON** (busca nacional, ambígua — dois candidatos):

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios",
    "params": { "nome": "São José", "limite": 10 },
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": [
    {
      "id": 3548807,
      "nome": "São José dos Campos",
      "uf_id": 35,
      "uf_sigla": "SP",
      "uf_nome": "São Paulo",
      "regiao_nome": "Sudeste",
      "raw": { "...": "..." }
    },
    {
      "id": 4125506,
      "nome": "São José dos Pinhais",
      "uf_id": 41,
      "uf_sigla": "PR",
      "uf_nome": "Paraná",
      "regiao_nome": "Sul",
      "raw": { "...": "..." }
    }
  ],
  "warnings": [
    "Encontrados 2 municípios para \"São José\": São José dos Campos, São José dos Pinhais. Refine a busca com \"uf\" ou um nome mais específico."
  ]
}
```

**Possíveis warnings**:

- `Encontrados N municípios para "<nome>": <nomes>. Refine a busca com "uf" ou um nome mais específico.`
  — emitido sempre que mais de um candidato é encontrado (mesmo que `N`
  exceda `limite`; a lista de nomes é truncada em `limite` itens, mas `N` é o
  total de candidatos antes do truncamento).

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| `uf` informada não corresponde a nenhuma sigla/código válido | `UF inválida: "XX". Use a sigla (ex.: "RJ") ou o código IBGE (ex.: "33").` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools). Não
há erro para "nenhum resultado encontrado": nesse caso `data` é `[]` e não há
`warnings`.

**Fonte usada**: [IBGE Localidades API](https://servicodados.ibge.gov.br/api/docs/localidades)
— `GET /localidades/municipios` (sem `uf`) ou
`GET /localidades/estados/{uf}/municipios` (com `uf`), com o filtro por nome
aplicado localmente sobre a resposta.

---

### 5. `obter_codigo_municipio`

**Descrição**: obtém o código IBGE de 7 dígitos de um único município, a
partir do nome e da UF. Internamente reutiliza a mesma busca *fuzzy* de
[`buscar_municipio`](#4-buscar_municipio) (limitada a 5 candidatos), mas
exige que o resultado seja **exatamente um** município — caso contrário,
retorna erro.

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `nome` | `string` | sim | Nome do município. |
| `uf` | `string` | sim | Sigla (ex.: `"SP"`) ou código IBGE da UF. |

**Exemplo de chamada**:

```python
obter_codigo_municipio(nome="Niterói", uf="RJ")
```

**Exemplo de resposta JSON**:

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios",
    "params": { "nome": "Niterói", "limite": 5, "uf": "RJ" },
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": 3303302
}
```

**Possíveis warnings**: em caso de sucesso, nenhum (a busca interna só
prossegue quando há exatamente um candidato). Quando há ambiguidade, o aviso
de `buscar_municipio` é reaproveitado — veja "Erros comuns" abaixo.

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| Nenhum município corresponde ao `nome` na `uf` informada | `Nenhum município encontrado para "<nome>" na UF "<uf>".` |
| Mais de um município corresponde ao `nome` na `uf` informada | `Encontrados N municípios para "<nome>": <nomes>. Refine a busca com "uf" ou um nome mais específico.` (mesmo texto do warning de `buscar_municipio`, retornado aqui como erro fatal) |
| `uf` informada não corresponde a nenhuma sigla/código válido | `UF inválida: "XX". Use a sigla (ex.: "RJ") ou o código IBGE (ex.: "33").` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**: [IBGE Localidades API](https://servicodados.ibge.gov.br/api/docs/localidades)
— `GET /localidades/estados/{uf}/municipios`, com filtro por nome aplicado
localmente.

---

### 6. `obter_municipio_por_codigo`

**Descrição**: retorna os detalhes de um município a partir do seu código
IBGE de 7 dígitos, com a UF e a região resolvidas (`uf_sigla`, `uf_nome`,
`regiao_nome`) — mesmo formato de item retornado por
[`listar_municipios`](#3-listar_municipios) e
[`buscar_municipio`](#4-buscar_municipio).

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `codigo_ibge` | `integer` | sim | Código IBGE do município com 7 dígitos (ex.: `3550308` = São Paulo). |

**Exemplo de chamada**:

```python
obter_municipio_por_codigo(codigo_ibge=3303302)
```

**Exemplo de resposta JSON**:

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3303302",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3303302",
    "params": { "municipio_id": 3303302 },
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": {
    "id": 3303302,
    "nome": "Niterói",
    "uf_id": 33,
    "uf_sigla": "RJ",
    "uf_nome": "Rio de Janeiro",
    "regiao_nome": "Sudeste",
    "raw": { "...": "JSON original do IBGE, com microrregiao/mesorregiao/UF" }
  }
}
```

**Possíveis warnings**: nenhum.

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| `codigo_ibge` não corresponde a nenhum município | `IBGE retornou HTTP 404 para https://servicodados.ibge.gov.br/api/v1/localidades/municipios/<codigo_ibge>` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**: [IBGE Localidades API](https://servicodados.ibge.gov.br/api/docs/localidades)
— `GET /localidades/municipios/{codigo_ibge}`.

---

### 7. `listar_distritos`

**Descrição**: lista os distritos de um município, identificado pelo seu
código IBGE de 7 dígitos. Cada distrito retornado inclui `id`, `nome`,
`municipio_id` e `municipio_nome` (resolvidos a partir do JSON aninhado da
API), além do JSON original em `raw`.

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `codigo_municipio` | `integer` | sim | Código IBGE do município com 7 dígitos (ex.: `3550308` = São Paulo). |

**Exemplo de chamada**:

```python
listar_distritos(codigo_municipio=3304557)
```

**Exemplo de resposta JSON** (lista truncada):

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3304557/distritos",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3304557/distritos",
    "params": { "municipio_id": 3304557 },
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": [
    {
      "id": 330455705,
      "nome": "Rio de Janeiro",
      "municipio_id": 3304557,
      "municipio_nome": "Rio de Janeiro",
      "raw": { "...": "..." }
    }
  ]
}
```

**Possíveis warnings**: nenhum.

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| `codigo_municipio` não corresponde a nenhum município | `IBGE retornou HTTP 404 para https://servicodados.ibge.gov.br/api/v1/localidades/municipios/<codigo_municipio>/distritos` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**: [IBGE Localidades API](https://servicodados.ibge.gov.br/api/docs/localidades)
— `GET /localidades/municipios/{codigo_municipio}/distritos`.

---

## Agregados / SIDRA

A partir da v0.2.0, estas 6 tools (`listar_agregados`,
`obter_metadados_agregado`, `listar_variaveis_agregado`,
`listar_periodos_agregado`, `listar_localidades_agregado` e
`consultar_agregado`) são consideradas **estáveis**: cobrem o acesso genérico
a qualquer agregado (tabela) do SIDRA — descoberta de metadados e consulta de
dados — e têm cobertura de testes completa. O indicador
[`consultar_populacao_municipio`](#14-consultar_populacao_municipio) continua
**experimental**, por depender de um agregado e variável fixos que o IBGE
pode descontinuar/renomear após um novo Censo.

### Como descobrir agregado, variável, período e localidade

O SIDRA tem milhares de agregados (tabelas), cada um com seu próprio conjunto
de variáveis, períodos, classificações e níveis territoriais. Antes de chamar
[`consultar_agregado`](#13-consultar_agregado), use as tools de metadados
nesta ordem:

1. **Encontrar o agregado** — [`listar_agregados`](#8-listar_agregados) com
   `pesquisa` (ex.: `"Índice Nacional de Preços ao Consumidor Amplo"`),
   `assunto` (ex.: `"Índices de preços"`) e/ou `texto` (filtro local pelo
   nome) para descobrir o `agregado_id`.
2. **Confirmar o agregado e ver o panorama geral** —
   [`obter_metadados_agregado`](#9-obter_metadados_agregado) com o
   `agregado_id` retorna `pesquisa`, `assunto`, `periodicidade` e, em `raw`,
   a lista completa de variáveis, classificações e níveis territoriais
   suportados (`nivelTerritorial`).
3. **Escolher a(s) variável(is)** —
   [`listar_variaveis_agregado`](#10-listar_variaveis_agregado) retorna
   `id`, `nome` e `unidade` de cada variável. O `id` vai no parâmetro
   `variaveis` de `consultar_agregado` (um ID, vários separados por vírgula,
   ou `"all"`).
4. **Escolher o(s) período(s)** —
   [`listar_periodos_agregado`](#11-listar_periodos_agregado) retorna os
   períodos disponíveis (ex.: `"202604"` para abril/2026 em um agregado
   mensal, `"2024"` para um agregado anual). O `id` vai no parâmetro
   `periodos` — que também aceita um intervalo (`"2010-2020"`), uma lista
   (`"2019,2021"`) ou um valor relativo (`"-1"` = último período disponível,
   `"-6"` = últimos 6 períodos).
5. **Escolher a(s) localidade(s)** —
   [`listar_localidades_agregado`](#12-listar_localidades_agregado) com um
   `niveis` (ex.: `"N1"` = Brasil, `"N3"` = estados, `"N6"` = municípios,
   conforme o que aparecer em `nivelTerritorial` no passo 2) retorna `id` e
   `nome` de cada localidade disponível **para aquele agregado**. O `id` vai
   no parâmetro `localidades` de `consultar_agregado`, no formato
   `N<nivel>[<id1>,<id2>,...]` (ou `N<nivel>[all]` para todas).
6. **Consultar os dados** —
   [`consultar_agregado`](#13-consultar_agregado) com `agregado_id`,
   `variaveis`, `localidades` e `periodos` resolvidos nos passos anteriores.
   Se o agregado tiver classificações (visíveis em `raw.classificacoes` no
   passo 2), use o parâmetro `classificacao` no formato
   `"<id_classificacao>[<id_categoria>]"`.

#### Exemplo completo: variação mensal do IPCA (agregado `7060`)

```python
# 1. Encontrar o agregado
listar_agregados(pesquisa="Índice Nacional de Preços ao Consumidor Amplo", texto="a partir de janeiro/2020")
# -> agregado_id = "7060"

# 2. Confirmar metadados (variáveis, classificações, níveis territoriais)
obter_metadados_agregado(agregado_id="7060")
# -> variável "63" = "IPCA - Variação mensal" (%)
# -> classificação "315" tem a categoria "7169" = "Índice geral"
# -> nivelTerritorial.Administrativo = ["N1", "N6", "N7"]

# 3. Variáveis disponíveis
listar_variaveis_agregado(agregado_id="7060")

# 4. Períodos disponíveis (ex.: "202604" = abril/2026)
listar_periodos_agregado(agregado_id="7060")

# 5. Localidades disponíveis no nível Brasil
listar_localidades_agregado(agregado_id="7060", niveis="N1")

# 6. Consultar a variação mensal do IPCA (índice geral) no Brasil, último período
consultar_agregado(
    agregado_id="7060",
    variaveis="63",
    localidades="N1[all]",
    periodos="-1",
    classificacao="315[7169]",
)
```

A consulta do passo 6 retorna, por exemplo, `valor: 0.67` (variação mensal de
0,67% em abril/2026), com `unidade: "%"`, `localidade_nome: "Brasil"` e
`periodo: "202604"`.

### 8. `listar_agregados`

**Descrição**: lista os agregados (tabelas estatísticas) disponíveis na API
de Agregados do IBGE/SIDRA, cada um com `id` e `nome`. Use esta tool para
descobrir o ID de um agregado antes de chamar
[`obter_metadados_agregado`](#9-obter_metadados_agregado),
[`listar_variaveis_agregado`](#10-listar_variaveis_agregado) ou
[`consultar_agregado`](#13-consultar_agregado). `pesquisa` e `assunto` são
filtros aplicados pela própria API; `texto` é um filtro adicional aplicado
localmente sobre o `nome` dos agregados (substring, sem distinção de
maiúsculas/minúsculas).

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `pesquisa` | `string \| null` | não | Filtra pela pesquisa de origem (ex.: `"Censo Demográfico"`). |
| `assunto` | `string \| null` | não | Filtra pelo nome do assunto (ex.: `"População"`). |
| `texto` | `string \| null` | não | Filtro textual adicional pelo nome dos agregados (substring local). |

**Exemplo de chamada**:

```python
listar_agregados(assunto="População")
```

**Exemplo de resposta JSON** (lista truncada):

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados",
    "params": { "assunto": "População" },
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": [
    { "id": "6579", "nome": "População residente estimada" },
    { "id": "9514", "nome": "População residente, por sexo, situação e grupos de idade" }
  ]
}
```

**Possíveis warnings**: nenhum.

**Erros comuns**: apenas os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).
Filtros que não correspondem a nada (ex.: `texto` muito específico) retornam
`data: []` em vez de erro.

**Fonte usada**: [IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados)
— `GET /agregados`.

---

### 9. `obter_metadados_agregado`

**Descrição**: retorna os metadados de um agregado do SIDRA. Os campos
`pesquisa`, `assunto` e `periodicidade` (frequência: `"anual"`, `"mensal"`,
etc.) ficam disponíveis diretamente; o JSON completo da API — incluindo
`variaveis`, `classificacoes` e `nivelTerritorial` — fica disponível em
`raw`. Use o resultado para escolher os parâmetros de
[`consultar_agregado`](#13-consultar_agregado).

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `agregado_id` | `string` | sim | ID do agregado do SIDRA (ex.: `"6579"` = "População residente estimada"). |

**Exemplo de chamada**:

```python
obter_metadados_agregado(agregado_id="6579")
```

**Exemplo de resposta JSON** (campo `raw` truncado):

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/metadados",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/metadados",
    "params": { "agregado_id": "6579" },
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": {
    "id": "6579",
    "nome": "População residente estimada",
    "pesquisa": "Estimativas de População",
    "assunto": "População",
    "periodicidade": "anual",
    "raw": {
      "id": 6579,
      "nome": "População residente estimada",
      "URL": "https://servicodados.ibge.gov.br/api/v3/agregados/6579",
      "pesquisa": "Estimativas de População",
      "assunto": "População",
      "periodicidade": { "frequencia": "anual", "inicio": 2001, "fim": 2024 },
      "nivelTerritorial": { "Administrativo": ["N1", "N2", "N3", "N6"], "Especial": [], "IBGE": [] },
      "variaveis": [
        { "id": 9324, "nome": "População residente estimada", "unidade": "Pessoas", "sumarizacao": [] }
      ],
      "classificacoes": []
    }
  }
}
```

**Possíveis warnings**: nenhum.

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| `agregado_id` é uma string vazia/só espaços | `Parâmetro "agregado_id" não pode ser vazio.` |
| `agregado_id` não corresponde a nenhum agregado existente (API retorna corpo vazio com HTTP 200) | `Agregado "<agregado_id>" não encontrado.` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**: [IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados)
— `GET /agregados/{agregado_id}/metadados`.

---

### 10. `listar_variaveis_agregado`

**Descrição**: lista as variáveis disponíveis em um agregado do SIDRA, cada
uma com `id`, `nome` e `unidade` (ex.: `"Pessoas"`, `"Reais"`). O JSON
original de cada variável fica disponível em `raw`. Use o `id` de uma
variável no parâmetro `variaveis` de
[`consultar_agregado`](#13-consultar_agregado).

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `agregado_id` | `string` | sim | ID do agregado do SIDRA (ex.: `"6579"` = "População residente estimada"). |

**Exemplo de chamada**:

```python
listar_variaveis_agregado(agregado_id="6579")
```

**Exemplo de resposta JSON**:

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/variaveis",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/variaveis",
    "params": { "agregado_id": "6579" },
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": [
    {
      "id": "9324",
      "nome": "População residente estimada",
      "unidade": "Pessoas",
      "raw": { "id": 9324, "nome": "População residente estimada", "unidade": "Pessoas", "sumarizacao": [] }
    }
  ]
}
```

**Possíveis warnings**: nenhum.

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| `agregado_id` é uma string vazia/só espaços | `Parâmetro "agregado_id" não pode ser vazio.` |
| `agregado_id` não corresponde a nenhum agregado existente | `Agregado "<agregado_id>" não encontrado.` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**: [IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados)
— `GET /agregados/{agregado_id}/variaveis`.

---

### 11. `listar_periodos_agregado`

**Descrição**: lista os períodos disponíveis para consulta em um agregado do
SIDRA, cada um com `id` (ex.: `"2024"`) e `nome` (descrição textual do
período, quando disponível). Use o `id` de um período no parâmetro
`periodos` de [`consultar_agregado`](#13-consultar_agregado).

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `agregado_id` | `string` | sim | ID do agregado do SIDRA (ex.: `"6579"` = "População residente estimada"). |

**Exemplo de chamada**:

```python
listar_periodos_agregado(agregado_id="6579")
```

**Exemplo de resposta JSON** (lista truncada):

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos",
    "params": { "agregado_id": "6579" },
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": [
    { "id": "2023", "nome": "2023" },
    { "id": "2024", "nome": "2024" }
  ]
}
```

**Possíveis warnings**: nenhum.

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| `agregado_id` é uma string vazia/só espaços | `Parâmetro "agregado_id" não pode ser vazio.` |
| `agregado_id` não corresponde a nenhum agregado existente | `Agregado "<agregado_id>" não encontrado.` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**: [IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados)
— `GET /agregados/{agregado_id}/periodos`.

---

### 12. `listar_localidades_agregado`

**Descrição**: lista as localidades disponíveis para um agregado em um ou
mais níveis territoriais (ex.: `"N1"` = Brasil, `"N2"` = regiões, `"N3"` =
estados, `"N6"` = municípios). **Não há schema tipado** para este endpoint:
cada item é devolvido exatamente como veio da API (`id`, `nome`, `nivel`,
...). Use o `id` de uma localidade no parâmetro `localidades` de
[`consultar_agregado`](#13-consultar_agregado) (ex.: `"N6[3303302]"`).

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `agregado_id` | `string` | sim | ID do agregado do SIDRA (ex.: `"6579"` = "População residente estimada"). |
| `niveis` | `string` | sim | Nível territorial (ex.: `"N6"`) ou múltiplos níveis separados por `"\|"` (ex.: `"N1\|N3"`). |

**Exemplo de chamada**:

```python
listar_localidades_agregado(agregado_id="6579", niveis="N6")
```

**Exemplo de resposta JSON** (lista truncada):

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/localidades/N6",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/localidades/N6",
    "params": { "agregado_id": "6579", "niveis": "N6" },
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": [
    {
      "id": "3303302",
      "nome": "Niterói",
      "nivel": { "id": "N6", "nome": "Município" }
    },
    {
      "id": "3304557",
      "nome": "Rio de Janeiro",
      "nivel": { "id": "N6", "nome": "Município" }
    }
  ]
}
```

**Possíveis warnings**: nenhum.

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| `agregado_id` ou `niveis` é uma string vazia/só espaços | `Parâmetro "agregado_id" não pode ser vazio.` ou `Parâmetro "niveis" não pode ser vazio.` |
| Combinação `agregado_id`/`niveis` não retorna localidades (ex.: nível não suportado pelo agregado) | `Nenhuma localidade encontrada para o agregado "<agregado_id>" no(s) nível(is) "<niveis>".` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**: [IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados)
— `GET /agregados/{agregado_id}/localidades/{niveis}`.

---

### 13. `consultar_agregado`

**Descrição**: consulta valores de um agregado do SIDRA para variáveis,
períodos e localidades específicas. Retorna uma lista **achatada** de
valores — um item por combinação de (variável, localidade, período) —, cada
um com `agregado_id`, `variavel_id`, `localidade_id`, `localidade_nome`,
`periodo`, `valor` (número, ou `null` quando o dado é ausente/sigiloso no
SIDRA — marcadores `"-"`, `".."`, `"..."`, `"X"`) e `unidade`. O item de série
original da API fica em `raw`.

> Para descobrir IDs válidos de agregado, variáveis, períodos e localidades,
> siga [Como descobrir agregado, variável, período e
> localidade](#como-descobrir-agregado-variável-período-e-localidade), usando
> [`listar_agregados`](#8-listar_agregados),
> [`obter_metadados_agregado`](#9-obter_metadados_agregado),
> [`listar_variaveis_agregado`](#10-listar_variaveis_agregado),
> [`listar_periodos_agregado`](#11-listar_periodos_agregado) e
> [`listar_localidades_agregado`](#12-listar_localidades_agregado).

**Parâmetros**:

| Nome | Tipo | Obrigatório | Padrão | Descrição |
| --- | --- | --- | --- | --- |
| `agregado_id` | `string` | sim | — | ID do agregado do SIDRA (ex.: `"6579"`). |
| `variaveis` | `string` | sim | — | ID de variável, lista separada por vírgula (ex.: `"9324,9325"`), ou `"all"` para todas. |
| `localidades` | `string` | sim | — | Unidade territorial no formato `N<nivel>[<ids>]`, ex.: `"N1[all]"` (Brasil), `"N3[all]"` (todos os estados), `"N6[3303302]"` (Niterói). `"BR"` é aceito como atalho para `"N1[all]"`. |
| `periodos` | `string` | não | `"-6"` | Um ano (`"2021"`), intervalo (`"2010-2020"`), lista (`"2019,2021"`) ou relativo (`"-6"` = últimos 6 períodos, `"-1"` = último período disponível). |
| `classificacao` | `string \| null` | não | `null` | Classificação opcional, formato `"<id_classificacao>[<id_categoria>]"`. |
| `view` | `string \| null` | não | `null` | Formato alternativo de resposta da API (ex.: `"flat"`). |

**Exemplo de chamada**:

```python
consultar_agregado(
    agregado_id="6579",
    variaveis="9324",
    localidades="N6[3303302]",
    periodos="2024",
)
```

**Exemplo de resposta JSON**:

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2024/variaveis/9324",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2024/variaveis/9324",
    "params": {
      "agregado_id": "6579",
      "variaveis": "9324",
      "periodos": "2024",
      "localidades": "N6[3303302]"
    },
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": [
    {
      "agregado_id": "6579",
      "variavel_id": "9324",
      "localidade_id": "3303302",
      "localidade_nome": "Niterói",
      "periodo": "2024",
      "valor": 516981.0,
      "unidade": "Pessoas",
      "raw": {
        "localidade": { "id": "3303302", "nome": "Niterói", "nivel": { "id": "N6", "nome": "Município" } },
        "serie": { "2024": "516981" }
      }
    }
  ]
}
```

**Possíveis warnings**: nenhum diretamente desta tool. (Note que `valor` pode
vir `null` quando o SIDRA marca o dado como ausente/sigiloso — isso **não**
gera um `warning` aqui; ao contrário de
[`consultar_populacao_municipio`](#14-consultar_populacao_municipio), que
adiciona um aviso explícito nesse caso.)

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| `agregado_id`, `variaveis`, `localidades` ou `periodos` é uma string vazia/só espaços | `Parâmetro "<nome>" não pode ser vazio.` |
| Combinação de `agregado_id`/`variaveis`/`localidades`/`periodos` não retorna dados (IDs inexistentes, nível territorial não suportado, período fora do range, etc. — a API costuma responder HTTP 200 com corpo vazio nesses casos) | `Nenhum dado encontrado para o agregado "<agregado_id>", variável(is) "<variaveis>" em "<localidades>" no(s) período(s) "<periodos>".` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**: [IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados)
— `GET /agregados/{agregado_id}/periodos/{periodos}/variaveis/{variaveis}`
(com `localidades`, `classificacao` e `view` como query string).

---

### 14. `consultar_populacao_municipio`

**Descrição**: retorna a população residente estimada de um município,
identificado por `nome` e `uf`. Internamente:

1. Resolve o código IBGE do município via
   [`obter_codigo_municipio`](#5-obter_codigo_municipio) (mesma busca *fuzzy*
   por `nome`/`uf`).
2. Consulta o agregado SIDRA "Estimativas de população residente"
   (`agregado_id="6579"`, `variavel_id="9324"`) para esse município, usando
   [`consultar_agregado`](#13-consultar_agregado) internamente.

Retorna o mesmo formato "achatado" de `consultar_agregado` (lista de
`AgregadoQueryResult`).

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `nome` | `string` | sim | Nome do município. |
| `uf` | `string` | sim | Sigla (ex.: `"SP"`) ou código IBGE da UF. |
| `ano` | `integer \| null` | não | Ano de referência. Sem este parâmetro, usa o período mais recente disponível (`periodos="-1"`). |

**Exemplo de chamada**:

```python
consultar_populacao_municipio(nome="Niterói", uf="RJ")
```

**Exemplo de resposta JSON** (sem `ano` informado — período mais recente
disponível):

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324",
    "params": {
      "nome": "Niterói",
      "uf": "RJ",
      "codigo_municipio": 3303302,
      "agregado_id": "6579",
      "variaveis": "9324",
      "periodos": "-1",
      "localidades": "N6[3303302]"
    },
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": [
    {
      "agregado_id": "6579",
      "variavel_id": "9324",
      "localidade_id": "3303302",
      "localidade_nome": "Niterói",
      "periodo": "2024",
      "valor": 516981.0,
      "unidade": "Pessoas",
      "raw": {
        "localidade": { "id": "3303302", "nome": "Niterói", "nivel": { "id": "N6", "nome": "Município" } },
        "serie": { "2024": "516981" }
      }
    }
  ],
  "warnings": [
    "Nenhum \"ano\" foi informado: retornado o período mais recente disponível no SIDRA (\"2024\"), que pode não ser o ano corrente."
  ]
}
```

**Possíveis warnings**:

- `Nenhum "ano" foi informado: retornado o período mais recente disponível no SIDRA ("<periodo>"), que pode não ser o ano corrente.`
  — emitido quando o parâmetro `ano` não é informado (sempre que a consulta
  tem sucesso e retorna ao menos um item).
- `O valor de população não está disponível (dado ausente ou sigiloso no SIDRA) para um ou mais períodos retornados.`
  — emitido quando algum item de `data` tem `valor: null`.
- Avisos de [`obter_codigo_municipio`](#5-obter_codigo_municipio) (ex.: lista
  de candidatos quando `nome` é ambíguo) também são propagados em caso de
  erro.

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| Nenhum município corresponde a `nome`/`uf` | `Nenhum município encontrado para "<nome>" na UF "<uf>".` |
| `nome` é ambíguo dentro da `uf` informada | `Encontrados N municípios para "<nome>": <nomes>. Refine a busca com "uf" ou um nome mais específico.` |
| `uf` informada não corresponde a nenhuma sigla/código válido | `UF inválida: "XX". Use a sigla (ex.: "RJ") ou o código IBGE (ex.: "33").` |
| O agregado/variável de população (`6579`/`9324`) foi descontinuado, renomeado ou não retorna dados para o município/período | `Não foi possível obter a população do município <codigo_municipio> usando o agregado 6579 (variável 9324) do SIDRA: <detalhe>. Essa tabela pode ter sido descontinuada ou renomeada pelo IBGE. Use \`consultar_agregado\` diretamente, após localizar os IDs corretos com \`listar_agregados\`, \`obter_metadados_agregado\` e \`listar_variaveis_agregado\`.` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**:

- [IBGE Localidades API](https://servicodados.ibge.gov.br/api/docs/localidades)
  — `GET /localidades/estados/{uf}/municipios` (resolução do código IBGE).
- [IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados)
  — `GET /agregados/6579/periodos/{periodos}/variaveis/9324` (agregado
  "Estimativas de população residente", [SIDRA tabela 6579](https://sidra.ibge.gov.br/tabela/6579)).

---

## SIDRA Query Builder

A API de Agregados/SIDRA exige parâmetros difíceis de descobrir
(`agregado_id`, `variaveis`, `periodos`, `localidades`, `classificacao`,
`view`). As 7 tools abaixo formam uma camada de **descoberta, sugestão e
validação** sobre as tools de [Agregados / SIDRA](#agregados--sidra)
acima — ajudando um agente a montar uma consulta correta para
[`consultar_agregado`](#13-consultar_agregado) sem precisar adivinhar IDs.

> **Nenhuma etapa usa modelos de linguagem.** `sugerir_consulta_sidra` é uma
> heurística simples: extrai palavras-chave da pergunta (remoção de acentos,
> caixa e stopwords em português) e pontua agregados/variáveis pela
> ocorrência dessas palavras no `nome` retornado pela API, mais um pequeno
> dicionário de palavras-chave → nível territorial. O resultado é sempre uma
> **proposta** (`sugerir_consulta_sidra` nunca executa uma consulta) e
> sempre inclui `warnings` explicando a heurística e, quando houver,
> agregados alternativos.

Fluxo recomendado:

1. **Descobrir o agregado** — [`buscar_tabelas_sidra`](#15-buscar_tabelas_sidra)
   (por tema) ou [`sugerir_consulta_sidra`](#19-sugerir_consulta_sidra) (por
   pergunta em linguagem natural, retorna uma proposta completa).
2. **Entender o agregado** — [`explicar_tabela_sidra`](#16-explicar_tabela_sidra),
   [`listar_variaveis_tabela_sidra`](#17-listar_variaveis_tabela_sidra) e
   [`listar_classificacoes_tabela_sidra`](#18-listar_classificacoes_tabela_sidra).
3. **Validar antes de gastar uma requisição de dados** —
   [`validar_consulta_sidra`](#20-validar_consulta_sidra) verifica os
   parâmetros propostos contra os metadados reais do agregado.
4. **Executar com segurança** —
   [`executar_consulta_sidra_validada`](#21-executar_consulta_sidra_validada)
   repete a validação do passo 3 e só chama
   [`consultar_agregado`](#13-consultar_agregado) se ela passar.

---

### 15. `buscar_tabelas_sidra`

**Descrição**: busca agregados (tabelas) do SIDRA relacionados a `tema`, por
palavras-chave no `nome` de cada agregado retornado por
[`listar_agregados`](#8-listar_agregados). Cada item retornado inclui `id`,
`nome` e `pontuacao` (quantas palavras-chave de `tema` casaram com o nome),
ordenados por `pontuacao` decrescente.

**Parâmetros**:

| Nome | Tipo | Obrigatório | Padrão | Descrição |
| --- | --- | --- | --- | --- |
| `tema` | `string` | sim | — | Tema/assunto de interesse (ex.: `"população"`, `"inflação"`). |
| `limite` | `integer` | não | `10` | Número máximo de agregados retornados (`1`-`100`). |

**Exemplo de chamada**:

```python
buscar_tabelas_sidra(tema="população dos municípios")
```

**Exemplo de resposta JSON**:

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados",
    "params": { "tema": "população dos municípios", "limite": 10 },
    "retrieved_at": "2026-06-11T12:00:00.000000+00:00",
    "license_note": null
  },
  "data": [
    { "id": "6579", "nome": "População residente estimada", "pontuacao": 1 },
    { "id": "9514", "nome": "População residente, por sexo, situação e grupos de idade", "pontuacao": 1 }
  ]
}
```

**Possíveis warnings**:

- `Nenhum agregado encontrado para o tema "<tema>". Tente palavras-chave diferentes ou use \`listar_agregados\` para ver todos os agregados.`
  — emitido quando nenhuma palavra-chave de `tema` casa com o nome de nenhum
  agregado (`data: []`).

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| `limite` fora do intervalo `1`-`100` | `Parâmetro "limite" deve ser um inteiro entre 1 e 100.` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**: [IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados)
— `GET /agregados` (mesmo endpoint de [`listar_agregados`](#8-listar_agregados),
ranqueado localmente por palavras-chave).

---

### 16. `explicar_tabela_sidra`

**Descrição**: explica um agregado do SIDRA, a partir dos metadados de
[`obter_metadados_agregado`](#9-obter_metadados_agregado), já estruturados
para descoberta de consultas: `id`, `nome`, `pesquisa`, `assunto`,
`periodicidade` (`frequencia`, `inicio`, `fim`), `niveis_territoriais`
(ex.: `["N1", "N3", "N6"]`), `variaveis` (`id`, `nome`, `unidade`),
`classificacoes` (`id`, `nome`, `categorias`) e `limitacoes` — uma lista de
frases em texto que resume o intervalo de períodos, os níveis territoriais
suportados e se há classificações adicionais.

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `agregado_id` | `string` | sim | ID do agregado do SIDRA (ex.: `"6579"` = "População residente estimada"). |

**Exemplo de chamada**:

```python
explicar_tabela_sidra(agregado_id="6579")
```

**Exemplo de resposta JSON**:

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/metadados",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/metadados",
    "params": { "agregado_id": "6579" },
    "retrieved_at": "2026-06-11T12:00:00.000000+00:00",
    "license_note": null
  },
  "data": {
    "id": "6579",
    "nome": "População residente estimada",
    "pesquisa": "Estimativas de População",
    "assunto": "População",
    "periodicidade": { "frequencia": "anual", "inicio": 2001, "fim": 2024 },
    "niveis_territoriais": ["N1", "N2", "N3", "N6"],
    "variaveis": [
      { "id": "9324", "nome": "População residente estimada", "unidade": "Pessoas" }
    ],
    "classificacoes": [],
    "limitacoes": [
      "Dados disponíveis de 2001 a 2024 (anual).",
      "Níveis territoriais disponíveis: N1, N2, N3, N6.",
      "Esta tabela não possui classificações adicionais (apenas variáveis)."
    ]
  }
}
```

**Possíveis warnings**: nenhum.

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| `agregado_id` é uma string vazia/só espaços | `Parâmetro "agregado_id" não pode ser vazio.` |
| `agregado_id` não corresponde a nenhum agregado existente | `Agregado "<agregado_id>" não encontrado.` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**: [IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados)
— `GET /agregados/{agregado_id}/metadados` (mesmo endpoint de
[`obter_metadados_agregado`](#9-obter_metadados_agregado), reestruturado).

---

### 17. `listar_variaveis_tabela_sidra`

**Descrição**: lista as variáveis de um agregado, a partir dos metadados
estruturados (`AgregadoMetadataParsed.variaveis`) — cada item com `id`,
`nome` e `unidade`. Equivalente a
[`listar_variaveis_agregado`](#10-listar_variaveis_agregado), mas obtido de
`/metadados` em vez de `/variaveis`.

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `agregado_id` | `string` | sim | ID do agregado do SIDRA (ex.: `"6579"` = "População residente estimada"). |

**Exemplo de chamada**:

```python
listar_variaveis_tabela_sidra(agregado_id="6579")
```

**Exemplo de resposta JSON**:

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/metadados",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/metadados",
    "params": { "agregado_id": "6579" },
    "retrieved_at": "2026-06-11T12:00:00.000000+00:00",
    "license_note": null
  },
  "data": [
    { "id": "9324", "nome": "População residente estimada", "unidade": "Pessoas" }
  ]
}
```

**Possíveis warnings**: nenhum.

**Erros comuns**: os mesmos de [`explicar_tabela_sidra`](#16-explicar_tabela_sidra)
mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**: [IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados)
— `GET /agregados/{agregado_id}/metadados`.

---

### 18. `listar_classificacoes_tabela_sidra`

**Descrição**: lista as classificações de um agregado, a partir dos
metadados estruturados (`AgregadoMetadataParsed.classificacoes`) — cada item
com `id`, `nome` e `categorias` (cada categoria com `id` e `nome`). Uma lista
vazia indica que a tabela não possui classificações adicionais (apenas
variáveis). Use `"<id_classificacao>[<id_categoria>]"` no parâmetro
`classificacao` de [`validar_consulta_sidra`](#20-validar_consulta_sidra),
[`executar_consulta_sidra_validada`](#21-executar_consulta_sidra_validada) ou
[`consultar_agregado`](#13-consultar_agregado).

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `agregado_id` | `string` | sim | ID do agregado do SIDRA (ex.: `"7060"` = "IPCA - Variação mensal"). |

**Exemplo de chamada**:

```python
listar_classificacoes_tabela_sidra(agregado_id="7060")
```

**Exemplo de resposta JSON**:

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/7060/metadados",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/7060/metadados",
    "params": { "agregado_id": "7060" },
    "retrieved_at": "2026-06-11T12:00:00.000000+00:00",
    "license_note": null
  },
  "data": [
    {
      "id": "315",
      "nome": "Geral, grupo, subgrupo, item e subitem",
      "categorias": [{ "id": "7169", "nome": "Índice geral" }]
    }
  ]
}
```

**Possíveis warnings**: nenhum.

**Erros comuns**: os mesmos de [`explicar_tabela_sidra`](#16-explicar_tabela_sidra)
mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**: [IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados)
— `GET /agregados/{agregado_id}/metadados`.

---

### 19. `sugerir_consulta_sidra`

**Descrição**: sugere uma consulta SIDRA (`agregado_id`, `variaveis`,
`localidades`) para uma `pergunta` em linguagem natural — **sem executar
nenhuma consulta**. Internamente: (1) lista os agregados disponíveis
([`listar_agregados`](#8-listar_agregados)) e os ranqueia por palavras-chave
extraídas de `pergunta`; (2) obtém os metadados do agregado com maior
pontuação ([`explicar_tabela_sidra`](#16-explicar_tabela_sidra)); (3) sugere a
variável cujo nome melhor pontua para as mesmas palavras-chave; (4) sugere o
nível territorial (`localidades`) a partir de um pequeno dicionário de
palavras-chave (ex.: "município"/"cidades" → `"N6[all]"`, "estado"/"UF" →
`"N3[all]"`, "Brasil"/"nacional" → `"N1[all]"`, padrão `"N1[all]"`).
`alternativas` traz até 5 outros agregados que também casaram com a pergunta.

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `pergunta` | `string` | sim | Pergunta em linguagem natural (ex.: `"qual a população estimada dos municípios em 2024?"`). |

**Exemplo de chamada**:

```python
sugerir_consulta_sidra(pergunta="qual a população estimada dos municípios em 2024?")
```

**Exemplo de resposta JSON**:

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/metadados",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/metadados",
    "params": {
      "pergunta": "qual a população estimada dos municípios em 2024?",
      "agregado_id": "6579"
    },
    "retrieved_at": "2026-06-11T12:00:00.000000+00:00",
    "license_note": null
  },
  "data": {
    "agregado_id": "6579",
    "agregado_nome": "População residente estimada",
    "variaveis": "9324",
    "variavel_nome": "População residente estimada",
    "localidades": "N6[all]",
    "periodos": "-1",
    "classificacao": null,
    "alternativas": [
      { "id": "9514", "nome": "População residente, por sexo, situação e grupos de idade", "pontuacao": 1 }
    ]
  },
  "warnings": [
    "Sugestão gerada por busca de palavras-chave em metadados (sem uso de modelos de linguagem); revise os parâmetros antes de executar, com `validar_consulta_sidra` ou `explicar_tabela_sidra`.",
    "Outros agregados também correspondem à pergunta: 9514 (População residente, por sexo, situação e grupos de idade)."
  ]
}
```

**Possíveis warnings**:

- O aviso sobre a heurística sem LLM acima é **sempre** retornado em caso de
  sucesso.
- `Outros agregados também correspondem à pergunta: <id> (<nome>), ...` —
  emitido quando mais de um agregado casa com `pergunta` (até 3 listados).
- `O agregado "<agregado_id>" não possui variáveis informadas.` — emitido
  quando o agregado escolhido não tem variáveis em seus metadados
  (`variaveis` é retornado como `"all"` e `variavel_nome` como `null`).

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| Nenhuma palavra-chave de `pergunta` casa com o nome de nenhum agregado | `Não foi possível identificar um agregado para a pergunta "<pergunta>". Tente reformular com termos mais específicos (ex.: o nome de um indicador) ou use \`buscar_tabelas_sidra\`/\`listar_agregados\`.` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**: [IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados)
— `GET /agregados` (ranqueamento) e `GET /agregados/{agregado_id}/metadados`
(do agregado escolhido).

---

### 20. `validar_consulta_sidra`

**Descrição**: valida `variaveis`, `localidades`, `periodos` e
`classificacao` para um `agregado_id`, em duas etapas: (1) valida o
**formato** de cada parâmetro com `mcp_ibge.utils.validators` (os mesmos
validadores usados por [`consultar_agregado`](#13-consultar_agregado)); (2)
obtém os metadados do agregado
([`explicar_tabela_sidra`](#16-explicar_tabela_sidra)) e verifica se os
valores informados **existem de fato** nesse agregado. `ok=false` (com
`errors`) se o formato for inválido, os metadados não puderem ser obtidos, ou
nenhuma variável/nível territorial válido for encontrado. Problemas que não
impedem a consulta (variável/nível parcialmente inválido, período fora do
intervalo conhecido) aparecem em `avisos` dentro de `data`, não em `errors`.

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `agregado_id` | `string` | sim | ID do agregado do SIDRA (ex.: `"6579"`). |
| `variaveis` | `string` | sim | ID de variável, lista separada por `\|` (ex.: `"93\|1000093"`) ou `"all"`. |
| `localidades` | `string` | sim | Unidade territorial no formato `N<nivel>[<ids>]`, ex.: `"N1[all]"`, `"N3[all]"`, `"N6[3550308]"`. |
| `periodos` | `string` | sim | Um ano (`"2021"`), intervalo (`"2010-2020"`), lista (`"2020\|2021\|2022"`) ou relativo (`"-1"`, `"-6"`). |
| `classificacao` | `string \| null` | não | Formato `"<id_classificacao>[<id_categoria>,...]"` (ex.: `"315[7169]"`). |

**Exemplo de chamada**:

```python
validar_consulta_sidra(
    agregado_id="6579",
    variaveis="9324",
    localidades="N6[3550308]",
    periodos="2024",
)
```

**Exemplo de resposta JSON** (consulta válida):

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/metadados",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/metadados",
    "params": {
      "agregado_id": "6579",
      "variaveis": "9324",
      "localidades": "N6[3550308]",
      "periodos": "2024"
    },
    "retrieved_at": "2026-06-11T12:00:00.000000+00:00",
    "license_note": null
  },
  "data": {
    "valido": true,
    "agregado_id": "6579",
    "variaveis_validas": ["9324"],
    "variaveis_invalidas": [],
    "niveis_territoriais": ["N6"],
    "niveis_invalidos": [],
    "classificacao_valida": null,
    "erros": [],
    "avisos": []
  }
}
```

**Exemplo de resposta JSON** (variável inexistente — `ok: false`):

```json
{
  "data": {
    "valido": false,
    "agregado_id": "6579",
    "variaveis_validas": [],
    "variaveis_invalidas": ["99999"],
    "niveis_territoriais": ["N6"],
    "niveis_invalidos": [],
    "classificacao_valida": null,
    "erros": [
      "Nenhuma das variáveis \"99999\" existe no agregado \"6579\". Use `listar_variaveis_tabela_sidra` para ver as variáveis disponíveis."
    ],
    "avisos": []
  },
  "errors": [
    "Nenhuma das variáveis \"99999\" existe no agregado \"6579\". Use `listar_variaveis_tabela_sidra` para ver as variáveis disponíveis."
  ]
}
```

**Possíveis warnings** (em `data.avisos`, e também em `warnings` quando
`valido=true`):

- `Variável(is) "<ids>" não encontrada(s) no agregado "<agregado_id>" e será(ão) ignorada(s).`
- `Nível(is) territorial(is) "<niveis>" não disponível(is) no agregado "<agregado_id>".`
- `Período "<periodo>" está fora do intervalo informado pela API para o agregado <agregado_id> (<inicio>-<fim>).`

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| Formato de `agregado_id`/`variaveis`/`localidades`/`periodos` inválido | mensagens de `mcp_ibge.utils.validators` (mesmas de [`consultar_agregado`](#13-consultar_agregado)) |
| `agregado_id` não corresponde a nenhum agregado existente | `Agregado "<agregado_id>" não encontrado.` |
| Nenhuma variável de `variaveis` existe no agregado | `Nenhuma das variáveis "<variaveis>" existe no agregado "<agregado_id>". Use \`listar_variaveis_tabela_sidra\` para ver as variáveis disponíveis.` |
| Nenhum nível territorial de `localidades` está disponível no agregado | `Nenhum dos níveis territoriais de "<localidades>" está disponível no agregado "<agregado_id>" (disponíveis: <niveis>).` |
| `classificacao` com `id_classificacao`/`id_categoria` inexistente | `Classificação "<id>" não existe no agregado "<agregado_id>". Use \`listar_classificacoes_tabela_sidra\` para ver as classificações disponíveis.` ou `Categoria(s) "<ids>" não existe(m) na classificação "<id>" do agregado "<agregado_id>".` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**: [IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados)
— `GET /agregados/{agregado_id}/metadados`. **Não consulta**
`/agregados/{agregado_id}/periodos/.../variaveis/...` (a validação é local,
contra os metadados já obtidos).

---

### 21. `executar_consulta_sidra_validada`

**Descrição**: valida a consulta contra os metadados do agregado — mesma
lógica de [`validar_consulta_sidra`](#20-validar_consulta_sidra) — e **só a
executa** ([`consultar_agregado`](#13-consultar_agregado)) se `data.valido`
for `true`. Se a validação falhar, retorna `ok=false` com os mesmos
`errors`/`warnings` de `validar_consulta_sidra` e **nenhuma requisição
adicional é feita** (a tool não chama `/periodos/.../variaveis/...` nesse
caso). Em caso de sucesso, `data` é a mesma lista "achatada" de
[`AgregadoQueryResult`](#13-consultar_agregado), e `warnings` combina os
avisos da validação com os avisos da consulta.

**Parâmetros**:

| Nome | Tipo | Obrigatório | Padrão | Descrição |
| --- | --- | --- | --- | --- |
| `agregado_id` | `string` | sim | — | ID do agregado do SIDRA (ex.: `"6579"`). |
| `variaveis` | `string` | sim | — | ID de variável, lista separada por `\|` (ex.: `"93\|1000093"`) ou `"all"`. |
| `localidades` | `string` | sim | — | Unidade territorial no formato `N<nivel>[<ids>]`, ex.: `"N1[all]"`, `"N6[3550308]"`. |
| `periodos` | `string` | não | `"-6"` | Um ano, intervalo, lista ou relativo (`"-1"` = último período disponível). |
| `classificacao` | `string \| null` | não | `null` | Formato `"<id_classificacao>[<id_categoria>,...]"`. |
| `view` | `string \| null` | não | `null` | Formato alternativo de resposta da API (ex.: `"flat"`). |

**Exemplo de chamada**:

```python
executar_consulta_sidra_validada(
    agregado_id="6579",
    variaveis="9324",
    localidades="N6[3550308]",
    periodos="2024",
)
```

**Exemplo de resposta JSON** (válida — executa e retorna os dados):

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2024/variaveis/9324",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2024/variaveis/9324",
    "params": {
      "agregado_id": "6579",
      "variaveis": "9324",
      "localidades": "N6[3550308]",
      "periodos": "2024"
    },
    "retrieved_at": "2026-06-11T12:00:00.000000+00:00",
    "license_note": null
  },
  "data": [
    {
      "agregado_id": "6579",
      "variavel_id": "9324",
      "localidade_id": "3550308",
      "localidade_nome": "São Paulo",
      "periodo": "2024",
      "valor": 11451245.0,
      "unidade": "Pessoas",
      "raw": { "...": "..." }
    }
  ],
  "warnings": []
}
```

**Exemplo de resposta JSON** (inválida — não executa a consulta):

```json
{
  "metadata": {
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/metadados",
    "params": {
      "agregado_id": "6579",
      "variaveis": "99999",
      "localidades": "N6[3550308]",
      "periodos": "2024"
    }
  },
  "data": [],
  "errors": [
    "Nenhuma das variáveis \"99999\" existe no agregado \"6579\". Use `listar_variaveis_tabela_sidra` para ver as variáveis disponíveis."
  ]
}
```

**Possíveis warnings**: os mesmos de
[`validar_consulta_sidra`](#20-validar_consulta_sidra), combinados com os de
[`consultar_agregado`](#13-consultar_agregado) (nenhum diretamente, hoje).

**Erros comuns**: os mesmos de
[`validar_consulta_sidra`](#20-validar_consulta_sidra) e de
[`consultar_agregado`](#13-consultar_agregado), mais os [erros comuns a todas
as tools](#erros-comuns-a-todas-as-tools). Se a validação passar mas a
consulta não retornar dados, `errors` traz a mesma mensagem de
`consultar_agregado` (`Nenhum dado encontrado para o agregado "<agregado_id>"...`).

**Fonte usada**: [IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados)
— `GET /agregados/{agregado_id}/metadados` (validação) e, se válida,
`GET /agregados/{agregado_id}/periodos/{periodos}/variaveis/{variaveis}`
(mesmo endpoint de [`consultar_agregado`](#13-consultar_agregado)).

---

## Perfil Municipal

### 22. `gerar_perfil_municipal`

**Descrição**: gera um perfil básico de um município a partir de `nome` e
`uf`, combinando as tools de Localidades e de Indicadores em uma única
resposta estruturada. Internamente:

1. Resolve o código IBGE do município via
   [`obter_codigo_municipio`](#5-obter_codigo_municipio) (mesma busca
   *fuzzy* por `nome`/`uf`, com os mesmos `warnings`/`errors` em caso de
   ambiguidade ou município não encontrado).
2. Obtém os detalhes do município via
   [`obter_municipio_por_codigo`](#6-obter_municipio_por_codigo): `nome`,
   código IBGE, UF e região, mais a microrregião ou região intermediária
   (extraída do JSON bruto retornado pela API de Localidades).
3. Consulta a população residente estimada via
   [`consultar_populacao_municipio`](#14-consultar_populacao_municipio).

A resposta separa claramente **dados obtidos** (`indicadores`, com fonte
rastreável) de **sugestões** (`proximos_indicadores_sugeridos`, apenas nomes
de indicadores ainda não implementados — nunca valores). Indicadores que não
puderem ser obtidos com segurança não aparecem em `indicadores`; em vez
disso, a resposta inclui um `warning` explicando o motivo.

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `nome` | `string` | sim | Nome do município. |
| `uf` | `string` | sim | Sigla (ex.: `"RJ"`) ou código IBGE da UF. |
| `ano` | `integer \| null` | não | Ano de referência para o indicador de população. Sem este parâmetro, usa o período mais recente disponível (`periodos="-1"`). |

**Exemplo de chamada**:

```python
gerar_perfil_municipal(nome="Rio de Janeiro", uf="RJ")
```

**Exemplo de resposta JSON** (sem `ano` informado — período mais recente
disponível):

```json
{
  "ok": true,
  "data": {
    "municipio": {
      "codigo_ibge": 3304557,
      "nome": "Rio de Janeiro",
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
        "valor": 6211423.0,
        "unidade": "Pessoas",
        "periodo": "2024",
        "agregado_id": "6579",
        "variavel_id": "9324"
      }
    ],
    "fontes": [
      "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3304557",
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
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3304557",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3304557",
    "params": {
      "nome": "Rio de Janeiro",
      "uf": "RJ",
      "municipio_id": 3304557
    },
    "retrieved_at": "2026-06-11T12:00:00.000000+00:00",
    "license_note": null
  },
  "warnings": [
    "Nenhum \"ano\" foi informado para a população: retornado o período mais recente disponível no SIDRA (\"2024\")."
  ],
  "errors": []
}
```

**Possíveis warnings**:

- `Nenhum "ano" foi informado para a população: retornado o período mais recente disponível no SIDRA ("<periodo>").`
  — emitido quando o parâmetro `ano` não é informado e a população foi
  obtida com sucesso.
- `Indicador de população não disponível: o SIDRA não retornou um valor para este município/período (dado ausente ou sigiloso).`
  — emitido quando a consulta de população tem sucesso, mas o valor é
  `null` (dado ausente/sigiloso); nesse caso, `indicadores` não inclui a
  população.
- `Indicador de população não pôde ser obtido: <detalhe>`
  — emitido quando a consulta de população falha (ex.: agregado/variável
  descontinuado pelo IBGE); nesse caso, `indicadores` não inclui a
  população.
- Avisos de [`obter_codigo_municipio`](#5-obter_codigo_municipio) (ex.: lista
  de candidatos quando `nome` é ambíguo) também são propagados em caso de
  erro.

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| Nenhum município corresponde a `nome`/`uf` | `Nenhum município encontrado para "<nome>" na UF "<uf>".` |
| `nome` é ambíguo dentro da `uf` informada | `Encontrados N municípios para "<nome>": <nomes>. Refine a busca com "uf" ou um nome mais específico.` |
| `uf` informada não corresponde a nenhuma sigla/código válido | `UF inválida: "XX". Use a sigla (ex.: "RJ") ou o código IBGE (ex.: "33").` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**:

- [IBGE Localidades API](https://servicodados.ibge.gov.br/api/docs/localidades)
  — `GET /localidades/estados/{uf}/municipios` (resolução do código IBGE) e
  `GET /localidades/municipios/{id}` (identificação, UF, região,
  microrregião/região intermediária).
- [IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados)
  — `GET /agregados/6579/periodos/{periodos}/variaveis/9324` (agregado
  "Estimativas de população residente", [SIDRA tabela 6579](https://sidra.ibge.gov.br/tabela/6579)).

---

## Comparação de Municípios

### 23. `comparar_municipios`

**Descrição**: compara múltiplos municípios (até `MAX_MUNICIPIOS = 10`) com
base em indicadores oficiais do IBGE, retornando uma tabela estruturada
pronta para um agente apresentar. Para cada município informado (`nome` +
`uf`):

1. Resolve o código IBGE via
   [`obter_codigo_municipio`](#5-obter_codigo_municipio) (mesma busca
   *fuzzy*). Municípios não encontrados ou com nome ambíguo na UF informada
   não interrompem a comparação: aparecem em `municipios_nao_resolvidos`,
   com o `motivo`.
2. Obtém os detalhes via
   [`obter_municipio_por_codigo`](#6-obter_municipio_por_codigo): `nome`,
   código IBGE, UF e região.
3. Consulta, para cada município resolvido, os indicadores solicitados que
   já estão implementados com segurança (por ora, apenas a população
   residente estimada, via
   [`consultar_populacao_municipio`](#14-consultar_populacao_municipio)).

Indicadores solicitados em `indicadores` que ainda não são suportados não
interrompem a comparação: são listados (apenas o nome, nunca dados) em
`indicadores_nao_implementados`, com um `warning` explicando o motivo. Se
`indicadores` não for informado, usa os indicadores básicos disponíveis
(atualmente, `["populacao"]`).

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `municipios` | `list[{"nome": string, "uf": string}]` | sim | Municípios a comparar (1 a 10), cada um com `nome` e `uf` (sigla ou código IBGE da UF). |
| `indicadores` | `list[string] \| null` | não | Nomes dos indicadores a comparar (ex.: `["populacao"]`). Sem este parâmetro, usa os indicadores básicos disponíveis. |
| `ano` | `integer \| null` | não | Ano de referência para os indicadores. Sem este parâmetro, usa o período mais recente disponível no SIDRA para cada município. |

**Exemplo de chamada**:

```python
comparar_municipios(
    municipios=[
        {"nome": "Rio de Janeiro", "uf": "RJ"},
        {"nome": "Niterói", "uf": "RJ"},
        {"nome": "Maricá", "uf": "RJ"},
    ]
)
```

**Exemplo de resposta JSON** (sem `ano` informado — período mais recente
disponível):

```json
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
      }
    ],
    "municipios_nao_resolvidos": [],
    "indicadores_consultados": ["populacao_estimada"],
    "indicadores_nao_implementados": [],
    "fontes": [
      "https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios",
      "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3304557",
      "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324",
      "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3303302"
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
        {"nome": "Niterói", "uf": "RJ"}
      ],
      "indicadores": ["populacao_estimada"],
      "ano": null
    },
    "retrieved_at": "2026-06-11T12:00:00.000000+00:00",
    "license_note": null
  },
  "warnings": [],
  "errors": []
}
```

**Possíveis warnings**:

- `Indicador "<nome>" não está implementado e foi ignorado. Indicadores disponíveis atualmente: "populacao" (população residente estimada).`
  — emitido para cada item de `indicadores` que não corresponde a um
  indicador suportado; o nome é incluído em
  `indicadores_nao_implementados` e a comparação continua com os demais.
- Avisos de [`obter_codigo_municipio`](#5-obter_codigo_municipio) (ex.: lista
  de candidatos quando `nome` é ambíguo dentro da `uf`) também são
  propagados; o município correspondente aparece em
  `municipios_nao_resolvidos`.
- `Não foi possível obter a população de "<nome>": <detalhe>` /
  `População não disponível para "<nome>" (dado ausente ou sigiloso no SIDRA).`
  — emitidos quando a consulta de população falha ou retorna `null` para um
  município; nesse caso, o indicador simplesmente não aparece em
  `indicadores` para esse município.

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| `municipios` vazio | `Informe ao menos um município em "municipios".` |
| `municipios` com mais de `MAX_MUNICIPIOS` itens | `No máximo 10 municípios por chamada (recebidos N).` |
| Nenhum dos municípios informados pôde ser resolvido | `Nenhum dos municípios informados pôde ser resolvido.` (mais os `warnings` de cada município, com o motivo individual) |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**:

- [IBGE Localidades API](https://servicodados.ibge.gov.br/api/docs/localidades)
  — `GET /localidades/estados/{uf}/municipios` (resolução do código IBGE) e
  `GET /localidades/municipios/{id}` (identificação, UF, região) para cada
  município.
- [IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados)
  — `GET /agregados/6579/periodos/{periodos}/variaveis/9324` (agregado
  "Estimativas de população residente", [SIDRA tabela 6579](https://sidra.ibge.gov.br/tabela/6579))
  para cada município, quando o indicador de população é consultado.

---

## Geoespacial

As tools desta seção consultam a
[API de Malhas do IBGE](https://servicodados.ibge.gov.br/api/docs/malhas) e
retornam `data` como um objeto [GeoJSON](https://geojson.org/) válido (RFC
7946) — `FeatureCollection`, `Feature` ou uma geometria diretamente.

Cada malha pode ser pedida em duas qualidades:

- `simplificado=true` (padrão): qualidade `"minima"` da malha — resposta bem
  menor, adequada para visualização em mapas. A resposta inclui um `warning`
  avisando que a geometria foi simplificada.
- `simplificado=false`: qualidade `"maxima"` — geometria mais detalhada, que
  pode ser bem maior e, em municípios/UFs grandes, ultrapassar o
  [limite de tamanho de resposta](#erros-comuns-a-todas-as-tools)
  (`Settings.max_response_size_bytes`, 5 MB por padrão), retornando um erro
  de servidor nesse caso.

### 24. `obter_malha_municipio`

**Descrição**: retorna a malha geográfica (GeoJSON) de um município, pelo
código IBGE.

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `codigo_ibge` | `integer` | sim | Código IBGE de 7 dígitos do município (ex.: `3304557`). |
| `simplificado` | `boolean` | não (padrão `true`) | Se `true`, retorna a malha simplificada (qualidade `"minima"`); se `false`, a malha mais detalhada (qualidade `"maxima"`). |

**Exemplo de chamada**:

```python
obter_malha_municipio(codigo_ibge=3303302)
```

**Exemplo de resposta JSON** (geometria simplificada para fins de exemplo):

```json
{
  "ok": true,
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "properties": { "codarea": "3303302" },
        "geometry": {
          "type": "Polygon",
          "coordinates": [[[-43.13, -22.92], [-43.13, -22.86], [-43.05, -22.86], [-43.05, -22.92], [-43.13, -22.92]]]
        }
      }
    ]
  },
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3303302",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3303302",
    "params": { "codigo_ibge": 3303302, "qualidade": "minima" },
    "territorial_level": "N6",
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "license_note": null
  },
  "warnings": [
    {
      "message": "Geometria simplificada (qualidade \"minima\" da malha do IBGE): adequada para visualização em mapas, mas não para análises que exigem precisão geométrica/cartográfica.",
      "code": null
    }
  ],
  "errors": []
}
```

**Possíveis warnings**:

- `Geometria simplificada (qualidade "minima" da malha do IBGE): adequada
  para visualização em mapas, mas não para análises que exigem precisão
  geométrica/cartográfica.` — emitido sempre que `simplificado=true`
  (padrão).

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| `codigo_ibge` não tem 7 dígitos | `Código de município inválido: "<valor>". Deve ser o código IBGE de 7 dígitos (ex.: 3550308).` |
| API não retorna um GeoJSON válido para o código informado | `A malha do município <codigo_ibge> não retornou um GeoJSON válido.` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools)
(incluindo o limite de tamanho de resposta, relevante com
`simplificado=false`).

**Fonte usada**: [IBGE API de Malhas](https://servicodados.ibge.gov.br/api/docs/malhas)
— `GET /malhas/municipios/{id}?formato=application/vnd.geo+json&qualidade=...`.

---

### 25. `obter_malha_uf`

**Descrição**: retorna a malha geográfica (GeoJSON) de uma UF.

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `uf` | `string` | sim | Sigla da UF (ex.: `"RJ"`) ou código IBGE da UF (ex.: `"33"`). |
| `simplificado` | `boolean` | não (padrão `true`) | Se `true`, retorna a malha simplificada (qualidade `"minima"`); se `false`, a malha mais detalhada (qualidade `"maxima"`). |

**Exemplo de chamada**:

```python
obter_malha_uf(uf="RJ")
```

**Exemplo de resposta JSON** (geometria simplificada para fins de exemplo):

```json
{
  "ok": true,
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "properties": { "codarea": "33" },
        "geometry": {
          "type": "Polygon",
          "coordinates": [[[-44.9, -23.4], [-44.9, -20.8], [-40.9, -20.8], [-40.9, -23.4], [-44.9, -23.4]]]
        }
      }
    ]
  },
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/malhas/estados/RJ",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/malhas/estados/RJ",
    "params": { "uf": "RJ", "qualidade": "minima" },
    "territorial_level": "N3",
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "license_note": null
  },
  "warnings": [
    {
      "message": "Geometria simplificada (qualidade \"minima\" da malha do IBGE): adequada para visualização em mapas, mas não para análises que exigem precisão geométrica/cartográfica.",
      "code": null
    }
  ],
  "errors": []
}
```

**Possíveis warnings**: o mesmo aviso de geometria simplificada de
[`obter_malha_municipio`](#24-obter_malha_municipio), emitido sempre que
`simplificado=true` (padrão).

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| `uf` não corresponde a nenhuma sigla/código válido | `UF inválida: "XX". Use a sigla (ex.: "RJ") ou o código IBGE (ex.: "33").` |
| API não retorna um GeoJSON válido para a UF informada | `A malha da UF "<uf>" não retornou um GeoJSON válido.` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools)
(incluindo o limite de tamanho de resposta, relevante com
`simplificado=false` em UFs grandes).

**Fonte usada**: [IBGE API de Malhas](https://servicodados.ibge.gov.br/api/docs/malhas)
— `GET /malhas/estados/{uf}?formato=application/vnd.geo+json&qualidade=...`.

---

### 26. `obter_bbox_municipio`

**Descrição**: retorna o bounding box (caixa delimitadora) de um município,
em coordenadas WGS84 (graus decimais), calculado localmente a partir da
malha simplificada (qualidade `"minima"`) do município. Útil para centralizar
ou enquadrar um mapa sem precisar processar a geometria completa.

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `codigo_ibge` | `integer` | sim | Código IBGE de 7 dígitos do município (ex.: `3304557`). |

**Exemplo de chamada**:

```python
obter_bbox_municipio(codigo_ibge=3303302)
```

**Exemplo de resposta JSON**:

```json
{
  "ok": true,
  "data": {
    "min_longitude": -43.13,
    "min_latitude": -22.92,
    "max_longitude": -43.05,
    "max_latitude": -22.86,
    "bbox": [-43.13, -22.92, -43.05, -22.86]
  },
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3303302",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3303302",
    "params": { "codigo_ibge": 3303302, "qualidade": "minima" },
    "territorial_level": "N6",
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "license_note": null
  },
  "warnings": [
    {
      "message": "Geometria simplificada (qualidade \"minima\" da malha do IBGE): adequada para visualização em mapas, mas não para análises que exigem precisão geométrica/cartográfica.",
      "code": null
    }
  ],
  "errors": []
}
```

`bbox` segue o formato `[west, south, east, north]` do GeoJSON (campo `bbox`
de uma `FeatureCollection`/`Feature`), enquanto `min_longitude`,
`min_latitude`, `max_longitude` e `max_latitude` repetem os mesmos valores
nomeados.

**Possíveis warnings**:

- O mesmo aviso de geometria simplificada de
  [`obter_malha_municipio`](#24-obter_malha_municipio) — sempre presente,
  pois o bounding box é calculado a partir da malha simplificada.

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| `codigo_ibge` não tem 7 dígitos | `Código de município inválido: "<valor>". Deve ser o código IBGE de 7 dígitos (ex.: 3550308).` |
| A malha retornada não contém geometria válida | `Não foi possível calcular o bounding box do município <codigo_ibge>: a malha retornada não contém geometria válida.` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**: [IBGE API de Malhas](https://servicodados.ibge.gov.br/api/docs/malhas)
— `GET /malhas/municipios/{id}?formato=application/vnd.geo+json&qualidade=minima`
(bounding box calculado localmente a partir da geometria retornada).

---

### 27. `gerar_geojson_municipios`

**Descrição**: combina a malha simplificada de até `MAX_MUNICIPIOS_GEOJSON =
10` municípios em uma única `FeatureCollection` GeoJSON, com uma `Feature`
por município (`properties.codigo_ibge` + a geometria da malha simplificada).
Útil para montar um mapa com vários municípios em uma só consulta.

Códigos IBGE que não retornarem uma malha válida não interrompem a geração:
aparecem em `data.codigos_nao_resolvidos`, com o `motivo`.

**Parâmetros**:

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `codigos_ibge` | `list[integer]` | sim | Códigos IBGE de 7 dígitos dos municípios (1 a 10), ex.: `[3304557, 3303302]`. |

**Exemplo de chamada**:

```python
gerar_geojson_municipios(codigos_ibge=[3304557, 3303302])
```

**Exemplo de resposta JSON** (geometrias simplificadas para fins de exemplo):

```json
{
  "ok": true,
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "properties": { "codigo_ibge": 3304557 },
        "geometry": { "type": "Polygon", "coordinates": [[["...", "..."]]] }
      },
      {
        "type": "Feature",
        "properties": { "codigo_ibge": 3303302 },
        "geometry": {
          "type": "Polygon",
          "coordinates": [[[-43.13, -22.92], [-43.13, -22.86], [-43.05, -22.86], [-43.05, -22.92], [-43.13, -22.92]]]
        }
      }
    ],
    "codigos_nao_resolvidos": []
  },
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3304557",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3304557",
    "params": {
      "codigos_ibge": [3304557, 3303302],
      "endpoints": [
        "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3304557",
        "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3303302"
      ]
    },
    "territorial_level": "N6",
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "license_note": null
  },
  "warnings": [
    {
      "message": "Geometria simplificada (qualidade \"minima\" da malha do IBGE): adequada para visualização em mapas, mas não para análises que exigem precisão geométrica/cartográfica.",
      "code": null
    }
  ],
  "errors": []
}
```

`codigos_nao_resolvidos` é um membro adicional do GeoJSON (um "foreign
member", permitido pela RFC 7946) com a lista de `{"codigo_ibge", "motivo"}`
dos códigos que não retornaram malha válida.

**Possíveis warnings**:

- O aviso de geometria simplificada de
  [`obter_malha_municipio`](#24-obter_malha_municipio) — sempre presente,
  pois esta tool sempre usa a malha simplificada (qualidade `"minima"`), para
  manter o tamanho da resposta combinada sob controle.
- `Códigos IBGE sem malha válida (ver `data.codigos_nao_resolvidos`): <códigos>`
  — emitido quando ao menos um código não retorna malha válida, mas pelo
  menos um outro código é resolvido.

**Erros comuns**:

| Situação | Mensagem (`error`) |
| --- | --- |
| `codigos_ibge` vazio | `Informe ao menos um código IBGE em "codigos_ibge".` |
| `codigos_ibge` com mais de `MAX_MUNICIPIOS_GEOJSON` itens | `No máximo 10 municípios por chamada (recebidos N).` |
| Nenhum dos códigos informados pôde ser resolvido | `Nenhum dos códigos IBGE informados pôde ser resolvido.` |
| `codigos_ibge` com algum código que não tem 7 dígitos | `Código de município inválido: "<valor>". Deve ser o código IBGE de 7 dígitos (ex.: 3550308).` |

Mais os [erros comuns a todas as tools](#erros-comuns-a-todas-as-tools).

**Fonte usada**: [IBGE API de Malhas](https://servicodados.ibge.gov.br/api/docs/malhas)
— `GET /malhas/municipios/{id}?formato=application/vnd.geo+json&qualidade=minima`
para cada município informado.

---

## Resources e prompts

Além das 23 tools acima, o servidor expõe:

- **Resource `ibge://status`**: status do servidor — `status`, `server`,
  `version`, lista de `tools` disponíveis e `timestamp` (UTC, ISO 8601). Não
  consulta a API do IBGE.
- **Prompt `comparar_municipios`**: orienta a comparação de um indicador
  (padrão: `"população"`) entre municípios informados, guiando o uso da tool
  [`comparar_municipios`](#23-comparar_municipios) (que já resolve os
  códigos IBGE e consulta os indicadores básicos disponíveis) e, se
  necessário, das tools de SIDRA (`listar_agregados`/
  `obter_metadados_agregado`/`listar_variaveis_agregado`/
  `consultar_agregado`) para indicadores ainda não suportados — exigindo que
  a resposta final cite fonte, período, unidade e limitações
  (`municipios_nao_resolvidos`, `indicadores_nao_implementados`,
  `warnings`).
