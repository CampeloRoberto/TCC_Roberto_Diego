import { API_BASE_URL } from "../config";

export type MedicamentoBusca = {
  id: number;
  nome_comercial: string;
  principio_ativo: string | null;
  fabricante: string | null;
  tipo_medicamento: string | null;
  situacao_registro: string | null;
};

type BuscaResponse = {
  total: number;
  resultados: MedicamentoBusca[];
};

export async function buscarMedicamentos(q: string): Promise<MedicamentoBusca[]> {
  const url = `${API_BASE_URL}/medicamentos/busca?q=${encodeURIComponent(q)}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Busca falhou (${response.status})`);
  }
  const data: BuscaResponse = await response.json();
  return data.resultados;
}
