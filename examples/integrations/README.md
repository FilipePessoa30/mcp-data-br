# Integrations

Exemplos mínimos mostrando o `mcp-ibge` sendo usado por **agentes reais**
(LangChain, LlamaIndex, OpenAI Agents SDK) e por um script simples com
[Ollama](https://ollama.com), além dos clientes MCP nativos cobertos em
[`claude_desktop/`](../claude_desktop/), [`cursor/`](../cursor/) e
[`open_webui/`](../open_webui/).

| Pasta | Framework | LLM padrão | Caso de uso |
| --- | --- | --- | --- |
| [`local_ollama/`](local_ollama/) | SDK `mcp` (Python) + `ollama` | Ollama local | Consulta direta de tools de municípios |
| [`langchain/`](langchain/) | LangChain / LangGraph (`langchain-mcp-adapters`) | Ollama local | Agente ReAct comparando municípios |
| [`llamaindex/`](llamaindex/) | LlamaIndex (`llama-index-tools-mcp`) | Ollama local | `FunctionAgent` consultando dados oficiais |
| [`openai_agents/`](openai_agents/) | OpenAI Agents SDK (`openai-agents`) | Ollama local (endpoint OpenAI-compatible) | Script gerando um perfil municipal |

## Requisitos comuns

- **Sem chave de API obrigatória.** Todos os exemplos usam, por padrão, um
  modelo local via [Ollama](https://ollama.com) — instale o Ollama, baixe um
  modelo com suporte a *tool calling* (ex.: `ollama pull llama3.1`) e rode
  `ollama serve` (ou deixe o Ollama em segundo plano).
- **`uv` instalado.** Todos os exemplos conectam ao `mcp-ibge` via `uvx
  mcp-ibge` (stdio) — não é preciso instalar `mcp-ibge` manualmente. Para usar
  um checkout local deste repositório em vez do pacote publicado, veja a
  seção "Usando um checkout local do `mcp-data-br`" no `README.md` de cada
  exemplo.
- **Chaves externas são opcionais.** Cada `README.md` documenta como trocar
  o modelo local por OpenAI (ou outro provedor compatível), caso você prefira
  — basta definir `OPENAI_API_KEY` e ajustar algumas linhas em `agent.py`.

## Estrutura de cada exemplo

Cada pasta contém:

- `README.md` — objetivo, pré-requisitos, como executar e fluxo do agente.
- `requirements.txt` — dependências Python do exemplo.
- `agent.py` — script mínimo executável (`python agent.py "<pergunta>"`).
- `prompt.md` — prompt de teste e variações.
- `example_output.md` — chamada de tool esperada, envelope de resposta
  (`{ok, data, metadata, warnings, errors}`) e resposta final ilustrativa do
  agente.

## Objetivo

Demonstrar que o `mcp-data-br` não está restrito a clientes MCP "nativos"
(Claude Desktop, Cursor, Open WebUI) — qualquer agente capaz de falar o
protocolo MCP (ou de chamar tools no formato OpenAI-compatible) pode consultar
dados oficiais do IBGE através destes servidores, localmente e sem custo.
