"""Modelos Pydantic dos dados do INEP e do envelope de resposta (planejado).

Seguindo `mcp_ibge.schemas`, cada conjunto de dados (escolas, indicadores
Ideb/Saeb, microdados disponíveis, perfil educacional municipal) terá seu
próprio modelo tipado, além do envelope compartilhado
`{"ok", "data", "metadata", "warnings", "errors"}` descrito em
`docs/data_sources.md`.

Nenhum modelo implementado ainda — os esquemas concretos dependem das
decisões de fonte de dados registradas em `docs/modules/inep.md`
("Fontes planejadas" e "Desafios"), em particular o mapeamento de códigos
(`co_municipio`, `co_entidade`/INEP da escola) para o código de município do
IBGE (`mcp_ibge.obter_codigo_municipio`), usado para integração entre
módulos.
"""
