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

## Estratégia de Atualização de Dados

| Fonte | Cadência real | Mecanismo no pipeline |
|-------|---------------|------------------------|
| ANVISA (produtos registrados) | Mensal (dado fechado no último dia do mês anterior) | ETL automatizável; disparo manual por enquanto |
| CMED (lista de preços PMVG/PF/PMC) | Mensal | ETL automatizável; mesmo ciclo do ANVISA |
| RENAME | Irregular, orientada a evento (nova edição via Portaria GM/MS, ex.: RENAME 2022 → RENAME 2024) | Disparo manual separado, sem cron |

O orquestrador do ETL roda ANVISA + CMED no mesmo ciclo mensal (quando automatizado); RENAME fica fora desse ciclo, disparada manualmente sempre que uma nova Portaria for publicada. Por enquanto, todo o pipeline é disparado manualmente (`--run-now`); o modo agendado (`schedule`) já está previsto no orquestrador para ser ligado depois, sem reescrita.

## Ambiente de Desenvolvimento e Distribuição

Por ora, tudo roda local: PostgreSQL via `docker-compose`, API FastAPI em `localhost`, ETL disparado manualmente. A migração para uma nuvem free-tier (Render/Railway/Supabase) fica para quando o projeto estiver mais maduro.

A distribuição de versões de teste do app usa build via Expo/EAS com link direto (internal distribution), sem restrição por e-mail por enquanto. Importante: como o backend é local, um build distribuído a testadores fora da rede local não consegue alcançar a API — será necessário expor a API via túnel (ngrok/Cloudflare Tunnel) durante a sessão de teste, ou já ter feito o deploy em nuvem antes de distribuir o link.

## Como Rodar o Projeto

### Pré-requisitos

- **Python 3.11+**
- **Docker Desktop** (com o backend WSL2 habilitado, no Windows) — usado só para rodar o PostgreSQL local
- **Node.js 18+** e **npm**
- **Expo Go** instalado no celular (Android/iOS), ou um emulador Android / simulador iOS configurado

### Backend (ETL + API)

```bash
cd backend

# 1. Variáveis de ambiente
cp .env.example .env

# 2. PostgreSQL local (cria o schema automaticamente na primeira subida,
#    via backend/db/init/001_schema.sql)
docker-compose up -d
docker-compose ps                # confirmar que o container está "healthy"/"Up"

# 3. Ambiente Python
python -m venv .venv
.venv\Scripts\activate           # Windows (PowerShell/cmd)
# source .venv/bin/activate      # Linux/macOS
pip install -r requirements.txt

# 4. Rodar o ETL
python -m pipeline.orchestrator --run-now --sample   # fixture local, determinístico — rode esse primeiro
python -m pipeline.orchestrator --run-now             # baixa o CSV real da ANVISA e carrega no Postgres

# 5. Subir a API
uvicorn api.main:app --reload --port 8000
```

Com a API no ar, confirme em outro terminal:

```bash
curl http://localhost:8000/health
curl "http://localhost:8000/medicamentos/busca?q=dipirona"
```

Ou abra `http://localhost:8000/docs` no navegador (Swagger).

### Frontend (App Mobile)

```bash
cd frontend

# 1. Variáveis de ambiente
cp .env.example .env
# edite EXPO_PUBLIC_API_BASE_URL em .env conforme onde o app vai rodar:
#   - Emulador Android -> http://10.0.2.2:8000
#   - Simulador iOS    -> http://localhost:8000 (funciona direto)
#   - Celular físico (Expo Go) -> http://<IP-da-sua-máquina-na-rede>:8000 (mesma Wi-Fi do backend)

# 2. Instalar dependências
npm install

# 3. Rodar
npx expo start
```

Escaneie o QR code com o app Expo Go (Android) ou a câmera (iOS), ou pressione `a`/`i` no terminal para abrir num emulador/simulador já configurado. Digite um termo (ex.: "dipirona") na tela de busca para ver resultados vindos do backend local.

### Solução de problemas comuns

- **`docker-compose up` trava ou dá erro de conexão com a API do Docker**: normalmente é o Docker Desktop ainda inicializando no Windows (o backend WSL2 demora para subir após abrir o app, ou após o PC reiniciar). Confirme com `docker info`; se continuar falhando, rode `wsl --update` e reinicie o Docker Desktop.
- **App não consegue buscar nada / erro de rede**: confira se `EXPO_PUBLIC_API_BASE_URL` em `frontend/.env` está certo para o jeito que você está rodando o app (emulador vs. dispositivo físico vs. simulador — ver tabela acima).

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
