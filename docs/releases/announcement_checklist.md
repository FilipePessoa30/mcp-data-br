# Checklist de divulgação — v0.1.0

Checklist para anunciar o release v0.1.0 do `mcp-ibge`. Mensagem central a
manter consistente em todos os canais:

> **mcp-ibge** é um servidor **MCP** (Model Context Protocol) que expõe dados
> públicos do **IBGE** (regiões, estados, municípios, distritos, agregados do
> SIDRA e indicadores de população) como *tools* tipadas e rastreáveis para
> Claude Desktop, Cursor e outros agentes de IA. v0.1.0 entrega um núcleo
> **estável de Localidades** (7 tools) com testes completos, CI e documentação;
> Agregados/SIDRA e o indicador de população vêm como **experimentais**.

Pré-requisito: o release v0.1.0 já foi publicado no GitHub (tag `v0.1.0`) e,
idealmente, no PyPI (ver
[checklist de publicação no PyPI](pypi_checklist.md)).

## 1. GitHub Release

- [ ] Criar a tag `v0.1.0` (se ainda não existir) e o **Release** no GitHub.
- [ ] Usar [docs/releases/v0.1.0.md](v0.1.0.md) como corpo do release (ajustar
      links relativos para absolutos, já que releases do GitHub não resolvem
      caminhos relativos do mesmo jeito que o README).
- [ ] Título sugerido: `v0.1.0 — Localidades estável + Agregados/SIDRA experimental`.
- [ ] Marcar como "Latest release".
- [ ] Conferir que o link do PyPI (se publicado) está mencionado no release.

## 2. README / repositório

- [ ] Badge de CI mostrando "passing" na branch `main`.
- [ ] Topics/tags do repositório no GitHub configurados (sugestões: `mcp`,
      `model-context-protocol`, `ibge`, `brazil`, `python`, `claude`,
      `claude-desktop`, `sidra`, `open-data`, `dados-abertos`).
- [ ] Descrição curta do repositório (campo "About") preenchida, ex.:
      "MCP server for Brazilian IBGE public data (locations, SIDRA aggregates,
      population) — typed tools for Claude Desktop, Cursor and other agents."
- [ ] Link do site/PyPI no campo "About", se aplicável.

## 3. LinkedIn

- [ ] Rascunho do post (PT-BR ou EN, conforme público-alvo):
  - Abertura: o problema (dados do IBGE são ricos mas fragmentados / difíceis
    de consumir por agentes de IA).
  - O que o `mcp-ibge` resolve: tools tipadas, com metadados de fonte, prontas
    para Claude Desktop/Cursor via MCP.
  - Destaques da v0.1.0: 7 tools de Localidades estáveis, testes completos,
    CI, segurança (allowlist de domínio, validação de entrada, limites de
    resposta).
  - Chamada para ação: link do repositório (e do PyPI, se publicado),
    convite para issues/contribuições.
  - 1-2 capturas de tela ou um GIF curto mostrando uma pergunta no Claude
    Desktop sendo respondida via `mcp-ibge` (opcional, mas aumenta engajamento).
- [ ] Hashtags sugeridas: `#MCP #ModelContextProtocol #IBGE #OpenData #Python
      #ClaudeAI #DadosAbertos #Brasil`.
- [ ] Revisar tom: técnico, mas acessível — evitar jargão excessivo de MCP
      para quem não conhece o protocolo (explicar em 1 frase o que é).

## 4. Reddit

Cada subreddit tem regras próprias sobre autopromoção — ler as regras da
comunidade antes de postar e, se exigido, marcar o post como "self-promotion"
ou postar em threads de "Showcase"/"What are you working on".

- [ ] **r/ClaudeAI** — foco em "novo MCP server para dados públicos
      brasileiros", com exemplo de prompt e resposta.
- [ ] **r/mcp** (se existir/ativo) — foco técnico: arquitetura, segurança
      (allowlist de domínio, validação), testes e CI.
- [ ] **r/Python** — foco no aspecto de engenharia: `pydantic`, `httpx`,
      `FastMCP`, testes com `respx`, `ruff`/`mypy`, `uv`. Verificar regras de
      autopromoção (muitos exigem proporção de posts não promocionais).
- [ ] **r/brasil** ou **r/devbr** — foco em dados públicos brasileiros e
      utilidade prática (ex.: "pergunte população de qualquer município pelo
      Claude").
- [ ] **r/LocalLLaMA** (opcional) — relevante se o post enfatizar uso local,
      sem API key, 100% via stdio.
- [ ] Para cada post: título claro, 2-3 frases de contexto, link do
      repositório, e disposição para responder perguntas nos comentários.

## 5. Pós-divulgação

- [ ] Acompanhar issues/comentários nas primeiras 48h e responder dúvidas
      sobre instalação/configuração.
- [ ] Anotar feedback recorrente (ex.: pedidos de novas tools, dúvidas sobre
      Agregados/SIDRA) para priorizar no roadmap (`v0.2.0` em diante).
- [ ] Se houver problemas de instalação relatados, considerar um patch
      `0.1.x` antes de seguir para `0.2.0`.
