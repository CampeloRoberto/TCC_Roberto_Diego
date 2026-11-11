from __future__ import annotations

from typing import Any

import pandas as pd
from sqlalchemy import func, or_
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from pipeline.loaders.models import DimFabricante, DimPrincipioAtivo, FatoMedicamento
from pipeline.transformers.normalizer import normalize_text

# O PostgreSQL aceita no máximo 65.535 parâmetros por comando. Com 7 colunas
# por linha, um INSERT único estoura acima de ~9.300 linhas — a base real da
# ANVISA tem dezenas de milhares. 1.000 linhas por lote = 7.000 parâmetros.
BATCH_SIZE = 1000

# Colunas que o upsert atualiza. Também são as colunas comparadas para decidir
# se a linha mudou de verdade (ver _upsert_lote).
COLUNAS_ATUALIZAVEIS = (
    "nome_comercial",
    "tipo_medicamento",
    "situacao_registro",
    "concentracao",
    "fk_principio_ativo",
    "fk_fabricante",
)


def _texto_ou_none(valor: Any) -> str | None:
    """O pandas troca None por NaN dentro do DataFrame; aqui volta a ser None
    (NULL no banco). Strings vazias também viram None."""
    if valor is None or (not isinstance(valor, str) and pd.isna(valor)):
        return None
    valor = str(valor).strip()
    return valor or None


def _get_or_create_principio_ativo(session: Session, cache: dict[str, int], nome_raw: str | None) -> int | None:
    # Sem princípio ativo -> NULL. Não cria uma linha "não informado" na
    # dimensão, senão todos esses produtos viram "equivalentes" entre si.
    if nome_raw is None:
        return None
    chave = normalize_text(nome_raw)
    if not chave:
        return None
    if chave in cache:
        return cache[chave]

    existente = session.query(DimPrincipioAtivo).filter_by(nome_normalizado=chave).one_or_none()
    if existente is None:
        existente = DimPrincipioAtivo(nome_normalizado=chave)
        session.add(existente)
        session.flush()  # garante existente.id sem precisar de commit

    cache[chave] = existente.id
    return existente.id


def _get_or_create_fabricante(session: Session, cache: dict[str, int], nome_raw: str | None, cnpj: str | None) -> int | None:
    if nome_raw is None:
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


def _upsert_lote(session: Session, linhas: list[dict[str, Any]]) -> int:
    """Upsert de um lote. Só atualiza (e só mexe em updated_at) quando algum
    campo mudou de fato. Sem isso, toda execução mensal marcaria todas as
    linhas como alteradas e o sync incremental mandaria a base inteira de
    novo para o celular. Retorna quantas linhas foram inseridas ou alteradas."""
    tabela = FatoMedicamento.__table__
    stmt = pg_insert(tabela).values(linhas)
    stmt = stmt.on_conflict_do_update(
        index_elements=["numero_registro_anvisa"],
        set_={**{col: stmt.excluded[col] for col in COLUNAS_ATUALIZAVEIS}, "updated_at": func.now()},
        where=or_(*[tabela.c[col].is_distinct_from(stmt.excluded[col]) for col in COLUNAS_ATUALIZAVEIS]),
    )
    resultado = session.execute(stmt)
    return resultado.rowcount or 0


def load_anvisa_dataframe(df: pd.DataFrame, session: Session) -> dict[str, int]:
    """Faz get-or-create nas dimensões afetadas pela ANVISA (princípio ativo,
    fabricante) e upsert em fato_medicamento por numero_registro_anvisa, em
    lotes de BATCH_SIZE linhas, numa única transação (ou carrega tudo, ou nada).

    ggrem, ean, preco_pf, preco_pmc, data_vigencia_preco, fk_forma_farmaceutica
    e fk_componente_sus não são tocados aqui — dependem de CMED/RENAME, ainda
    não implementados (ver pipeline/extractors/cmed_extractor.py e
    rename_extractor.py).

    Retorna {"processadas": linhas lidas, "alteradas": inseridas + atualizadas}.
    """
    principio_cache: dict[str, int] = {}
    fabricante_cache: dict[str, int] = {}

    linhas = []
    for row in df.itertuples(index=False):
        fk_principio = _get_or_create_principio_ativo(
            session, principio_cache, _texto_ou_none(row.principio_ativo_raw)
        )
        fk_fabricante = _get_or_create_fabricante(
            session,
            fabricante_cache,
            _texto_ou_none(row.fabricante_nome_raw),
            _texto_ou_none(row.fabricante_cnpj),
        )

        linhas.append(
            {
                "numero_registro_anvisa": row.numero_registro_anvisa,
                "nome_comercial": row.nome_comercial,
                "tipo_medicamento": _texto_ou_none(row.tipo_medicamento),
                "situacao_registro": _texto_ou_none(row.situacao_registro),
                "concentracao": _texto_ou_none(row.concentracao),
                "fk_principio_ativo": fk_principio,
                "fk_fabricante": fk_fabricante,
            }
        )

    alteradas = 0
    try:
        for inicio in range(0, len(linhas), BATCH_SIZE):
            alteradas += _upsert_lote(session, linhas[inicio : inicio + BATCH_SIZE])
        session.commit()
    except Exception:
        session.rollback()
        raise

    return {"processadas": len(linhas), "alteradas": alteradas}
