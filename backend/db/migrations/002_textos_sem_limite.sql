-- Migração para bancos criados com a versão antiga do 001_schema.sql.
-- (O 001 só roda na primeira subida do container; quem já tem o volume
-- susmed_pgdata precisa aplicar esta migração uma vez.)
--
-- Motivo: VARCHAR(20) em tipo_medicamento e VARCHAR(200) em nome_normalizado
-- estouram com dados reais (categorias regulatórias longas, misturas de vários
-- princípios ativos). Um único valor longo derrubava a carga inteira.
--
-- Como aplicar (com o container rodando, dentro da pasta backend):
--   docker exec -i susmed_postgres psql -U susmed -d susmed < db/migrations/002_textos_sem_limite.sql

BEGIN;

ALTER TABLE dim_principio_ativo    ALTER COLUMN nome_normalizado TYPE TEXT;
ALTER TABLE dim_fabricante         ALTER COLUMN nome             TYPE TEXT;
ALTER TABLE dim_forma_farmaceutica ALTER COLUMN descricao        TYPE TEXT;
ALTER TABLE fato_medicamento       ALTER COLUMN tipo_medicamento TYPE TEXT;
ALTER TABLE fato_medicamento       ALTER COLUMN concentracao     TYPE TEXT;

-- Linha "nao informado" criada pela versão antiga do ETL: desfaz o vínculo
-- (vira NULL) e remove a linha, para esses produtos não aparecerem como
-- equivalentes entre si.
UPDATE fato_medicamento
   SET fk_principio_ativo = NULL, updated_at = NOW()
 WHERE fk_principio_ativo IN (SELECT id FROM dim_principio_ativo WHERE nome_normalizado = 'nao informado');
DELETE FROM dim_principio_ativo WHERE nome_normalizado = 'nao informado';

COMMIT;
