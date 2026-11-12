"""Extractor da lista de preços da CMED (PMC — Preço Máximo ao Consumidor).

Estrutura real do arquivo, verificada em 12/11/2026 baixando e inspecionando a
planilha publicada em CMED_PMC_PAGE_URL (não assumida a partir da documentação
antiga, que previa um ``.xls`` ISO-8859-1):

- Formato real é ``.xlsx`` (OOXML/UTF-8) — não precisa de tratamento de
  encoding nem de ``skiprows``; ``pd.read_excel(..., engine="openpyxl")`` lê
  direto, cabeçalho já na primeira linha da aba "Lista PMC".
- A URL do arquivo muda a cada publicação (tem timestamp no nome); a página em
  CMED_PMC_PAGE_URL é estável e tem um link cujo texto contém "PMC" e cujo
  href termina em ``.xlsx/@@download/file`` — descoberto via scraping
  (``_descobrir_url_arquivo_atual``).
- Colunas relevantes (nomes exatos, com espaço duplo antes de alguns "%"):
  REGISTRO, CÓDIGO GGREM, EAN 1, APRESENTAÇÃO, "PF 18 %", "PMC 18 %".
- ``REGISTRO`` é sempre uma string numérica de 13 dígitos. Os 9 primeiros
  dígitos são o mesmo valor de ``ANVISA.NUMERO_REGISTRO_PRODUTO``; os últimos
  4 identificam a apresentação (dose/embalagem) dentro daquele registro — 1
  registro ANVISA pode ter N linhas CMED. Confirmado empiricamente com a
  Novalgina: registro ANVISA "186200018" ↔ REGISTRO CMED "1862000180013",
  "1862000180021", etc. Isso corrige o Plano_Arquitetural.md, que descrevia a
  chave como "NUMERO_REGISTRO <-> GGREM" — GGREM é um código próprio da CMED,
  único por apresentação, sem relação direta com o registro ANVISA.
- Preços vêm como texto com vírgula decimal (ex. "50,28"); tratados como
  ausentes quando vazios ou "-" (produtos de uso hospitalar têm PMC omitido
  por resolução da própria CMED — não é erro de dado).
- A data de vigência não é uma coluna por linha: é a data de publicação da
  lista inteira, na aba "Cabeçalho" ("Publicada em DD/MM/AAAA...") — extraída
  uma vez por ``extract()`` e repetida em todas as linhas do lote.
- "PMC 18 %"/"PF 18 %" (alíquota de ICMS de 18%) foram escolhidas como preço
  de referência nacional — é um teto de preço por apresentação que varia por
  estado (alíquota de ICMS), não "o" preço nem o preço de uma farmácia
  específica. A API/UI devem deixar isso explícito.

TODO (sessão futura): como 1 registro ANVISA mapeia para N apresentações CMED
e ``fato_medicamento`` guarda só 1 linha por registro, esta implementação fica
com a apresentação de MENOR "PMC 18 %" como representante do produto inteiro
(simplificação deliberada). Se um dia for preciso comparar preço por
embalagem/dose específica, vale um modelo 1:N dedicado em vez de forçar isso
nas colunas singulares de fato_medicamento.
"""

from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from urllib.parse import urljoin

import openpyxl
import pandas as pd
import requests
from bs4 import BeautifulSoup

from pipeline.config import settings
from pipeline.extractors.base_extractor import BaseExtractor

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
SAMPLE_PATH = FIXTURES_DIR / "cmed_sample.xlsx"

SHEET_DADOS = "Lista PMC"
SHEET_CABECALHO = "Cabeçalho"

COL_REGISTRO = "REGISTRO"
COL_GGREM = "CÓDIGO GGREM"
COL_EAN1 = "EAN 1"
COL_APRESENTACAO = "APRESENTAÇÃO"
COL_PF = "PF 18 %"
COL_PMC = "PMC 18 %"


class CmedExtractor(BaseExtractor):
    def __init__(self, use_sample: bool | None = None) -> None:
        self.use_sample = settings.cmed_use_sample if use_sample is None else use_sample

    def extract(self) -> pd.DataFrame:
        raw_path = self._resolve_source_file()
        data_vigencia = self._data_publicacao(raw_path)

        df = pd.read_excel(raw_path, sheet_name=SHEET_DADOS, dtype=str, engine="openpyxl")
        df = self._filter_valid_rows(df)
        df["_preco_pf"] = df[COL_PF].map(self._parse_preco)
        df["_preco_pmc"] = df[COL_PMC].map(self._parse_preco)
        df["_numero_registro_anvisa"] = df[COL_REGISTRO].str[:9]

        df = self._selecionar_apresentacao_representativa(df)
        return self._to_canonical_schema(df, data_vigencia)

    def _resolve_source_file(self) -> Path:
        if self.use_sample:
            return SAMPLE_PATH

        today = dt.date.today().isoformat()
        dest = settings.raw_data_dir / f"cmed_{today}.xlsx"
        if dest.exists():
            return dest  # cache do dia: não baixa de novo se já rodou hoje
        url = settings.cmed_xlsx_url or self._descobrir_url_arquivo_atual()
        return self._download(url, dest)

    @staticmethod
    def _descobrir_url_arquivo_atual() -> str:
        response = requests.get(settings.cmed_pmc_page_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "lista_pmc_" in href and href.endswith(".xlsx/@@download/file"):
                return urljoin("https://www.gov.br", href)

        raise RuntimeError(
            "Não encontrei o link da lista PMC na página da CMED — o HTML da "
            f"página pode ter mudado ({settings.cmed_pmc_page_url})."
        )

    @staticmethod
    def _data_publicacao(raw_path: Path) -> dt.date:
        wb = openpyxl.load_workbook(raw_path, read_only=True, data_only=True)
        try:
            ws = wb[SHEET_CABECALHO]
            for row in ws.iter_rows(min_row=1, max_row=10, values_only=True):
                for valor in row:
                    if isinstance(valor, str) and "Publicada em" in valor:
                        m = re.search(r"(\d{2})/(\d{2})/(\d{4})", valor)
                        if m:
                            dia, mes, ano = m.groups()
                            return dt.date(int(ano), int(mes), int(dia))
            raise RuntimeError(
                f"Não encontrei a data de publicação na aba '{SHEET_CABECALHO}' de {raw_path}."
            )
        finally:
            wb.close()

    @staticmethod
    def _filter_valid_rows(df: pd.DataFrame) -> pd.DataFrame:
        # REGISTRO é a chave de cruzamento com a ANVISA — sem ele (ou fora do
        # formato de 13 dígitos observado no arquivo real), a linha é inútil.
        mask = df[COL_REGISTRO].notna() & df[COL_REGISTRO].str.fullmatch(r"\d{13}").fillna(False)
        return df.loc[mask].copy()

    @staticmethod
    def _parse_preco(valor: object) -> float | None:
        if valor is None or (isinstance(valor, float) and pd.isna(valor)):
            return None
        texto = str(valor).strip()
        if not texto or texto == "-":
            return None
        try:
            return float(texto.replace(".", "").replace(",", "."))
        except ValueError:
            return None

    @staticmethod
    def _valor_ou_none(valor: object) -> str | None:
        if valor is None or (isinstance(valor, float) and pd.isna(valor)):
            return None
        texto = str(valor).strip()
        if not texto or set(texto) <= {"-", " "}:
            return None
        return texto

    @staticmethod
    def _selecionar_apresentacao_representativa(df: pd.DataFrame) -> pd.DataFrame:
        # 1 registro ANVISA -> N apresentações CMED (ver TODO no docstring do
        # módulo): fica a de menor PMC 18%; sem PMC em nenhuma (produto
        # hospitalar), fica a primeira mesmo assim, só pra não perder
        # ggrem/ean.
        df = df.copy()
        df["_ordenacao"] = df["_preco_pmc"].fillna(float("inf"))
        df = df.sort_values("_ordenacao", kind="stable")
        df = df.drop_duplicates(subset="_numero_registro_anvisa", keep="first")
        return df.drop(columns="_ordenacao")

    @classmethod
    def _to_canonical_schema(cls, df: pd.DataFrame, data_vigencia: dt.date) -> pd.DataFrame:
        out = pd.DataFrame(
            {
                "numero_registro_anvisa": df["_numero_registro_anvisa"],
                "ggrem": df[COL_GGREM].map(cls._valor_ou_none),
                "ean": df[COL_EAN1].map(cls._valor_ou_none),
                "preco_pf": df["_preco_pf"],
                "preco_pmc": df["_preco_pmc"],
                "data_vigencia_preco": data_vigencia,
                "forma_farmaceutica_raw": df[COL_APRESENTACAO].map(cls._valor_ou_none),
            }
        )
        return out.reset_index(drop=True)
