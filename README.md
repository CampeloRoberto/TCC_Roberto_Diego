# SUS Med — Sistema Integrado de Consulta de Medicamentos do SUS

## Sobre o Projeto

O presente trabalho consiste no desenvolvimento de um sistema de software integrado — composto por um pipeline de engenharia de dados (backend) e um aplicativo móvel multiplataforma (frontend) — projetado para unificar e otimizar a consulta de medicamentos distribuídos pelo Sistema Único de Saúde (SUS) e seus respectivos equivalentes genéricos e similares autorizados pela ANVISA. O projeto abordará o desafio técnico de extrair, tratar e cruzar dados de bases públicas heterogêneas e frequentemente fragmentadas (ANVISA, CMED e RENAME/DATASUS). Como resultado final, espera-se entregar uma aplicação mobile funcional que opere sob o paradigma offline-first, garantindo que profissionais de saúde e cidadãos realizem buscas indexadas instantâneas por princípios ativos e nomes comerciais, mesmo em ambientes hospitalares ou regiões com severas restrições de conectividade à internet.

## Objetivo Geral

Desenvolver e avaliar um sistema computacional composto por um pipeline de engenharia de dados e um aplicativo móvel baseado em uma arquitetura de persistência local, voltado para a consolidação, cruzamento e consulta otimizada de dados de assistência farmacêutica pública e regulamentação de medicamentos no Brasil.

## Objetivos Específicos

- **ETL Automatizado**: Construir um pipeline automatizado de ETL (Extração, Transformação e Carga) utilizando scripts isolados para coletar, higienizar e padronizar os dados brutos oriundos dos portais de Dados Abertos da ANVISA, da lista de conformidade da CMED e do catálogo da RENAME.

- **Modelagem Dimensional**: Modelar e implementar um banco de dados relacional centralizado utilizando o conceito de Modelagem Dimensional (Esquema Estrela / Star Schema) para mapear com alta performance as relações de equivalência entre medicamentos de referência, genéricos e as regras de distribuição do SUS.

- **Aplicação Mobile**: Desenvolver a aplicação móvel multiplataforma utilizando o framework React Native com TypeScript, aplicando padrões modernos de engenharia de software, componentização e gerenciamento de estado.

- **Offline-First**: Implementar e validar uma camada de persistência local offline-first por meio de um banco de dados embarcado eficiente (SQLite), integrando um algoritmo de sincronização incremental periódica de dados.

## Fontes de Dados

| Fonte | Descrição | Link |
|-------|-----------|------|
| RENAME | Relação Nacional de Medicamentos Essenciais | https://www.gov.br/saude/pt-br/composicao/sectics/rename |
| ANVISA | Agência Nacional de Vigilância Sanitária — Dados Abertos | https://dados.gov.br/dados/organizacoes/visualizar/agencia-nacional-de-vigilancia-sanitaria-anvisa |
| CMED | Câmara de Regulação do Mercado de Medicamentos — Preços | https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/cmed/precos |

## Stack Tecnológica

### Backend / Pipeline ETL
- **Linguagem**: Python 3.11+
- **ETL**: Pandas, openpyxl, pdfplumber, requests
- **Banco de Dados**: PostgreSQL 15+ (com extensão `pg_trgm` para busca fuzzy)
- **ORM**: SQLAlchemy 2.x
- **API REST**: FastAPI

### Frontend / Mobile
- **Framework**: React Native com Expo
- **Linguagem**: TypeScript
- **Banco Local**: SQLite via WatermelonDB (offline-first)

## Estrutura do Repositório

```
tcc-medicamentos-sus/
├── backend/          ← Pipeline ETL + API FastAPI
├── frontend/         ← Aplicativo React Native
├── README.md
└── .gitignore
```

## Autores

Trabalho de Conclusão de Curso — Sistemas de Informação / Ciência da Computação
