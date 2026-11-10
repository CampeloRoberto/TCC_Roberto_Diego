"""Extractor da lista de preços da CMED (XLS, ISO-8859-1, atualização mensal).

TODO (sessão futura): baixar a planilha de conformidade/preços publicada em
https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/cmed/precos, tratar o
encoding ISO-8859-1, normalizar separador decimal (ex.: "1.234,56" -> 1234.56),
remover asteriscos de campos marcados, e casar com ANVISA via GGREM (ver
estratégia de matching em Plano_Arquitetural.md: ANVISA.NUMERO_REGISTRO <->
CMED.GGREM). Popula ggrem, ean, preco_pf, preco_pmc, data_vigencia_preco em
fato_medicamento, hoje NULL porque só o ANVISA extractor está implementado.
"""

from pipeline.extractors.base_extractor import BaseExtractor


class CmedExtractor(BaseExtractor):
    def extract(self):
        raise NotImplementedError("CMED extractor ainda não implementado — ver TODO no módulo.")
