# Arquitetura

O projeto é organizado em camadas, cada uma com uma responsabilidade única,
para manter baixo acoplamento e facilitar testes e evolução.

```
src/mcp_ibge/
├── server.py            # Monta o FastMCP, registra tools/resource/prompt e expõe `main()`
├── config.py            # Settings (pydantic-settings), lidas de env / .env
├── logging_config.py    # Configura logging para stderr (stdio-safe)
├── clients/             # Camada HTTP "fina": só chama a API e devolve dados brutos
│   ├── base.py           # AsyncIBGEClient: GET com timeout, cache e tratamento de erros
│   ├── localidades.py    # LocalidadesClient (regiões, estados, municípios)
│   └── agregados.py      # AgregadosClient (lista, metadados, dados do SIDRA)
├── schemas/              # Modelos Pydantic: validação e envelope de resposta
│   ├── common.py          # SourceMetadata, TypedToolResult, ToolResponse, ToolWarning/ToolError, build_metadata/build_tool_response
│   ├── localidades.py     # Region, State, Municipality, District + conversores *_from_raw
│   ├── agregados.py       # AgregadoSummary, AgregadoMetadata, AgregadoVariable, AgregadoPeriod, AgregadoQueryResult + conversores *_from_raw
│   ├── perfil.py          # PerfilMunicipal, MunicipioPerfil, IndicadorPerfil + extrair_microrregiao_ou_regiao_intermediaria
│   └── comparacao.py      # MunicipioConsulta, MunicipioComparado, MunicipioNaoResolvido, ComparacaoMunicipios
├── services/             # Regras de negócio: validação, filtros, aliases, indicadores
│   ├── localidades_service.py  # retorna TypedToolResult[T] (data/metadata/warnings/errors)
│   ├── agregados_service.py    # idem; constantes AGREGADO_POPULACAO_ESTIMADA / VARIAVEL_POPULACAO_ESTIMADA
│   ├── sidra_service.py        # SIDRA Query Builder: descoberta, sugestão, validação e execução
│   ├── perfil_service.py       # PerfilService: combina Localidades + população em um PerfilMunicipal
│   └── comparacao_service.py   # ComparacaoService: resolve e compara N municípios (MAX_MUNICIPIOS)
├── sidra/                # SIDRA Query Builder: parsing de metadados, validação local e sugestão
│   ├── metadata_parser.py # parse_agregado_metadata(): JSON de /metadados -> AgregadoMetadataParsed
│   ├── query_builder.py   # validar_consulta(): valida variaveis/localidades/periodos/classificacao
│   └── suggestions.py     # sugestão por palavras-chave (sem LLM): ranquear_agregados, sugerir_variavel/localidade
├── geo/                  # Módulo geoespacial: malhas (GeoJSON) e bounding boxes
│   ├── client.py           # MalhasClient: GET /v3/malhas/{municipios,estados}/{id} em GeoJSON
│   ├── service.py           # GeoService: is_valid_geojson, calcular_bbox, MAX_MUNICIPIOS_GEOJSON
│   └── schemas.py           # QUALIDADE_*, GEOJSON_TYPES, BBox, GeoJSONMunicipios, MunicipioGeoNaoResolvido
├── tools/                # Camada MCP: expõe funções como `@mcp.tool()`
│   ├── __init__.py        # `run_typed_tool()` (TypedToolResult) -> envelope padrão
│   ├── localidades_tools.py  # register_localidades_tools(mcp)
│   ├── agregados_tools.py    # register_agregados_tools(mcp)
│   ├── sidra_tools.py        # register_sidra_tools(mcp): 7 tools do SIDRA Query Builder
│   ├── perfil_tools.py       # register_perfil_tools(mcp): gerar_perfil_municipal
│   ├── comparacao_tools.py   # register_comparacao_tools(mcp): comparar_municipios
│   └── geo_tools.py          # register_geo_tools(mcp): malhas e bounding boxes (GeoJSON)
└── utils/
    ├── normalization.py   # normalize_text(): busca textual sem acento/caixa
    ├── cache.py            # TTLCache + singleton get_cache()/clear_cache()
    ├── validators.py       # validação de formato (UF, agregado, variável, período, nível, limite)
    └── errors.py           # IBGEClientError e subclasses (NotFound, Validation, RateLimit, Server)
```

## SIDRA Query Builder

`sidra_service.SidraService` não duplica acesso HTTP: reutiliza
`AgregadosClient`/`AgregadosService` para `listar_agregados` e
`obter_metadados_agregado`, e usa `sidra/metadata_parser.py` para converter o
JSON de `/agregados/{id}/metadados` em `AgregadoMetadataParsed` (periodicidade,
níveis territoriais, variáveis, classificações, limitações em texto).

- `sidra/query_builder.validar_consulta()` é **puramente local**: não faz
  requisições, apenas confere `variaveis`/`localidades`/`periodos`/
  `classificacao` (já validados em *formato* por `utils/validators.py`)
  contra `AgregadoMetadataParsed`.
- `sidra/suggestions.py` implementa `sugerir_consulta_sidra` **sem nenhum
  modelo de linguagem**: extração de palavras-chave (remoção de
  acentos/caixa/stopwords), pontuação por substring nos nomes de
  agregados/variáveis já obtidos da API, e um dicionário fixo de
  palavras-chave → nível territorial.
- `executar_consulta_sidra_validada` chama `validar_consulta_sidra`
  internamente e só delega a `AgregadosService.consultar_agregado` se
  `data.valido=True` — nenhuma requisição de dados é feita para uma consulta
  inválida.

## Perfil Municipal

`perfil_service.PerfilService` não duplica acesso HTTP: reutiliza
`LocalidadesService` (resolução de nome/UF para código IBGE, identificação,
UF e região) e `AgregadosService.consultar_populacao_municipio` (indicador de
população). `schemas/perfil.py` define `PerfilMunicipal` e
`extrair_microrregiao_ou_regiao_intermediaria()`, que lê o JSON bruto
(`Municipality.raw`) e localiza `microrregiao` ou
`regiao-imediata.regiao-intermediaria`, dependendo da estrutura retornada
pela API.

- Ambiguidade ou município não encontrado em `obter_codigo_municipio` é
  propagado diretamente (`ok=False`, mesmos `warnings`/`errors`) — nenhuma
  outra requisição é feita.
- Apenas indicadores efetivamente obtidos entram em `data.indicadores`; se a
  consulta de população falhar ou retornar dado ausente/sigiloso, isso vira
  um `warning` e o indicador simplesmente não aparece — nunca um valor
  inventado.
- `data.proximos_indicadores_sugeridos` é uma lista fixa de nomes de
  indicadores ainda não implementados (ex.: PIB, IDH, área territorial) —
  apenas sugestões, nunca dados.

## Comparação de Municípios

`comparacao_service.ComparacaoService` reutiliza os mesmos serviços do
Perfil Municipal (`LocalidadesService` e
`AgregadosService.consultar_populacao_municipio`) para resolver e comparar
até `MAX_MUNICIPIOS` municípios em uma única chamada.

- Cada município (`nome` + `uf`) é resolvido independentemente: um município
  não encontrado ou ambíguo entra em `municipios_nao_resolvidos` (com o
  `motivo`) e **não** interrompe a resolução dos demais.
- `indicadores` é mapeado para os indicadores suportados via
  `_normalizar_chave_indicador()` (reusa `utils/normalization.normalize_text`).
  Indicadores não reconhecidos (ex.: `"pib"`) entram em
  `indicadores_nao_implementados` — apenas o nome, nunca dados — com um
  `warning`, sem interromper a comparação dos demais indicadores.
- Por ora, apenas `"populacao_estimada"` é suportado; indicadores cujo valor
  não pôde ser obtido (falha do SIDRA ou dado ausente/sigiloso) geram um
  `warning` e simplesmente não aparecem em `indicadores` para aquele
  município — nunca um valor inventado.
- `fontes` acumula, sem duplicar, todos os endpoints da API do IBGE usados na
  comparação (um `/localidades/estados/{uf}/municipios` e um
  `/localidades/municipios/{id}` por município, mais um
  `/agregados/6579/.../variaveis/9324` por município/indicador).
- `limitacoes` combina avisos fixos (alcance dos indicadores, risco do
  agregado SIDRA 6579 após um novo Censo) com um aviso condicional sobre
  variação de período entre municípios quando `ano` não é informado.
- Se `municipios` vier vazio, exceder `MAX_MUNICIPIOS`, ou nenhum município
  puder ser resolvido, a resposta tem `ok=False` (sem fazer requisições
  desnecessárias nos dois primeiros casos).

## Malhas Geográficas (Geo)

`geo/` é um módulo independente — cliente, serviço e schemas próprios, fora
de `clients/`/`services/`/`schemas/` — que consulta a
[API de Malhas do IBGE](https://servicodados.ibge.gov.br/api/docs/malhas) e
devolve GeoJSON (RFC 7946) praticamente como recebido da API, exceto para o
bounding box (calculado localmente). Apenas `geo_tools.py` fica em `tools/`,
seguindo a mesma convenção das demais tools.

- `geo/client.py` define `MalhasClient` (subclasse de `AsyncIBGEClient`, path
  base `/v3/malhas`), com `get_malha_municipio(codigo_ibge, qualidade)` e
  `get_malha_uf(uf, qualidade)` — cada um pede explicitamente
  `formato=application/vnd.geo+json` e valida `codigo_ibge`/`uf` via
  `utils/validators` antes da requisição.
- `geo/schemas.py` define `QUALIDADE_SIMPLIFICADA = "minima"` e
  `QUALIDADE_COMPLETA = "maxima"` (os dois valores aceitos pelo parâmetro
  `qualidade` da API), `GEOJSON_TYPES` (tipos GeoJSON válidos por RFC 7946,
  usados por `service.is_valid_geojson`), `BBox` e `GeoJSONMunicipios` (com
  `codigos_nao_resolvidos` como "foreign member" do GeoJSON).
- `geo/service.py` (`GeoService`) implementa as 4 tools:
  - `obter_malha_municipio`/`obter_malha_uf` repassam o GeoJSON da API sem
    alterações, com `metadata.territorial_level` `"N6"`/`"N3"`.
  - `obter_bbox_municipio` reusa `get_malha_municipio` (sempre qualidade
    `"minima"`) e calcula o bounding box localmente (`calcular_bbox`),
    achatando recursivamente as `coordinates` da geometria.
  - `gerar_geojson_municipios` busca a malha simplificada de até
    `MAX_MUNICIPIOS_GEOJSON = 10` municípios e monta uma `FeatureCollection`
    com uma `Feature` por município; códigos sem malha válida vão para
    `codigos_nao_resolvidos` (com `motivo`), sem interromper os demais.
- Por padrão (`simplificado=True`), todas as tools usam qualidade `"minima"`
  e a resposta inclui um aviso fixo informando que a geometria foi
  simplificada. `simplificado=False` (apenas em
  `obter_malha_municipio`/`obter_malha_uf`) usa qualidade `"maxima"`, sem o
  aviso, mas o tamanho pode ultrapassar `Settings.max_response_size_bytes`
  para UFs/municípios grandes — nesse caso `AsyncIBGEClient` converte a
  resposta em `IBGEServerError` antes de retornar ao cliente MCP.

## Fluxo de uma chamada

1. Um cliente MCP chama uma tool (ex.: `consultar_populacao_municipio`).
2. A tool (em `tools/`) delega para o `service` correspondente e envolve o
   resultado com `run_typed_tool()`, que monta o envelope padrão
   `{"ok": ..., "data": ..., "metadata": ..., "warnings": [...], "errors": [...]}`,
   igual em sucesso ou erro.
3. O `service` aplica regras de negócio (filtros, validação com Pydantic,
   resolução de aliases, conversão `*_from_raw`) e delega ao `client`.
   `localidades_service` e `agregados_service` retornam
   `TypedToolResult[T]` (`ok`, `data`, `metadata`, `warnings`, `errors`),
   convertido pelo `run_typed_tool()`.
4. O `client` (em `clients/`) monta a URL e os parâmetros, consulta o cache
   (`utils/cache.py`) e, em caso de *miss*, faz a requisição HTTP via
   `AsyncIBGEClient.get_json`.
5. Erros de rede/HTTP são convertidos em subclasses de `IBGEClientError`
   (`IBGENotFoundError`, `IBGEValidationError`, `IBGERateLimitError`,
   `IBGEServerError`) por `AsyncIBGEClient`. Em ambos os services, são
   capturados e convertidos em `TypedToolResult(ok=False, errors=[...])`,
   que `run_typed_tool()` transforma no envelope de erro — sem derrubar o
   servidor.

## Por que essa separação

- **clients/**: isolam detalhes da API do IBGE (URLs, formatos de query).
  Podem ser testados com `respx` sem nenhuma lógica adicional.
- **services/**: contêm a lógica que realmente importa para o usuário
  (filtrar por região, buscar por nome ignorando acentos, calcular
  população) — testáveis sem depender do protocolo MCP.
- **tools/**: a única camada que conhece o FastMCP e o formato de envelope.
  Mantém a "borda" do servidor fina e uniforme.
- **schemas/**: garantem que os dados externos tenham o formato esperado
  (`extra="allow"` permite campos adicionais da API sem quebrar o parsing) e
  centralizam o formato do envelope de resposta.

## Trabalho futuro

- **API de Projeções da População** (`servicodados.ibge.gov.br/api/v1/projecoes`):
  base URL distinta da usada pelos agregados/SIDRA; pode ser adicionada como
  um novo client (`clients/projecoes.py`) + service/tool dedicados, seguindo
  o mesmo padrão.
- **Transporte `streamable-http`**: `config.py` já expõe `transport`, e
  `server.py` repassa o valor para `mcp.run(transport=...)` — falta apenas
  documentar/testar o deploy via HTTP (ex.: atrás do `mcpo` para Open WebUI).
- **Cache persistente**: `utils/cache.py` é um TTL cache em memória; pode ser
  trocado por um backend externo (ex.: SQLite, Redis) sem alterar `clients/`.
