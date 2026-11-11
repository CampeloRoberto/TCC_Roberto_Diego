"""Testes do extractor da ANVISA usando o fixture local (não precisa de banco
nem de internet). Rodar de dentro da pasta backend:  python -m pytest -v
"""

import pandas as pd
import pytest

from pipeline.extractors.anvisa_extractor import AnvisaExtractor


@pytest.fixture(scope="module")
def df() -> pd.DataFrame:
    return AnvisaExtractor(use_sample=True).extract()


def _linha(df: pd.DataFrame, nome: str) -> pd.Series:
    return df.loc[df["nome_comercial"] == nome].iloc[0]


def test_um_registro_por_numero(df):
    assert df["numero_registro_anvisa"].is_unique


def test_fica_o_processo_mais_recente(df):
    # NOXX aparece duas vezes no fixture; fica a linha de 2022, não a de 2015.
    assert "NOXX" in set(df["nome_comercial"])
    assert "NOXX (PROCESSO ANTERIOR)" not in set(df["nome_comercial"])


def test_linha_sem_numero_de_registro_e_descartada(df):
    assert "LABORHEX 2,0%" not in set(df["nome_comercial"])


def test_inativos_sao_mantidos(df):
    # Antes eram descartados e o banco nunca ficava sabendo do cancelamento.
    assert _linha(df, "INSUMAN")["situacao_registro"] == "Inativo"


def test_principio_ativo_vazio_vira_nulo(df):
    # Antes virava "NÃO INFORMADO", juntando produtos sem relação entre si.
    assert pd.isna(_linha(df, "ZIOR")["principio_ativo_raw"])


def test_categoria_mapeada_para_tipo(df):
    assert _linha(df, "NOVALGINA")["tipo_medicamento"] == "referência"
    assert _linha(df, "MALEATO DE ENALAPRIL")["tipo_medicamento"] == "genérico"
    assert _linha(df, "LYSUGI")["tipo_medicamento"] == "similar"


def test_empresa_separada_em_cnpj_e_nome(df):
    linha = _linha(df, "NOVALGINA")
    assert linha["fabricante_cnpj"] == "38391432000143"
    assert linha["fabricante_nome_raw"] == "OPELLA HEALTHCARE BRAZIL LTDA"
