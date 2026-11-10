import { useState } from "react";
import { FlatList, SafeAreaView, StyleSheet, Text, View } from "react-native";

import { MedicamentoCard } from "../components/MedicamentoCard";
import { SearchBar } from "../components/SearchBar";
import { buscarMedicamentos, type MedicamentoBusca } from "../services/api";
import { theme } from "../theme";

export function BuscaScreen() {
  const [resultados, setResultados] = useState<MedicamentoBusca[]>([]);
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [buscou, setBuscou] = useState(false);

  async function handleSubmit(query: string) {
    if (query.trim().length < 2) {
      setErro("Digite ao menos 2 letras.");
      return;
    }
    setLoading(true);
    setErro(null);
    try {
      const dados = await buscarMedicamentos(query.trim());
      setResultados(dados);
      setBuscou(true);
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Erro ao buscar.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <SafeAreaView style={styles.container}>
      <SearchBar onSubmit={handleSubmit} loading={loading} />
      {erro ? <Text style={styles.erro}>{erro}</Text> : null}
      <FlatList
        data={resultados}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => <MedicamentoCard medicamento={item} />}
        contentContainerStyle={styles.lista}
        ListEmptyComponent={
          !loading && buscou
            ? () => <Text style={styles.vazio}>Nenhum medicamento encontrado.</Text>
            : undefined
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  lista: {
    paddingBottom: theme.spacing.lg,
  },
  erro: {
    color: theme.colors.accent,
    padding: theme.spacing.md,
  },
  vazio: {
    textAlign: "center",
    marginTop: theme.spacing.lg,
    color: theme.colors.textMuted,
  },
});
