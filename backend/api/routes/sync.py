"""TODO: POST /sync/delta?since=<timestamp>&limit=500 — sync incremental para
o WatermelonDB do app (filtra fato_medicamento.updated_at > since). Não
registrado em api/main.py ainda: a fatia atual testa a tela de busca com fetch
direto (frontend/src/services/api.ts), sem passar pelo SQLite embarcado —
ver "Estado Atual da Implementação" em Plano_Arquitetural.md."""
