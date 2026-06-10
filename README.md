# mcp-ibge

Servidor [MCP](https://modelcontextprotocol.io/) (Model Context Protocol) que
expõe dados públicos e oficiais do **IBGE** (Instituto Brasileiro de
Geografia e Estatística) como *tools* prontas para uso por LLMs e agentes:
localidades (regiões, estados, municípios e seus códigos), agregados
estatísticos do **SIDRA** e indicadores de **população**.

- ✅ 100% gratuito, **sem chave de API**.
- ✅ Dados oficiais via [servicodados.ibge.gov.br](https://servicodados.ibge.gov.br/api/docs).
- ✅ Toda resposta inclui metadados de **fonte e rastreabilidade**
  (`source_name`, `source_url`, `retrieved_at`, `endpoint`, `params`).
- ✅ Async (`httpx`), validação com `pydantic`, cache opcional em memória.
- ✅ Roda 100% local, via stdio — pronto para Claude Desktop, Cursor e outros
  clientes MCP.

## Sumário

- [Instalação](#instalação)
- [Executando o servidor](#executando-o-servidor)
- [Tools disponíveis](#tools-disponíveis)
- [Formato das respostas](#formato-das-respostas)
- [Configuração (variáveis de ambiente)](#configuração-variáveis-de-ambiente)
- [Integração com clientes MCP](#integração-com-clientes-mcp)
- [Desenvolvimento](#desenvolvimento)
- [Documentação adicional](#documentação-adicional)
- [Limitações e fontes de dados](#limitações-e-fontes-de-dados)
- [Licença](#licença)

## Instalação

Requer **Python 3.11+**. Recomenda-se [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/your-username/mcp-ibge.git
cd mcp-ibge

# Cria o ambiente virtual e instala o projeto + dependências de desenvolvimento
uv venv
uv pip install -e ".[dev]"
```

Alternativa com `pip`:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Executando o servidor

### Diretamente (stdio)

```bash
uv run mcp-ibge
# ou, equivalente:
uv run python -m mcp_ibge.server
```

Isso inicia o servidor MCP usando o transporte **stdio** (entrada/saída
padrão), o modo recomendado para integração com Claude Desktop, Cursor e
outros clientes MCP locais. Logs vão para **stderr** — stdout é reservado
exclusivamente para o protocolo MCP.

### Modo de desenvolvimento (MCP Inspector)

O pacote `mcp[cli]` traz o [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector),
útil para testar as tools interativamente:

```bash
uv run mcp dev src/mcp_ibge/server.py
```

### Transporte alternativo (preparado para o futuro)

O transporte padrão é `stdio`, mas o servidor já está preparado para rodar
com `streamable-http` (útil para expor o servidor via rede/Docker/Open
WebUI), bastando definir a variável de ambiente:

```bash
export MCP_IBGE_TRANSPORT=streamable-http
uv run mcp-ibge
```

## Tools disponíveis

### Localidades

| Tool | Descrição |
| --- | --- |
| `listar_regioes` | Lista as 5 grandes regiões do Brasil. |
| `listar_estados` | Lista os 26 estados + DF, ordenados por nome. |
| `obter_estado` | Detalhes de um estado por sigla (`SP`) ou código IBGE (`35`). |
| `listar_municipios` | Lista os municípios de uma UF, com UF e região resolvidas. |
| `buscar_municipio` | Busca fuzzy de municípios por nome (ignora acentos/maiúsculas); retorna `warnings` se ambíguo. |
| `obter_codigo_municipio` | Obtém o código IBGE (7 dígitos) de um município pelo nome e UF. |
| `obter_municipio_por_codigo` | Detalhes de um município pelo código IBGE, com UF e região. |
| `listar_distritos` | Lista os distritos de um município pelo código IBGE. |

### Agregados / SIDRA

| Tool | Descrição |
| --- | --- |
| `listar_agregados` | Lista tabelas/agregados do SIDRA, com filtros por pesquisa, assunto ou texto. |
| `obter_metadados_agregado` | Metadados de um agregado: variáveis, períodos e níveis territoriais disponíveis. |
| `consultar_dados_agregado` | Consulta valores de um agregado para variáveis, períodos e localidades específicas. |

### Indicadores

| Tool | Descrição |
| --- | --- |
| `obter_populacao_municipio` | População residente estimada mais recente de um município (agregado SIDRA 6579). |

Veja [docs/tools.md](docs/tools.md) para a descrição completa de argumentos
de cada tool e [examples/queries.md](examples/queries.md) para exemplos de
chamadas.

### Exemplos de uso

**1. Descobrir o código IBGE de um município**

```jsonc
// Chamada
obter_codigo_municipio(nome="Florianópolis", uf="SC")

// Resposta (resumida)
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/estados/SC/municipios",
    "retrieved_at": "2026-06-10T12:00:00Z",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/estados/SC/municipios",
    "params": {"nome": "Florianópolis", "uf": "SC", "limite": 5}
  },
  "data": 4205407
}
```

Se o nome buscado for ambíguo (ex.: `buscar_municipio(nome="São José")`, sem
`uf`), a resposta inclui um campo `warnings` com a lista de candidatos
encontrados, pedindo para refinar a busca.

**2. População estimada de um município**

```jsonc
// Chamada
obter_populacao_municipio(codigo_municipio="4205407")

// Resposta (resumida)
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324",
    "retrieved_at": "2026-06-10T12:00:01Z",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324",
    "params": {"codigo_municipio": "4205407", "localidades": "N6[4205407]"}
  },
  "data": [
    {
      "id": "9324",
      "variavel": "População residente estimada",
      "unidade": "Pessoas",
      "resultados": [
        {
          "series": [
            {
              "localidade": {"id": "4205407", "nome": "Florianópolis"},
              "serie": {"2024": "537062"}
            }
          ]
        }
      ]
    }
  ]
}
```

**3. Consultar um agregado do SIDRA para todos os estados**

```jsonc
consultar_dados_agregado(
  agregado_id=6579,
  variaveis="9324",
  periodos="-1",
  localidades="N3[all]"
)
```

## Formato das respostas

Toda tool retorna um objeto JSON com dois campos:

- **Sucesso**: `{"metadata": {...}, "data": ...}`
- **Erro**: `{"metadata": {...}, "error": "mensagem de erro"}`

O bloco `metadata` é sempre:

```json
{
  "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
  "source_url": "https://servicodados.ibge.gov.br/...",
  "retrieved_at": "2026-06-10T12:00:00Z",
  "endpoint": "https://servicodados.ibge.gov.br/...",
  "params": { "...": "parâmetros usados na consulta" }
}
```

Isso garante que qualquer dado retornado possa ser **rastreado até a fonte
oficial**, com data/hora da consulta e os parâmetros utilizados.

## Configuração (variáveis de ambiente)

Todas as configurações têm valores padrão e podem ser ajustadas via
variáveis de ambiente (prefixo `MCP_IBGE_`) ou um arquivo `.env` na raiz do
projeto — veja [.env.example](.env.example).

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `MCP_IBGE_API_BASE_URL` | `https://servicodados.ibge.gov.br/api` | URL base comum às APIs do IBGE; cada cliente acrescenta seu prefixo (`/v1/localidades`, `/v3/agregados`). |
| `MCP_IBGE_SOURCE_NAME` | `IBGE - Instituto Brasileiro de Geografia e Estatística` | Nome da fonte exibido em `metadata.source_name`. |
| `MCP_IBGE_USER_AGENT` | `mcp-ibge/0.1.0` | Header `User-Agent` usado nas requisições. |
| `MCP_IBGE_TIMEOUT` | `30.0` | Timeout (segundos) para cada requisição HTTP às APIs do IBGE. |
| `MCP_IBGE_CACHE_ENABLED` | `true` | Habilita/desabilita o cache em memória. |
| `MCP_IBGE_CACHE_TTL_SECONDS` | `3600.0` | Tempo de vida (segundos) das entradas em cache. |
| `MCP_IBGE_CACHE_MAX_SIZE` | `256` | Número máximo de respostas em cache simultaneamente. |
| `MCP_IBGE_LOG_LEVEL` | `INFO` | Nível de log (`DEBUG`, `INFO`, `WARNING`, ...). Logs sempre vão para stderr. |
| `MCP_IBGE_TRANSPORT` | `stdio` | Transporte MCP (`stdio` ou `streamable-http`). |

## Integração com clientes MCP

### Claude Desktop

Edite o arquivo `claude_desktop_config.json` (no Windows:
`%APPDATA%\Claude\claude_desktop_config.json`; no macOS:
`~/Library/Application Support/Claude/claude_desktop_config.json`) e
adicione o conteúdo de [examples/claude_desktop_config.json](examples/claude_desktop_config.json),
ajustando `--directory` para o caminho absoluto do projeto:

```json
{
  "mcpServers": {
    "ibge": {
      "command": "uv",
      "args": [
        "--directory",
        "/caminho/absoluto/para/mcp-ibge",
        "run",
        "python",
        "-m",
        "mcp_ibge.server"
      ]
    }
  }
}
```

Reinicie o Claude Desktop. As tools `listar_estados`, `obter_municipio_por_codigo`,
`consultar_dados_agregado` etc. ficarão disponíveis nas conversas.

### Cursor

Em `Settings -> MCP -> Add new MCP Server`, ou editando
`~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "ibge": {
      "command": "uv",
      "args": [
        "--directory",
        "/caminho/absoluto/para/mcp-ibge",
        "run",
        "mcp-ibge"
      ]
    }
  }
}
```

### Open WebUI / outros clientes baseados em HTTP

Para clientes que falam HTTP em vez de stdio (ex.: Open WebUI via
[`mcpo`](https://github.com/open-webui/mcpo)), inicie o servidor com o
transporte `streamable-http`:

```bash
MCP_IBGE_TRANSPORT=streamable-http uv run mcp-ibge
```

e aponte o cliente/proxy para o endpoint exposto pelo servidor.

## Desenvolvimento

```bash
# Lint e formatação
uv run ruff check .
uv run ruff format .

# Testes
uv run pytest
```

### Estrutura do projeto

```
mcp-ibge/
├── src/mcp_ibge/
│   ├── server.py        # Monta o FastMCP, registra as tools, entrypoint `main()`
│   ├── config.py          # Settings (pydantic-settings): URLs, timeouts, cache
│   ├── logging_config.py  # Logging para stderr (stdio-safe)
│   ├── clients/            # Camada HTTP "fina" (base, localidades, agregados)
│   ├── schemas/            # Modelos Pydantic e envelope de resposta
│   ├── services/           # Regras de negócio (filtros, aliases, indicadores)
│   ├── tools/              # Tools FastMCP (`@mcp.tool()`)
│   └── utils/              # cache, normalização de texto, exceções
├── tests/                  # Testes unitários (pytest + respx)
├── examples/               # Config de exemplo para clientes MCP e queries
└── docs/                   # Arquitetura, tools, fontes de dados, segurança
```

Veja [docs/architecture.md](docs/architecture.md) para uma descrição
detalhada de cada camada e do fluxo de uma chamada.

## Documentação adicional

- [docs/architecture.md](docs/architecture.md) — arquitetura em camadas e
  fluxo de uma chamada.
- [docs/tools.md](docs/tools.md) — referência completa de cada tool.
- [docs/data_sources.md](docs/data_sources.md) — APIs do IBGE utilizadas e
  formato do envelope de resposta.
- [docs/security.md](docs/security.md) — considerações de segurança.
- [examples/queries.md](examples/queries.md) — exemplos de chamadas às
  tools.

## Limitações e fontes de dados

- Todas as informações são obtidas em tempo real da
  [API de Serviços de Dados do IBGE](https://servicodados.ibge.gov.br/api/docs)
  (`servicodados.ibge.gov.br`), que é pública e não requer autenticação.
- O cache em memória é local ao processo e não persiste entre execuções —
  serve apenas para evitar chamadas repetidas durante uma mesma sessão.
- A tool `consultar_dados_agregado` espelha a sintaxe da API SIDRA
  (parâmetros `periodos` e `localidades`); use `obter_metadados_agregado`
  para descobrir os IDs válidos de variáveis, períodos e níveis territoriais
  de cada agregado.

## Licença

[MIT](LICENSE)
