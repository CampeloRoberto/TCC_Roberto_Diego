"""Extractor da base de medicamentos registrados da ANVISA (Dados Abertos).

Estrutura real do CSV, verificada em 09/11/2026 contra o arquivo publicado em
ANVISA_CSV_URL (não assumida a partir da documentação antiga da ANVISA):

- separador ``;`` (não ``,``)
- encoding ISO-8859-1 / latin-1 (não UTF-8 como o Plano_Arquitetural.md assumia)
- ~229.000 linhas; cada linha é um *processo regulatório*, não um produto único —
  um mesmo NUMERO_REGISTRO_PRODUTO aparece em várias linhas (~84% são duplicatas).
- colunas: TIPO_PRODUTO, NOME_PRODUTO, DATA_FINALIZACAO_PROCESSO, CATEGORIA_REGULATORIA,
  NUMERO_REGISTRO_PRODUTO, DATA_VENCIMENTO_REGISTRO, NUMERO_PROCESSO, CLASSE_TERAPEUTICA,
  EMPRESA_DETENTORA_REGISTRO, SITUACAO_REGISTRO, PRINCIPIO_ATIVO
- não existem colunas de forma farmacêutica, concentração, EAN ou GGREM nesta base —
  esses campos só serão preenchidos quando CMED entrar (fk_forma_farmaceutica, ean,
  ggrem, preco_* ficam NULL nesta fatia).
- SITUACAO_REGISTRO contém ``Ativo``/``Inativo`` (não ``VÁLIDO`` como documentação antiga
  de 2020 da ANVISA sugeria).
- EMPRESA_DETENTORA_REGISTRO vem como ``"<CNPJ> - <NOME DA EMPRESA>"`` numa única coluna.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd

from pipeline.config import settings
from pipeline.extractors.base_extractor import BaseExtractor

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
SAMPLE_PATH = FIXTURES_DIR / "anvisa_sample.csv"

# CATEGORIA_REGULATORIA -> tipo_medicamento. Produtos "Novo" são o medicamento de
# referência (inovador); os demais rótulos (Específico, Biológico, Fitoterápico, etc.)
# não mapeiam para o trio referência/genérico/similar e são mantidos como vieram,
# apenas normalizados (minúsculo/sem acento inconsistente), já que o dataset real
# tem ~13 categorias distintas, não só as 3 do enum didático do Plano Arquitetural.
CATEGORIA_PARA_TIPO = {
    "novo": "referência",
    "genérico": "genérico",
    "similar": "similar",
}

PRINCIPIO_ATIVO_NAO_INFORMADO = "NÃO INFORMADO"


class AnvisaExtractor(BaseExtractor):
    def __init__(self, use_sample: bool | None = None) -> None:
        self.use_sample = settings.anvisa_use_sample if use_sample is None else use_sample

    def extract(self) -> pd.DataFrame:
        raw_path = self._resolve_source_file()
        encoding = "utf-8" if self.use_sample else "latin-1"

        df = pd.read_csv(
            raw_path,
            sep=";",
            encoding=encoding,
            dtype=str,
            quotechar='"',
            low_memory=False,
        )

        df = self._filter_valid_rows(df)
        df = self._collapse_duplicate_registros(df)
        df = self._to_canonical_schema(df)
        return df

    def _resolve_source_file(self) -> Path:
        if self.use_sample:
            return SAMPLE_PATH

        today = dt.date.today().isoformat()
        dest = settings.raw_data_dir / f"anvisa_{today}.csv"
        if dest.exists():
            return dest  # cache do dia: não baixa de novo se já rodou hoje
        return self._download(settings.anvisa_csv_url, dest)

    @staticmethod
    def _filter_valid_rows(df: pd.DataFrame) -> pd.DataFrame:
        # Só produtos com registro ativo e com número de registro preenchido
        # (o NUMERO_REGISTRO_PRODUTO é a chave única em fato_medicamento).
        mask = (df["SITUACAO_REGISTRO"] == "Ativo") & df["NUMERO_REGISTRO_PRODUTO"].notna()
        return df.loc[mask].copy()

    @staticmethod
    def _collapse_duplicate_registros(df: pd.DataFrame) -> pd.DataFrame:
        # Cada NUMERO_REGISTRO_PRODUTO pode ter várias linhas (um processo
        # regulatório por linha). Fica só a linha do processo mais recente.
        df["_data_processo"] = pd.to_datetime(
            df["DATA_FINALIZACAO_PROCESSO"], format="%d/%m/%Y", errors="coerce"
        )
        df = df.sort_values("_data_processo", ascending=False)
        df = df.drop_duplicates(subset=["NUMERO_REGISTRO_PRODUTO"], keep="first")
        return df.drop(columns="_data_processo")

    @staticmethod
    def _to_canonical_schema(df: pd.DataFrame) -> pd.DataFrame:
        empresa = df["EMPRESA_DETENTORA_REGISTRO"].fillna("").str.split(" - ", n=1)

        def cnpj_de(partes: list[str]) -> str | None:
            if len(partes) == 2 and partes[0].strip().isdigit():
                return partes[0].strip()
            return None

        def nome_de(partes: list[str]) -> str:
            if len(partes) == 2 and partes[0].strip().isdigit():
                return partes[1].strip()
            return (partes[0] if partes else "").strip()

        categoria_lower = df["CATEGORIA_REGULATORIA"].str.strip().str.lower()

        out = pd.DataFrame(
            {
                "numero_registro_anvisa": df["NUMERO_REGISTRO_PRODUTO"].str.strip(),
                "nome_comercial": df["NOME_PRODUTO"].str.strip(),
                "tipo_medicamento": categoria_lower.map(CATEGORIA_PARA_TIPO).fillna(categoria_lower),
                "situacao_registro": df["SITUACAO_REGISTRO"],
                "principio_ativo_raw": df["PRINCIPIO_ATIVO"].fillna(PRINCIPIO_ATIVO_NAO_INFORMADO).str.strip(),
                "fabricante_nome_raw": empresa.map(nome_de),
                "fabricante_cnpj": empresa.map(cnpj_de),
                # Não existem nesta fonte — ficam para quando CMED for implementado.
                "forma_farmaceutica_raw": None,
                "concentracao": None,
            }
        )
        return out.reset_index(drop=True)
