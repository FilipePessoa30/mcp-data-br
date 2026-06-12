# Examples

Ready-to-use configuration files and prompts for connecting MCP clients to
the servers in this repository. Today that's `mcp-ibge`; future modules will
add their own subfolders here following the same pattern.

- [`claude_desktop/`](claude_desktop/) — `claude_desktop_config.json` snippets
  for Claude Desktop (uvx, Windows, and local development).
- [`cursor/`](cursor/) — equivalent snippets for Cursor's `mcp.json`.
- [`open_webui/`](open_webui/) — running MCP servers behind
  [`mcpo`](https://github.com/open-webui/mcpo) for Open WebUI.
- [`agent_recipes/`](agent_recipes/) — natural-language prompts and example
  tool calls for each module, useful for testing a new connection.
- [`integrations/`](integrations/) — minimal agent examples using
  `mcp-ibge` from LangChain, LlamaIndex, the OpenAI Agents SDK, and a plain
  `mcp` + Ollama script — all running locally, no API key required.

For module-specific setup instructions, see each package's docs, e.g.
[packages/mcp_ibge/docs/client_setup.md](../packages/mcp_ibge/docs/client_setup.md).
