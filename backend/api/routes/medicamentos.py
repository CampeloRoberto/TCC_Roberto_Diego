from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.schemas import BuscaResponse, MedicamentoBusca
from pipeline.loaders.models import DimFabricante, DimPrincipioAtivo, FatoMedicamento, SessionLocal

router = APIRouter(prefix="/medicamentos", tags=["medicamentos"])


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@router.get("/busca", response_model=BuscaResponse)
def buscar(
    q: str = Query(..., min_length=2, description="nome comercial do medicamento"),
    fuzzy: bool = False,
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    incluir_inativos: bool = Query(False, description="inclui registros com situação Inativo"),
    session: Session = Depends(get_session),
) -> BuscaResponse:
    base = (
        session.query(
            FatoMedicamento.id,
            FatoMedicamento.nome_comercial,
            DimPrincipioAtivo.nome_normalizado.label("principio_ativo"),
            DimFabricante.nome.label("fabricante"),
            FatoMedicamento.tipo_medicamento,
            FatoMedicamento.situacao_registro,
        )
        .outerjoin(DimPrincipioAtivo, FatoMedicamento.fk_principio_ativo == DimPrincipioAtivo.id)
        .outerjoin(DimFabricante, FatoMedicamento.fk_fabricante == DimFabricante.id)
    )

    # O ETL carrega também os registros inativos (para o banco e o sync
    # saberem que foram cancelados); a busca mostra só os ativos por padrão.
    if not incluir_inativos:
        base = base.filter(FatoMedicamento.situacao_registro == "Ativo")

    if fuzzy:
        # pg_trgm: `%` usa o threshold de similaridade configurado no Postgres
        # (default 0.3); ordena pelos mais parecidos primeiro.
        base = base.filter(FatoMedicamento.nome_comercial.op("%")(q))
        base = base.order_by(func.similarity(FatoMedicamento.nome_comercial, q).desc())
    else:
        base = base.filter(FatoMedicamento.nome_comercial.ilike(f"%{q}%"))
        base = base.order_by(FatoMedicamento.nome_comercial)

    total = base.count()
    linhas = base.offset(offset).limit(limit).all()

    resultados = [
        MedicamentoBusca(
            id=linha.id,
            nome_comercial=linha.nome_comercial,
            principio_ativo=linha.principio_ativo,
            fabricante=linha.fabricante,
            tipo_medicamento=linha.tipo_medicamento,
            situacao_registro=linha.situacao_registro,
        )
        for linha in linhas
    ]
    return BuscaResponse(total=total, resultados=resultados)


@router.get("/ean/{ean}")
def buscar_por_ean(ean: str):
    # TODO: só faz sentido quando o CMED extractor popular fato_medicamento.ean
    # (ver pipeline/extractors/cmed_extractor.py) — nenhuma linha tem EAN hoje.
    # 501 em vez de NotImplementedError, que virava erro 500 genérico.
    raise HTTPException(status_code=501, detail="Busca por EAN depende do CMED extractor, ainda não implementado.")
