# Integração: LlamaIndex (`llamaindex`)

## Objetivo

Mostrar um `FunctionAgent` do [LlamaIndex](https://docs.llamaindex.ai/)
consultando dados oficiais do IBGE através do `mcp-ibge`, usando
[`llama-index-tools-mcp`](https://pypi.org/project/llama-index-tools-mcp/)
para converter as tools MCP em `FunctionTool`s.

Por padrão, o LLM é um modelo **local via Ollama**
(`llama-index-llms-ollama`) — não é necessária nenhuma chave de API.

## Pré-requisitos

1. [Ollama](https://ollama.com) instalado e em execução, com um modelo com
   suporte a tool calling:

   ```bash
   ollama pull llama3.1
   ```

2. [`uv`](https://docs.astral.sh/uv/) instalado (para `uvx mcp-ibge`).
3. Dependências Python:

   ```bash
   pip install -r requirements.txt
   ```

### Usando um checkout local do `mcp-data-br`

Troque a criação do `BasicMCPClient` em [`agent.py`](agent.py) de:

```python
mcp_client = BasicMCPClient("uvx", args=["mcp-ibge"])
```

para:

```python
mcp_client = BasicMCPClient(
    "uv",
    args=["--directory", "/caminho/absoluto/para/mcp-data-br", "run", "mcp-ibge"],
)
```

### Usando a OpenAI em vez de Ollama (opcional)

Defina `OPENAI_API_KEY` no ambiente e troque, em [`agent.py`](agent.py):

```python
from llama_index.llms.ollama import Ollama
llm = Ollama(model=OLLAMA_MODEL, request_timeout=120.0)
```

por:

```python
from llama_index.llms.openai import OpenAI
llm = OpenAI(model="gpt-4o-mini")
```

(requer também `pip install llama-index-llms-openai`).

## Como executar

```bash
python agent.py "Quais são as grandes regiões do Brasil segundo o IBGE?"
```

Sem argumentos, o script usa o [prompt de teste](prompt.md) como padrão.

## Fluxo

1. `BasicMCPClient` abre uma sessão `stdio` com o `mcp-ibge`.
2. `McpToolSpec(client=mcp_client).to_tool_list_async()` converte cada tool
   MCP em uma `FunctionTool` do LlamaIndex (preservando nome, descrição e
   schema de parâmetros).
3. Um `FunctionAgent` (workflow de agente do LlamaIndex) recebe essas tools
   e o LLM local, e responde à pergunta chamando as tools necessárias.

## Prompt de teste e resposta esperada

Veja [`prompt.md`](prompt.md) e [`example_output.md`](example_output.md).

## Limitações

- O resultado depende do modelo escolhido — modelos pequenos podem não
  invocar a tool corretamente. Sempre confira `data` no envelope retornado
  pela tool, não apenas o texto final do agente.
- Este exemplo usa `listar_regioes`, que não depende de SIDRA/Agregados e
  responde rapidamente mesmo com modelos locais pequenos.
