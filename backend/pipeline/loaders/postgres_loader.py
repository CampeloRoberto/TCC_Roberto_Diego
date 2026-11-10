from __future__ import annotations

import pandas as pd
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from pipeline.loaders.models import DimFabricante, DimPrincipioAtivo, FatoMedicamento
from pipeline.transformers.normalizer import normalize_text


def _get_or_create_principio_ativo(session: Session, cache: dict[str, int], nome_raw: str) -> int:
    chave = normalize_text(nome_raw)
    if chave in cache:
        return cache[chave]

    existente = session.query(DimPrincipioAtivo).filter_by(nome_normalizado=chave).one_or_none()
    if existente is None:
        existente = DimPrincipioAtivo(nome_normalizado=chave)
        session.add(existente)
        session.flush()  # garante existente.id sem precisar de commit

    cache[chave] = existente.id
    return existente.id


def _get_or_create_fabricante(session: Session, cache: dict[str, int], nome_raw: str, cnpj: str | None) -> int | None:
    if not nome_raw:
        return None
    chave = normalize_text(nome_raw)
    if chave in cache:
        return cache[chave]

    existente = session.query(DimFabricante).filter_by(nome=nome_raw).one_or_none()
    if existente is None:
        existente = DimFabricante(nome=nome_raw, cnpj=cnpj)
        session.add(existente)
        session.flush()

    cache[chave] = existente.id
    return existente.id


def load_anvisa_dataframe(df: pd.DataFrame, session: Session) -> dict[str, int]:
    """Faz get-or-create nas dimensões afetadas pela ANVISA (princípio ativo,
    fabricante) e upsert em fato_medicamento por numero_registro_anvisa.

    ggrem, ean, preco_pf, preco_pmc, data_vigencia_preco, fk_forma_farmaceutica
    e fk_componente_sus não são tocados aqui — dependem de CMED/RENAME, ainda
    não implementados (ver pipeline/extractors/cmed_extractor.py e
    rename_extractor.py).
    """
    principio_cache: dict[str, int] = {}
    fabricante_cache: dict[str, int] = {}

    linhas = []
    for row in df.itertuples(index=False):
        fk_principio = _get_or_create_principio_ativo(session, principio_cache, row.principio_ativo_raw)
        fk_fabricante = _get_or_create_fabricante(
            session, fabricante_cache, row.fabricante_nome_raw, row.fabricante_cnpj
        )

        linhas.append(
            {
                "numero_registro_anvisa": row.numero_registro_anvisa,
                "nome_comercial": row.nome_comercial,
                "tipo_medicamento": row.tipo_medicamento,
                "situacao_registro": row.situacao_registro,
                "concentracao": row.concentracao,
                "fk_principio_ativo": fk_principio,
                "fk_fabricante": fk_fabricante,
            }
        )

    if not linhas:
        return {"upserted": 0}

    stmt = pg_insert(FatoMedicamento).values(linhas)
    stmt = stmt.on_conflict_do_update(
        index_elements=["numero_registro_anvisa"],
        set_={
            "nome_comercial": stmt.excluded.nome_comercial,
            "tipo_medicamento": stmt.excluded.tipo_medicamento,
            "situacao_registro": stmt.excluded.situacao_registro,
            "concentracao": stmt.excluded.concentracao,
            "fk_principio_ativo": stmt.excluded.fk_principio_ativo,
            "fk_fabricante": stmt.excluded.fk_fabricante,
            "updated_at": func.now(),
        },
    )
    session.execute(stmt)
    session.commit()

    return {"upserted": len(linhas)}
