// Sketch do schema WatermelonDB (SQLite local), per Plano_Arquitetural.md.
// Ainda NÃO usado por nenhuma tela — a fatia atual (BuscaScreen) busca direto
// na API via src/services/api.ts. Isto fixa os nomes/colunas para quando o
// sync offline-first (src/database/sync.ts) for implementado de fato.
import { tableSchema } from "@nozbe/watermelondb";

export const medicamentoSchema = tableSchema({
  name: "medicamentos",
  columns: [
    { name: "nome_comercial", type: "string", isIndexed: true },
    { name: "principio_ativo", type: "string", isIndexed: true },
    { name: "ean", type: "string" },
    { name: "tipo", type: "string" }, // referência/genérico/similar
    { name: "preco_pmc", type: "number" },
    { name: "disponivel_sus", type: "boolean" },
    { name: "componente_sus", type: "string" },
    { name: "updated_at", type: "number" }, // timestamp para sync
  ],
});
