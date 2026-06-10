# Checklist de publicação no PyPI — v0.1.0

Checklist para publicar `mcp-ibge` 0.1.0 no PyPI. Marque cada item antes de
seguir para o próximo.

## 1. Pré-requisitos do código

- [ ] `uv run pytest -q` — todos os testes passam.
- [ ] `uv run ruff check .` — sem erros de lint.
- [ ] `uv run ruff format --check .` — sem diferenças de formatação.
- [ ] `uv run mypy` — sem erros de tipo (passo opcional na CI, mas vale
      conferir antes do release).
- [ ] CI (`.github/workflows/ci.yml`) verde na branch `main`.
- [ ] Versão em `pyproject.toml` (`[project] version`) é `0.1.0`.
- [ ] `CHANGELOG.md` tem uma seção `[0.1.0]` com a data de release correta.
- [ ] `README.md` sem placeholders (`your-username` etc.) e com os links do
      repositório corretos (`https://github.com/FilipePessoa30/mcp-ibge`).
- [ ] `LICENSE` (MIT) presente na raiz e referenciado em `pyproject.toml`
      (`license = { text = "MIT" }`).
- [ ] `pyproject.toml` → `[project.urls]` aponta para o repositório real
      (Homepage, Issues).

## 2. Metadados do pacote

- [ ] `name = "mcp-ibge"` — confirmar que o nome está disponível no PyPI
      (acessar `https://pypi.org/project/mcp-ibge/` e confirmar 404/"not
      found"). Se já estiver em uso, decidir um nome alternativo **antes**
      de publicar (mudança de nome depois é dolorosa).
- [ ] `description`, `keywords`, `classifiers` revisados e coerentes com o
      escopo da v0.1.0 (foco em Localidades; Agregados/SIDRA experimental).
- [ ] `requires-python = ">=3.11"` confere com a matriz testada na CI.
- [ ] `dependencies` mínimas e corretas (`mcp[cli]`, `httpx`, `pydantic`,
      `pydantic-settings`); `dev` extras não vazam para a instalação padrão.
- [ ] `[project.scripts] mcp-ibge = "mcp_ibge.server:main"` — confirma que o
      entrypoint existe e funciona (`uv run mcp-ibge` inicia o servidor).

## 3. Build local

```bash
# Limpar builds antigos, se houver
rm -rf dist/

# Gerar sdist + wheel
uv build
```

- [ ] `dist/` contém um `.tar.gz` (sdist) e um `.whl` (wheel).
- [ ] Conferir o conteúdo do sdist/wheel (sem arquivos indesejados, ex.:
      `.env`, caches, `tests/__pycache__`):
  ```bash
  tar -tzf dist/mcp_ibge-0.1.0.tar.gz | sort
  unzip -l dist/mcp_ibge-0.1.0-py3-none-any.whl
  ```
- [ ] (Opcional, requer `twine`) `uv run --with twine twine check dist/*` —
      valida metadados e renderização do `README.md` como long_description.

## 4. Publicar no TestPyPI primeiro (recomendado)

- [ ] Criar/usar uma conta no [TestPyPI](https://test.pypi.org/) e gerar um
      API token específico para o projeto.
- [ ] Publicar:
  ```bash
  uv publish --publish-url https://test.pypi.org/legacy/ --token <TEST_PYPI_TOKEN>
  ```
- [ ] Em um ambiente limpo (venv novo ou `uvx` com `--index`), instalar a
      partir do TestPyPI e validar que o servidor inicia:
  ```bash
  uvx --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mcp-ibge
  ```
- [ ] Confirmar que o pacote inicia em `stdio` sem erros e que
      `MCP_IBGE_API_BASE_URL` continua restrito ao domínio oficial do IBGE
      (ver [docs/security.md](../security.md)).

## 5. Publicar no PyPI

- [ ] Criar/usar uma conta no [PyPI](https://pypi.org/) e gerar um API token
      específico para o projeto (escopo limitado ao projeto `mcp-ibge`, não
      "conta inteira").
- [ ] (Opcional, recomendado a médio prazo) Configurar **Trusted
      Publishing** (OIDC) do PyPI com o GitHub Actions, para publicar via CI
      sem armazenar token de longa duração.
- [ ] Publicar:
  ```bash
  uv publish --token <PYPI_TOKEN>
  ```
- [ ] Verificar a página do projeto em `https://pypi.org/project/mcp-ibge/`:
      versão, descrição, README renderizado, links, classificadores e
      licença corretos.
- [ ] Em um ambiente limpo, instalar via `uvx mcp-ibge` (ou
      `pip install mcp-ibge`) e confirmar que o servidor inicia.

## 6. Pós-publicação

- [ ] Criar a tag `v0.1.0` no git e dar push:
  ```bash
  git tag -a v0.1.0 -m "v0.1.0"
  git push origin v0.1.0
  ```
- [ ] Criar o **Release** no GitHub apontando para a tag `v0.1.0`, usando o
      conteúdo de [docs/releases/v0.1.0.md](v0.1.0.md) como descrição.
- [ ] Atualizar `README.md`:
  - [ ] Remover/ajustar o aviso "While the package is not yet published to an
        index..." na seção *Installation* agora que `uvx mcp-ibge` funciona
        a partir do PyPI.
- [ ] Conferir se o badge de CI no README aponta para o workflow correto e
      está "passing".
- [ ] Anunciar o release (ver
      [checklist de divulgação](announcement_checklist.md)).
