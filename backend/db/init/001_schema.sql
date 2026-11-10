-- Star Schema central do SUS Med.
-- Montado em /docker-entrypoint-initdb.d pelo docker-compose: roda automaticamente
-- na primeira subida do container (não reexecuta em subidas seguintes com volume já criado).

CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Dimensões
CREATE TABLE dim_principio_ativo (
    id               SERIAL PRIMARY KEY,
    dcb              VARCHAR(100),
    nome_normalizado VARCHAR(200) NOT NULL UNIQUE
);

CREATE TABLE dim_fabricante (
    id   SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL UNIQUE,
    cnpj VARCHAR(18)
);

CREATE TABLE dim_forma_farmaceutica (
    id        SERIAL PRIMARY KEY,
    descricao VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE dim_componente_sus (
    id   SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL UNIQUE  -- básico, estratégico, especializado
);

-- Tabela Fato Central
CREATE TABLE fato_medicamento (
    id                      BIGSERIAL PRIMARY KEY,
    numero_registro_anvisa  VARCHAR(20) UNIQUE,  -- necessário para upsert (ON CONFLICT) no loader
    ggrem                   VARCHAR(20),
    ean                     VARCHAR(14),
    nome_comercial          TEXT NOT NULL,
    concentracao            VARCHAR(100),
    tipo_medicamento        VARCHAR(20),   -- referência, genérico, similar
    situacao_registro       VARCHAR(30),
    preco_pf                NUMERIC(10, 2),
    preco_pmc               NUMERIC(10, 2),
    data_vigencia_preco     DATE,
    fk_principio_ativo      INT REFERENCES dim_principio_ativo (id),
    fk_fabricante           INT REFERENCES dim_fabricante (id),
    fk_forma_farmaceutica   INT REFERENCES dim_forma_farmaceutica (id),
    fk_componente_sus       INT REFERENCES dim_componente_sus (id),  -- NULL se não está no RENAME
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()  -- para delta sync mobile
);

-- Índices para busca fuzzy e full-text
CREATE INDEX idx_med_nome_trgm ON fato_medicamento
    USING GIN (nome_comercial gin_trgm_ops);

CREATE INDEX idx_med_fts ON fato_medicamento
    USING GIN (to_tsvector('portuguese', nome_comercial));

CREATE INDEX idx_med_ean     ON fato_medicamento (ean);
CREATE INDEX idx_med_updated ON fato_medicamento (updated_at);
