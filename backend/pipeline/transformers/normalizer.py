from unidecode import unidecode


def normalize_text(value: str | None) -> str:
    """lowercase + strip + remoção de acentos — usado para casar nomes entre
    ANVISA/CMED/RENAME (ex.: "Dipirona" e "DIPIRONA " -> "dipirona") e para
    chave de dedupe das dimensões (dim_principio_ativo, dim_fabricante, ...).
    """
    if value is None:
        return ""
    return unidecode(value).strip().lower()
