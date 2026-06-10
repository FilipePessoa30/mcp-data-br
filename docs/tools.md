# Tools disponíveis

Todas as tools retornam um envelope JSON com `metadata` e (`data` ou
`error`) — veja [data_sources.md](data_sources.md) para o formato completo.

## Localidades

### `listar_regioes`

Lista as 5 grandes regiões geográficas do Brasil (Norte, Nordeste, Sudeste,
Sul, Centro-Oeste).

- **Argumentos**: nenhum.
- **Endpoint**: `GET /localidades/regioes`.

### `listar_estados`

Lista os 26 estados e o Distrito Federal.

- **Argumentos**:
  - `regiao` (opcional): sigla (`"N"`, `"NE"`, `"CO"`, `"SE"`, `"S"`) ou ID
    numérico da região. Filtra os estados pertencentes a ela.
- **Endpoint**: `GET /localidades/estados`.

### `obter_estado`

Detalhes de um estado (UF).

- **Argumentos**:
  - `uf` (obrigatório): sigla (ex.: `"SP"`) ou ID IBGE (ex.: `"35"`).
- **Endpoint**: `GET /localidades/estados/{uf}`.

### `listar_municipios`

Lista municípios brasileiros.

- **Argumentos**:
  - `uf` (opcional): sigla ou ID do estado. Sem ele, retorna todos os ~5570
    municípios do Brasil.
- **Endpoint**: `GET /localidades/estados/{uf}/municipios` ou
  `GET /localidades/municipios`.

### `obter_municipio`

Detalhes completos de um município pelo código IBGE.

- **Argumentos**:
  - `codigo` (obrigatório): código IBGE com 7 dígitos (ex.: `"3550308"`).
- **Endpoint**: `GET /localidades/municipios/{codigo}`.

### `buscar_municipios_por_nome`

Busca municípios cujo nome contenha o termo informado, ignorando acentos e
maiúsculas/minúsculas. Útil para descobrir o código IBGE a partir do nome.

- **Argumentos**:
  - `nome` (obrigatório): termo de busca (ex.: `"sao jose"`).
  - `uf` (opcional): restringe a busca a uma UF.
  - `limit` (opcional, padrão `20`, entre 1 e 200): número máximo de
    resultados.
- **Endpoint**: mesmo de `listar_municipios`, com filtro aplicado localmente.

### `obter_distritos_municipio`

Lista os distritos de um município.

- **Argumentos**:
  - `codigo` (obrigatório): código IBGE do município com 7 dígitos (ex.:
    `"3550308"`).
- **Endpoint**: `GET /localidades/municipios/{codigo}/distritos`.

## Agregados / SIDRA

### `listar_agregados`

Lista os agregados (tabelas estatísticas) disponíveis no SIDRA. Use para
descobrir o ID de um agregado antes de chamar `obter_metadados_agregado` ou
`consultar_dados_agregado`.

- **Argumentos**:
  - `pesquisa` (opcional): nome/sigla da pesquisa de origem (ex.: `"Censo
    Demográfico"`).
  - `assunto` (opcional): nome do assunto (ex.: `"População"`).
  - `texto` (opcional): filtro textual adicional aplicado ao nome dos
    agregados (substring, sem distinção de caixa).
- **Endpoint**: `GET /agregados`.

### `obter_metadados_agregado`

Metadados de um agregado: variáveis, períodos e níveis territoriais
disponíveis. Use o resultado para escolher os parâmetros de
`consultar_dados_agregado`.

- **Argumentos**:
  - `agregado_id` (obrigatório): ID numérico do agregado (ex.: `6579`).
- **Endpoint**: `GET /agregados/{agregado_id}/metadados`.

### `consultar_dados_agregado`

Consulta valores de um agregado do SIDRA para variáveis, períodos e
localidades específicas.

- **Argumentos**:
  - `agregado_id` (obrigatório): ID numérico do agregado.
  - `variaveis` (opcional, padrão `"all"`): ID de variável, lista separada
    por vírgula, ou `"all"`.
  - `periodos` (opcional, padrão `"-1"`): um ano (`"2021"`), intervalo
    (`"2010-2020"`), lista (`"2019,2021"`) ou relativo (`"-1"` = último
    período disponível).
  - `localidades` (opcional, padrão `"N1[all]"`): unidade territorial no
    formato `N<nivel>[<ids>]`, ex.: `"N1[all]"` (Brasil), `"N3[all]"` (todos
    os estados), `"N6[3550308]"` (município de São Paulo). `"BR"` é aceito
    como atalho para `"N1[all]"`.
  - `classificacoes` (opcional): filtro de classificação, formato
    `"<id_classificacao>[<id_categoria>]"`.
- **Endpoint**: `GET /agregados/{agregado_id}/periodos/{periodos}/variaveis/{variaveis}`.

> Para descobrir IDs válidos de variáveis, períodos e níveis territoriais,
> chame `obter_metadados_agregado` antes.

## Indicadores

### `obter_populacao_municipio`

População residente estimada mais recente de um município, baseada no
agregado SIDRA 6579 ("Estimativas de população"), variável 9324.

- **Argumentos**:
  - `codigo_municipio` (obrigatório): código IBGE com 7 dígitos (ex.:
    `"3550308"` = São Paulo/SP).
- **Endpoint**: `GET /agregados/6579/periodos/-1/variaveis/9324`.
