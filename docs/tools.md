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

**Agregados / SIDRA** (experimental na v0.1.0 — funcionais e testadas, mas a
interface pode mudar antes de serem marcadas como estáveis)

8. [`listar_agregados`](#8-listar_agregados)
9. [`obter_metadados_agregado`](#9-obter_metadados_agregado)
10. [`listar_variaveis_agregado`](#10-listar_variaveis_agregado)
11. [`listar_periodos_agregado`](#11-listar_periodos_agregado)
12. [`listar_localidades_agregado`](#12-listar_localidades_agregado)
13. [`consultar_agregado`](#13-consultar_agregado)
14. [`consultar_populacao_municipio`](#14-consultar_populacao_municipio)

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

> **Experimental na v0.1.0**: estas tools são funcionais e têm cobertura de
> testes, mas sua interface (parâmetros, formatos aceitos) ainda pode mudar
> em versões futuras antes de serem marcadas como estáveis. Veja o
> [Roadmap no README](../README.md#roadmap).

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

> Para descobrir IDs válidos de variáveis, períodos e localidades, use
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

## Resources e prompts

Além das 14 tools acima, o servidor expõe:

- **Resource `ibge://status`**: status do servidor — `status`, `server`,
  `version`, lista de `tools` disponíveis e `timestamp` (UTC, ISO 8601). Não
  consulta a API do IBGE.
- **Prompt `comparar_municipios`**: orienta a comparação de um indicador
  (padrão: `"população"`) entre municípios informados, guiando o uso de
  `obter_codigo_municipio`, `listar_agregados`/`obter_metadados_agregado`/
  `listar_variaveis_agregado`, `consultar_agregado`/
  `consultar_populacao_municipio`, e exigindo que a resposta final cite
  fonte, período, unidade territorial e limitações (dados ausentes,
  estimativas vs. censo, `warnings`).
