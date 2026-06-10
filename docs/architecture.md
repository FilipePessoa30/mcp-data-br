# Arquitetura

O projeto é organizado em camadas, cada uma com uma responsabilidade única,
para manter baixo acoplamento e facilitar testes e evolução.

```
src/mcp_ibge/
├── server.py            # Monta o FastMCP, registra as tools e expõe `main()`
├── config.py            # Settings (pydantic-settings), lidas de env / .env
├── logging_config.py    # Configura logging para stderr (stdio-safe)
├── clients/             # Camada HTTP "fina": só chama a API e devolve dados brutos
│   ├── base.py           # AsyncIBGEClient: GET com timeout, cache e tratamento de erros
│   ├── localidades.py    # LocalidadesClient (regiões, estados, municípios)
│   └── agregados.py      # AgregadosClient (lista, metadados, dados do SIDRA)
├── schemas/              # Modelos Pydantic: validação e envelope de resposta
│   ├── common.py          # SourceMetadata, TypedToolResult, ToolResponse/ToolErrorResponse, build_response
│   ├── localidades.py     # Region, State, Municipality, District + conversores *_from_raw
│   └── agregados.py       # AgregadoResumo, PesquisaAgregados, Variavel, MetadadosAgregado
├── services/             # Regras de negócio: validação, filtros, aliases, indicadores
│   ├── localidades_service.py  # retorna TypedToolResult[T] (data/metadata/warnings/errors)
│   └── agregados_service.py
├── tools/                # Camada MCP: expõe funções como `@mcp.tool()`
│   ├── __init__.py        # `run_tool()` (IBGEResult) e `run_typed_tool()` (TypedToolResult) -> envelope padrão
│   ├── localidades_tools.py
│   └── agregados_tools.py
└── utils/
    ├── normalization.py   # normalize_text(): busca textual sem acento/caixa
    ├── cache.py            # TTLCache + singleton get_cache()/clear_cache()
    └── errors.py           # IBGEClientError e subclasses (NotFound, Validation, RateLimit, Server)
```

## Fluxo de uma chamada

1. Um cliente MCP chama uma tool (ex.: `obter_populacao_municipio`).
2. A tool (em `tools/`) delega para o `service` correspondente e envolve o
   resultado com `run_tool()` ou `run_typed_tool()`, que montam o envelope
   `{"metadata": ..., "data" ou "error": ...}` (opcionalmente com `"warnings"`).
3. O `service` aplica regras de negócio (filtros, validação com Pydantic,
   resolução de aliases) e delega ao `client`. As tools de Localidades
   retornam `TypedToolResult[T]` (`ok`, `data`, `metadata`, `warnings`,
   `errors`), convertido pelo `run_typed_tool()`.
4. O `client` (em `clients/`) monta a URL e os parâmetros, consulta o cache
   (`utils/cache.py`) e, em caso de *miss*, faz a requisição HTTP via
   `AsyncIBGEClient.get_json`.
5. Erros de rede/HTTP são convertidos em subclasses de `IBGEClientError`
   (`IBGENotFoundError`, `IBGEValidationError`, `IBGERateLimitError`,
   `IBGEServerError`) por `AsyncIBGEClient`. Em `agregados_service`, são
   tratados por `run_tool()`; em `localidades_service`, são capturados e
   convertidos em `TypedToolResult(ok=False, errors=[...])`, que
   `run_typed_tool()` transforma no envelope de erro — sem derrubar o
   servidor em ambos os casos.

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
