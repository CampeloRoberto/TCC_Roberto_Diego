"""Cruzamento entre as 3 bases (ver Plano_Arquitetural.md, com a correção
empírica abaixo):

    ANVISA <-> CMED   : ANVISA.numero_registro_anvisa (9 dígitos) é igual aos
                        9 primeiros dígitos de CMED.REGISTRO (13 dígitos; os
                        últimos 4 identificam a apresentação dentro daquele
                        registro). NÃO é "NUMERO_REGISTRO <-> GGREM" como o
                        Plano_Arquitetural.md descrevia — GGREM é um código
                        próprio da CMED, único por apresentação, sem relação
                        direta com o registro ANVISA. A fatia do REGISTRO é
                        feita em cmed_extractor.py (_to_canonical_schema); o
                        "join" em si acontece no loader via UPDATE ... WHERE
                        numero_registro_anvisa = :chave (ver
                        postgres_loader.load_cmed_dataframe) — não precisa de
                        função de matching dedicada aqui.

    CMED   <-> RENAME : PRINCIPIO_ATIVO normalizado (normalizer.normalize_text)

CMED já está implementado (ver cmed_extractor.py); RENAME continua pendente."""
