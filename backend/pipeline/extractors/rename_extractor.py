"""Extractor da RENAME (PDF, publicação irregular via Portaria GM/MS).

TODO (sessão futura): baixar o PDF vigente (ex.: RENAME 2024) de
https://www.gov.br/saude/pt-br/composicao/sectics/rename, parsear com
pdfplumber, extrair a lista de princípios ativos/apresentações por componente
da assistência farmacêutica (básico/estratégico/especializado), normalizar o
nome do princípio ativo (DCB) com a mesma função de pipeline/transformers/
normalizer.py usada no ANVISA/CMED, e casar via PRINCIPIO_ATIVO normalizado
(ver estratégia de matching em Plano_Arquitetural.md). Popula
dim_componente_sus e fk_componente_sus em fato_medicamento, hoje sempre NULL.

Diferente de ANVISA/CMED, este extractor não roda no ciclo mensal automático:
é disparado manualmente sempre que o Ministério da Saúde publica uma nova
edição (não há cadência fixa).
"""

from pipeline.extractors.base_extractor import BaseExtractor


class RenameExtractor(BaseExtractor):
    def extract(self):
        raise NotImplementedError("RENAME extractor ainda não implementado — ver TODO no módulo.")
