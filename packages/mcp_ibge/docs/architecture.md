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
│   └── agregados.py       # AgregadoSummary, AgregadoMetadata, AgregadoVariable, AgregadoPeriod, AgregadoQueryResult + conversores *_from_raw
├── services/             # Regras de negócio: validação, filtros, aliases, indicadores
│   ├── localidades_service.py  # retorna TypedToolResult[T] (data/metadata/warnings/errors)
│   ├── agregados_service.py    # idem; constantes AGREGADO_POPULACAO_ESTIMADA / VARIAVEL_POPULACAO_ESTIMADA
│   └── sidra_service.py        # SIDRA Query Builder: descoberta, sugestão, validação e execução
├── sidra/                # SIDRA Query Builder: parsing de metadados, validação local e sugestão
│   ├── metadata_parser.py # parse_agregado_metadata(): JSON de /metadados -> AgregadoMetadataParsed
│   ├── query_builder.py   # validar_consulta(): valida variaveis/localidades/periodos/classificacao
│   └── suggestions.py     # sugestão por palavras-chave (sem LLM): ranquear_agregados, sugerir_variavel/localidade
├── tools/                # Camada MCP: expõe funções como `@mcp.tool()`
│   ├── __init__.py        # `run_typed_tool()` (TypedToolResult) -> envelope padrão
│   ├── localidades_tools.py  # register_localidades_tools(mcp)
│   ├── agregados_tools.py    # register_agregados_tools(mcp)
│   └── sidra_tools.py        # register_sidra_tools(mcp): 7 tools do SIDRA Query Builder
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
