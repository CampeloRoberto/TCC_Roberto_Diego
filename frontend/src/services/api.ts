import { API_BASE_URL } from "../config";

export type MedicamentoBusca = {
  id: number;
  nome_comercial: string;
  principio_ativo: string | null;
  fabricante: string | null;
  tipo_medicamento: string | null;
  situacao_registro: string | null;
  // Preço de referência CMED (PMC, alíquota padrão 18% ICMS) — teto nacional
  // por apresentação, não o preço de uma farmácia específica.
  preco_pmc: number | null;
};

export type MedicamentoDetalhe = MedicamentoBusca & {
  preco_pf: number | null;
  data_vigencia_preco: string | null;
  ean: string | null;
  concentracao: string | null;
};

export type Equivalente = {
  id: number;
  nome_comercial: string;
  fabricante: string | null;
  tipo_medicamento: string | null;
  preco_pmc: number | null;
};

export type EquivalenciasResponse = {
  principio_ativo: string | null;
  total: number;
  equivalentes: Equivalente[];
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

export async function buscarDetalhe(id: number): Promise<MedicamentoDetalhe> {
  const response = await fetch(`${API_BASE_URL}/medicamentos/${id}`);
  if (!response.ok) {
    throw new Error(`Detalhe falhou (${response.status})`);
  }
  return response.json();
}

export async function buscarEquivalencias(id: number): Promise<EquivalenciasResponse> {
  const response = await fetch(`${API_BASE_URL}/medicamentos/${id}/equivalencias`);
  if (!response.ok) {
    throw new Error(`Equivalências falhou (${response.status})`);
  }
  return response.json();
}
