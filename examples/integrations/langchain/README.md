# Integração: LangChain + LangGraph (`langchain`)

## Objetivo

Mostrar como conectar o `mcp-ibge` a um agente
[LangGraph](https://langchain-ai.github.io/langgraph/) (ReAct) usando
[`langchain-mcp-adapters`](https://github.com/langchain-ai/langchain-mcp-adapters),
que converte automaticamente as tools MCP em `BaseTool`s do LangChain.

Por padrão, o LLM é um modelo **local via Ollama** (`langchain-ollama`) — não
é necessária nenhuma chave de API.

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

Troque a entrada `"ibge"` em `MCP_SERVERS` (em [`agent.py`](agent.py)) de:

```python
"ibge": {"command": "uvx", "args": ["mcp-ibge"], "transport": "stdio"}
```

para:

```python
"ibge": {
    "command": "uv",
    "args": ["--directory", "/caminho/absoluto/para/mcp-data-br", "run", "mcp-ibge"],
    "transport": "stdio",
}
```

### Usando a OpenAI em vez de Ollama (opcional)

Defina `OPENAI_API_KEY` no ambiente e troque, em [`agent.py`](agent.py):

```python
from langchain_ollama import ChatOllama
llm = ChatOllama(model=OLLAMA_MODEL, temperature=0)
```

por:

```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

(requer também `pip install langchain-openai`).

## Como executar

```bash
python agent.py "Compare a população estimada de Niterói e Maricá (RJ)."
```

Sem argumentos, o script usa o [prompt de teste](prompt.md) como padrão.

## Fluxo

1. `MultiServerMCPClient` abre uma sessão `stdio` com o `mcp-ibge` e, via
   `get_tools()`, converte cada tool MCP (incluindo seu JSON Schema de
   entrada) em uma `BaseTool` do LangChain.
2. `create_react_agent(llm, tools)` monta um agente ReAct (LangGraph) com
   essas tools.
3. O agente recebe a pergunta, decide quais tools chamar (possivelmente em
   várias rodadas), e produz a resposta final em `result["messages"][-1]`.

## Prompt de teste e resposta esperada

Veja [`prompt.md`](prompt.md) e [`example_output.md`](example_output.md).

## Limitações

- O resultado depende do modelo escolhido: modelos pequenos podem não chamar
  a tool corretamente ou podem somar/arredondar valores de forma incorreta —
  sempre confira `data` no envelope retornado pela tool, não apenas o texto
  final do agente.
- `comparar_municipios` aceita no máximo 10 municípios e hoje só implementa o
  indicador `"populacao_estimada"` — outros nomes de indicador aparecem em
  `data.indicadores_nao_implementados`, nunca como valores inventados.
