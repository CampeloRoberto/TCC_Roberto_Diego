"""Testes do extractor da CMED usando o fixture local (não precisa de banco
nem de internet). Rodar de dentro da pasta backend:  python -m pytest -v
"""

import pandas as pd
import pytest

from pipeline.extractors.cmed_extractor import CmedExtractor


@pytest.fixture(scope="module")
def df() -> pd.DataFrame:
    return CmedExtractor(use_sample=True).extract()


def _linha(df: pd.DataFrame, numero_registro_anvisa: str) -> pd.Series:
    return df.loc[df["numero_registro_anvisa"] == numero_registro_anvisa].iloc[0]


def test_prefixo_de_9_digitos_vira_numero_registro_anvisa(df):
    # REGISTRO "1862000180110" -> numero_registro_anvisa "186200018", igual
    # ao número de registro da Novalgina no fixture da ANVISA.
    assert "186200018" in set(df["numero_registro_anvisa"])
    assert df["numero_registro_anvisa"].is_unique


def test_escolhe_apresentacao_de_menor_pmc_quando_ha_varias(df):
    # Fixture tem 4 apresentações da Novalgina (mesmo registro) com PMC 18%
    # 16,45 / 214,06 / 24,37 / 555,77 — deve ficar só a de menor preço.
    linha = _linha(df, "186200018")
    assert linha["preco_pmc"] == pytest.approx(16.45)
    assert linha["ggrem"] == "615324020006317"


def test_preco_ausente_vira_none(df):
    # Produto hospitalar (Abatacepte/Orencia): PMC 18% omitido por resolução
    # da CMED, só tem PF.
    linha = _linha(df, "101800390")
    assert pd.isna(linha["preco_pmc"])
    assert linha["preco_pf"] == pytest.approx(2589.85)


def test_virgula_decimal_convertida_para_ponto(df):
    linha = _linha(df, "186200018")
    assert isinstance(linha["preco_pmc"], float)


def test_ean_presente(df):
    linha = _linha(df, "186200018")
    assert linha["ean"] == "7891058487096"
