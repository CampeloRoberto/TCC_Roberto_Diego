from datetime import date

from pydantic import BaseModel


class MedicamentoBusca(BaseModel):
    id: int
    nome_comercial: str
    principio_ativo: str | None = None
    fabricante: str | None = None
    tipo_medicamento: str | None = None
    situacao_registro: str | None = None
    # Preço de referência CMED (PMC, alíquota padrão 18% ICMS) — teto
    # nacional por apresentação, não o preço de uma farmácia específica.
    preco_pmc: float | None = None


class BuscaResponse(BaseModel):
    total: int
    resultados: list[MedicamentoBusca]


class MedicamentoDetalhe(MedicamentoBusca):
    preco_pf: float | None = None
    data_vigencia_preco: date | None = None
    ean: str | None = None
    concentracao: str | None = None


class Equivalente(BaseModel):
    id: int
    nome_comercial: str
    fabricante: str | None = None
    tipo_medicamento: str | None = None
    preco_pmc: float | None = None


class EquivalenciasResponse(BaseModel):
    principio_ativo: str | None
    total: int
    equivalentes: list[Equivalente]
