# Integração: OpenAI Agents SDK (`openai_agents`)

## Objetivo

Script simples usando o [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
(`openai-agents`) que conecta o `mcp-ibge` via `MCPServerStdio` e gera um
**perfil municipal** com `gerar_perfil_municipal`.

Apesar do nome "OpenAI Agents SDK", **por padrão este exemplo não usa a
OpenAI** nem exige `OPENAI_API_KEY`: o SDK é apontado para um endpoint local
compatível com a API da OpenAI, servido pelo [Ollama](https://ollama.com)
(`http://localhost:11434/v1`), usando uma chave fictícia.

## Pré-requisitos

1. [Ollama](https://ollama.com) instalado e em execução, com um modelo com
   suporte a tool calling:

   ```bash
   ollama pull llama3.1
   ```

   O Ollama expõe automaticamente um endpoint compatível com a API da OpenAI
   em `http://localhost:11434/v1` — nenhuma configuração extra é necessária.

2. [`uv`](https://docs.astral.sh/uv/) instalado (para `uvx mcp-ibge`).
3. Dependências Python:

   ```bash
   pip install -r requirements.txt
   ```

### Usando um checkout local do `mcp-data-br`

Troque os `params` do `MCPServerStdio` em [`agent.py`](agent.py) de:

```python
params={"command": "uvx", "args": ["mcp-ibge"]}
```

para:

```python
params={
    "command": "uv",
    "args": ["--directory", "/caminho/absoluto/para/mcp-data-br", "run", "mcp-ibge"],
}
```

### Usando a OpenAI de fato (opcional)

Defina `OPENAI_API_KEY` no ambiente e remova a configuração customizada de
`model`/`client` em [`agent.py`](agent.py), deixando o `Agent` usar o modelo
padrão do SDK (ex.: `Agent(name=..., instructions=..., mcp_servers=[...])`,
sem `model=`). Você também pode reativar o tracing padrão do SDK removendo a
chamada a `set_tracing_disabled(True)`.

## Como executar

```bash
python agent.py "Gere um perfil básico do município de Maricá, RJ."
```

Sem argumentos, o script usa o [prompt de teste](prompt.md) como padrão.

## Fluxo

1. `MCPServerStdio` abre uma sessão `stdio` com o `mcp-ibge` (via `uvx`).
2. Um `AsyncOpenAI` client é configurado para falar com o endpoint
   OpenAI-compatible do Ollama (`base_url="http://localhost:11434/v1"`,
   `api_key="ollama"` — qualquer string serve, o Ollama não valida).
3. `set_tracing_disabled(True)` evita que o SDK tente enviar traços para a
   plataforma da OpenAI (o que exigiria `OPENAI_API_KEY`).
4. `Agent(..., model=..., mcp_servers=[ibge_server])` + `Runner.run(...)`
   executam o agente, que chama `gerar_perfil_municipal` conforme
   necessário e retorna `result.final_output`.

## Prompt de teste e resposta esperada

Veja [`prompt.md`](prompt.md) e [`example_output.md`](example_output.md).

## Limitações

- `gerar_perfil_municipal` hoje cobre apenas identificação básica do
  município e o indicador de população estimada (`data.limitacoes` no
  envelope detalha o que falta — PIB, IDH, área territorial etc.).
- Como nenhum `ano` é informado, o indicador de população retorna o período
  mais recente disponível no SIDRA (pode variar com o tempo).
- A qualidade da resposta final depende do modelo local escolhido — modelos
  pequenos podem omitir parte das informações do perfil. Sempre confira
  `data` no envelope retornado pela tool.
