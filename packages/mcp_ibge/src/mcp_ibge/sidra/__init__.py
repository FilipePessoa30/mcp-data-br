"""SIDRA Query Builder: descoberta, explicação, sugestão e validação de consultas ao SIDRA.

Submódulos:
    - `metadata_parser`: converte os metadados brutos de um agregado
      (`/agregados/{id}/metadados`) em um modelo tipado, com periodicidade,
      níveis territoriais, variáveis, classificações e limitações em texto.
    - `query_builder`: valida `variaveis`, `localidades`, `periodos` e
      `classificacao` de uma consulta contra os metadados de um agregado.
    - `suggestions`: sugere agregados, variáveis e localidades a partir de
      palavras-chave de uma pergunta em linguagem natural, por busca em
      metadados (sem uso de modelos de linguagem).
"""

from __future__ import annotations
