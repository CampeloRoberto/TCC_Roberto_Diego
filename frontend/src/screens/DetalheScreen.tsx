import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import { useEffect, useState } from "react";
import { ActivityIndicator, FlatList, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import type { RootStackParamList } from "../../App";
import {
  buscarDetalhe,
  buscarEquivalencias,
  type Equivalente,
  type MedicamentoDetalhe,
} from "../services/api";
import { theme } from "../theme";

type Props = NativeStackScreenProps<RootStackParamList, "Detalhe">;

export function DetalheScreen({ route }: Props) {
  const { id } = route.params;
  const [medicamento, setMedicamento] = useState<MedicamentoDetalhe | null>(null);
  const [equivalentes, setEquivalentes] = useState<Equivalente[]>([]);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    let cancelado = false;
    setLoading(true);
    setErro(null);
    Promise.all([buscarDetalhe(id), buscarEquivalencias(id)])
      .then(([detalhe, equivalencias]) => {
        if (cancelado) return;
        setMedicamento(detalhe);
        setEquivalentes(equivalencias.equivalentes);
      })
      .catch((e) => {
        if (cancelado) return;
        setErro(e instanceof Error ? e.message : "Erro ao carregar.");
      })
      .finally(() => {
        if (!cancelado) setLoading(false);
      });
    return () => {
      cancelado = true;
    };
  }, [id]);

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <ActivityIndicator style={styles.carregando} color={theme.colors.primaryDark} />
      </SafeAreaView>
    );
  }

  if (erro || !medicamento) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.erro}>{erro ?? "Medicamento não encontrado."}</Text>
      </SafeAreaView>
    );
  }

  const maisBaratoId = equivalentes.find((e) => e.preco_pmc != null)?.id;

  return (
    <SafeAreaView style={styles.container}>
      <FlatList
        data={equivalentes}
        keyExtractor={(item) => String(item.id)}
        ListHeaderComponent={
          <View style={styles.cabecalho}>
            <Text style={styles.nome}>{medicamento.nome_comercial}</Text>
            {medicamento.principio_ativo ? (
              <Text style={styles.linha}>Princípio ativo: {medicamento.principio_ativo}</Text>
            ) : null}
            {medicamento.fabricante ? <Text style={styles.linha}>Fabricante: {medicamento.fabricante}</Text> : null}
            {medicamento.tipo_medicamento ? <Text style={styles.tipo}>{medicamento.tipo_medicamento}</Text> : null}

            {medicamento.preco_pmc != null ? (
              <>
                <Text style={styles.preco}>R$ {medicamento.preco_pmc.toFixed(2)}</Text>
                <Text style={styles.legenda}>
                  Preço de referência CMED (alíquota padrão 18% ICMS) — pode variar por estado/farmácia.
                </Text>
              </>
            ) : (
              <Text style={styles.legenda}>Preço não disponível para este medicamento.</Text>
            )}

            {equivalentes.length > 0 ? <Text style={styles.subtitulo}>Equivalentes (mesmo princípio ativo)</Text> : null}
          </View>
        }
        renderItem={({ item }) => (
          <View style={styles.equivalenteCard}>
            <View style={styles.equivalenteHeader}>
              <Text style={styles.equivalenteNome}>{item.nome_comercial}</Text>
              {item.id === maisBaratoId ? (
                <Text style={styles.badgeMaisBarato}>MAIS BARATO</Text>
              ) : null}
            </View>
            {item.fabricante ? <Text style={styles.linha}>{item.fabricante}</Text> : null}
            <View style={styles.rodape}>
              {item.tipo_medicamento ? <Text style={styles.tipo}>{item.tipo_medicamento}</Text> : null}
              {item.preco_pmc != null ? (
                <Text style={styles.preco}>R$ {item.preco_pmc.toFixed(2)}</Text>
              ) : (
                <Text style={styles.legenda}>sem preço</Text>
              )}
            </View>
          </View>
        )}
        ListEmptyComponent={
          <Text style={styles.legenda}>Nenhum equivalente encontrado para este princípio ativo.</Text>
        }
        contentContainerStyle={styles.lista}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  carregando: {
    marginTop: theme.spacing.lg,
  },
  erro: {
    color: theme.colors.accent,
    padding: theme.spacing.md,
  },
  lista: {
    paddingBottom: theme.spacing.lg,
  },
  cabecalho: {
    padding: theme.spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
    marginBottom: theme.spacing.sm,
  },
  nome: {
    fontSize: 20,
    fontWeight: "700",
    color: theme.colors.text,
  },
  linha: {
    marginTop: 4,
    color: theme.colors.textMuted,
  },
  tipo: {
    marginTop: theme.spacing.sm,
    alignSelf: "flex-start",
    backgroundColor: theme.colors.border,
    color: theme.colors.primaryDark,
    fontSize: 12,
    fontWeight: "600",
    textTransform: "uppercase",
    paddingHorizontal: theme.spacing.sm,
    paddingVertical: 2,
    borderRadius: theme.radius.sm,
  },
  preco: {
    marginTop: theme.spacing.sm,
    fontSize: 22,
    fontWeight: "700",
    color: theme.colors.primaryDark,
  },
  legenda: {
    marginTop: 4,
    fontSize: 12,
    color: theme.colors.textMuted,
  },
  subtitulo: {
    marginTop: theme.spacing.lg,
    fontSize: 14,
    fontWeight: "700",
    color: theme.colors.text,
    textTransform: "uppercase",
  },
  equivalenteCard: {
    backgroundColor: theme.colors.surface,
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.radius.md,
    padding: theme.spacing.md,
    marginHorizontal: theme.spacing.md,
    marginTop: theme.spacing.sm,
  },
  equivalenteHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  equivalenteNome: {
    fontSize: 15,
    fontWeight: "700",
    color: theme.colors.text,
  },
  badgeMaisBarato: {
    fontSize: 10,
    fontWeight: "700",
    color: theme.colors.background,
    backgroundColor: theme.colors.accent,
    paddingHorizontal: theme.spacing.sm,
    paddingVertical: 2,
    borderRadius: theme.radius.sm,
  },
  rodape: {
    marginTop: theme.spacing.sm,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
});
