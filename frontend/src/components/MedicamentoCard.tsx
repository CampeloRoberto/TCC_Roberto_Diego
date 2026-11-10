import { StyleSheet, Text, View } from "react-native";

import { theme } from "../theme";
import type { MedicamentoBusca } from "../services/api";

type Props = {
  medicamento: MedicamentoBusca;
};

export function MedicamentoCard({ medicamento }: Props) {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.cross} />
        <Text style={styles.nome}>{medicamento.nome_comercial}</Text>
      </View>
      {medicamento.principio_ativo ? (
        <Text style={styles.linha}>Princípio ativo: {medicamento.principio_ativo}</Text>
      ) : null}
      {medicamento.fabricante ? (
        <Text style={styles.linha}>Fabricante: {medicamento.fabricante}</Text>
      ) : null}
      {medicamento.tipo_medicamento ? (
        <Text style={styles.tipo}>{medicamento.tipo_medicamento}</Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: theme.colors.surface,
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.radius.md,
    padding: theme.spacing.md,
    marginHorizontal: theme.spacing.md,
    marginTop: theme.spacing.sm,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    gap: theme.spacing.sm,
  },
  cross: {
    width: 10,
    height: 10,
    backgroundColor: theme.colors.accent,
    borderRadius: 2,
  },
  nome: {
    fontSize: 16,
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
});
