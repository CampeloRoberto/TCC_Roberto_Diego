"""TODO: validação de campos obrigatórios antes da carga (ex.: nome_comercial
não vazio, numero_registro_anvisa com formato esperado). A fatia atual confia
na filtragem já feita em anvisa_extractor.py (SITUACAO_REGISTRO == "Ativo" e
NUMERO_REGISTRO_PRODUTO não nulo); um validator dedicado vale a pena quando
CMED/RENAME entrarem e os dados precisarem ser cruzados antes da carga."""
