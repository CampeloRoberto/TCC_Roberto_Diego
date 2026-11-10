"""TODO: deduplicação entre fontes (ex.: mesma apresentação listada por ANVISA
e CMED com grafias diferentes) usando EAN/GGREM como chave primária e nome
normalizado como fallback. Não necessário enquanto só ANVISA está implementado
— a deduplicação *dentro* da própria base ANVISA (múltiplos processos por
registro) já é feita em extractors/anvisa_extractor.py."""
