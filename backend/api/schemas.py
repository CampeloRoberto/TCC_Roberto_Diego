from pydantic import BaseModel


class MedicamentoBusca(BaseModel):
    id: int
    nome_comercial: str
    principio_ativo: str | None = None
    fabricante: str | None = None
    tipo_medicamento: str | None = None
    situacao_registro: str | None = None


class BuscaResponse(BaseModel):
    total: int
    resultados: list[MedicamentoBusca]
