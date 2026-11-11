"""Modelos ORM (SQLAlchemy 2.x) espelhando backend/db/init/001_schema.sql.

A DDL (extensão pg_trgm, índices GIN/tsvector) é criada pelo script SQL, não
por `Base.metadata.create_all()` — expressar índices de trigram e tsvector de
forma confiável via metadata do SQLAlchemy é frágil. Estes modelos servem para
consultar/upsertar, não para criar o schema.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker
from sqlalchemy import create_engine

from pipeline.config import settings


class Base(DeclarativeBase):
    pass


class DimPrincipioAtivo(Base):
    __tablename__ = "dim_principio_ativo"

    id: Mapped[int] = mapped_column(primary_key=True)
    dcb: Mapped[str | None] = mapped_column(String(100))
    nome_normalizado: Mapped[str] = mapped_column(Text, unique=True, nullable=False)


class DimFabricante(Base):
    __tablename__ = "dim_fabricante"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    cnpj: Mapped[str | None] = mapped_column(String(18))


class DimFormaFarmaceutica(Base):
    __tablename__ = "dim_forma_farmaceutica"

    id: Mapped[int] = mapped_column(primary_key=True)
    descricao: Mapped[str] = mapped_column(Text, unique=True, nullable=False)


class DimComponenteSus(Base):
    __tablename__ = "dim_componente_sus"

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)


class FatoMedicamento(Base):
    __tablename__ = "fato_medicamento"
    __table_args__ = (UniqueConstraint("numero_registro_anvisa"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    numero_registro_anvisa: Mapped[str | None] = mapped_column(String(20))
    ggrem: Mapped[str | None] = mapped_column(String(20))
    ean: Mapped[str | None] = mapped_column(String(14))
    nome_comercial: Mapped[str] = mapped_column(Text, nullable=False)
    concentracao: Mapped[str | None] = mapped_column(Text)
    tipo_medicamento: Mapped[str | None] = mapped_column(Text)
    situacao_registro: Mapped[str | None] = mapped_column(String(30))
    preco_pf: Mapped[float | None] = mapped_column(Numeric(10, 2))
    preco_pmc: Mapped[float | None] = mapped_column(Numeric(10, 2))
    data_vigencia_preco: Mapped[dt.date | None]
    fk_principio_ativo: Mapped[int | None] = mapped_column(ForeignKey("dim_principio_ativo.id"))
    fk_fabricante: Mapped[int | None] = mapped_column(ForeignKey("dim_fabricante.id"))
    fk_forma_farmaceutica: Mapped[int | None] = mapped_column(ForeignKey("dim_forma_farmaceutica.id"))
    fk_componente_sus: Mapped[int | None] = mapped_column(ForeignKey("dim_componente_sus.id"))
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    principio_ativo: Mapped[DimPrincipioAtivo | None] = relationship()
    fabricante: Mapped[DimFabricante | None] = relationship()
    forma_farmaceutica: Mapped[DimFormaFarmaceutica | None] = relationship()
    componente_sus: Mapped[DimComponenteSus | None] = relationship()


engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, class_=Session)
