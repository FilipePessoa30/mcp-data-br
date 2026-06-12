# Integração: agente local com Ollama (`local_ollama`)

## Objetivo

Mostrar o caso de uso **mais simples e 100% local**: um agente que roda
inteiramente na sua máquina, usando um LLM local via [Ollama](https://ollama.com)
com *tool calling* nativo e o servidor `mcp-ibge` conectado por `stdio`.

Não é necessário nenhuma chave de API — nem da OpenAI, nem do IBGE (a API do
IBGE é pública e não exige autenticação).

## Pré-requisitos

1. [Ollama](https://ollama.com) instalado e em execução (`ollama serve`, ou já
   roda em segundo plano após a instalação).
2. Um modelo com suporte a *tool calling* baixado, por exemplo:

   ```bash
   ollama pull llama3.1
   ```

   Outros modelos com tool calling funcionam também (`qwen2.5`,
   `mistral-nemo`, etc.) — ajuste `OLLAMA_MODEL` em [`agent.py`](agent.py).
3. [`uv`](https://docs.astral.sh/uv/) instalado, para que `uvx mcp-ibge`
   funcione (o script chama `uvx` automaticamente — não é preciso instalar
   `mcp-ibge` manualmente).
4. Python 3.10+ com as dependências de [`requirements.txt`](requirements.txt):

   ```bash
   pip install -r requirements.txt
   ```

### Usando um checkout local do `mcp-data-br`

Se você está desenvolvendo neste repositório (em vez de usar o pacote
publicado), troque a configuração do servidor em [`agent.py`](agent.py) de:

```python
SERVER = StdioServerParameters(command="uvx", args=["mcp-ibge"])
```

para:

```python
SERVER = StdioServerParameters(
    command="uv",
    args=["--directory", "/caminho/absoluto/para/mcp-data-br", "run", "mcp-ibge"],
)
```

## Como executar

```bash
python agent.py "Qual é o código IBGE do município de Niterói, no Rio de Janeiro?"
```

Sem argumentos, o script usa o [prompt de teste](prompt.md) como padrão.

## Fluxo

1. O script abre uma sessão MCP `stdio` com o `mcp-ibge` e lista as tools
   disponíveis (`list_tools`).
2. Cada tool é convertida para o formato de função aceito pelo cliente
   `ollama` (`{"type": "function", "function": {...}}`).
3. O modelo local recebe a pergunta + a lista de tools e decide se chama
   alguma (`tool_calls`).
4. Se chamar, o script executa a tool via `session.call_tool(...)` e devolve
   o resultado (o envelope JSON `{ok, data, metadata, warnings, errors}`) ao
   modelo como mensagem `role="tool"`.
5. O modelo gera a resposta final em linguagem natural.

## Prompt de teste e resposta esperada

Veja [`prompt.md`](prompt.md) e [`example_output.md`](example_output.md).

## Limitações

- A qualidade da resposta depende do modelo local escolhido — nem todos os
  modelos suportam *tool calling* de forma confiável. `llama3.1` e `qwen2.5`
  são bons pontos de partida.
- Este exemplo faz apenas **uma rodada** de chamadas de tool (sem loop de
  múltiplas chamadas encadeadas). Para fluxos mais complexos, veja os
  exemplos [`langchain/`](../langchain/) e [`llamaindex/`](../llamaindex/),
  que usam um agente ReAct com loop completo.
