from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.routes.medicamentos import get_session
from api.schemas import Equivalente, EquivalenciasResponse
from pipeline.loaders.models import DimFabricante, FatoMedicamento

router = APIRouter(prefix="/medicamentos", tags=["equivalencias"])


@router.get("/{id}/equivalencias", response_model=EquivalenciasResponse)
def listar_equivalencias(
    id: int,
    incluir_proprio: bool = Query(False, description="inclui o próprio medicamento na lista"),
    incluir_inativos: bool = Query(False, description="inclui registros com situação Inativo"),
    session: Session = Depends(get_session),
) -> EquivalenciasResponse:
    medicamento = session.get(FatoMedicamento, id)
    if medicamento is None:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado.")

    if medicamento.fk_principio_ativo is None:
        return EquivalenciasResponse(principio_ativo=None, total=0, equivalentes=[])

    query = (
        session.query(
            FatoMedicamento.id,
            FatoMedicamento.nome_comercial,
            DimFabricante.nome.label("fabricante"),
            FatoMedicamento.tipo_medicamento,
            FatoMedicamento.preco_pmc,
        )
        .outerjoin(DimFabricante, FatoMedicamento.fk_fabricante == DimFabricante.id)
        .filter(FatoMedicamento.fk_principio_ativo == medicamento.fk_principio_ativo)
    )
    if not incluir_inativos:
        query = query.filter(FatoMedicamento.situacao_registro == "Ativo")
    if not incluir_proprio:
        query = query.filter(FatoMedicamento.id != id)

    # Quem tem preço vem primeiro; dentro de quem tem preço, o mais barato
    # primeiro — é o caso de uso central (comparar equivalentes por preço).
    query = query.order_by(FatoMedicamento.preco_pmc.is_(None), FatoMedicamento.preco_pmc.asc())
    linhas = query.all()

    equivalentes = [Equivalente(**linha._asdict()) for linha in linhas]
    nome_principio = medicamento.principio_ativo.nome_normalizado if medicamento.principio_ativo else None
    return EquivalenciasResponse(principio_ativo=nome_principio, total=len(equivalentes), equivalentes=equivalentes)
