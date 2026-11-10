import { useState } from "react";
import { StyleSheet, TextInput, TouchableOpacity, Text, View } from "react-native";

import { theme } from "../theme";

type Props = {
  onSubmit: (query: string) => void;
  loading?: boolean;
};

export function SearchBar({ onSubmit, loading }: Props) {
  const [value, setValue] = useState("");

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        placeholder="Buscar medicamento (ex.: dipirona)"
        placeholderTextColor={theme.colors.textMuted}
        value={value}
        onChangeText={setValue}
        onSubmitEditing={() => onSubmit(value)}
        autoCapitalize="none"
        autoCorrect={false}
        returnKeyType="search"
      />
      <TouchableOpacity
        style={styles.button}
        onPress={() => onSubmit(value)}
        disabled={loading}
      >
        <Text style={styles.buttonText}>{loading ? "..." : "Buscar"}</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    gap: theme.spacing.sm,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.primary,
  },
  input: {
    flex: 1,
    backgroundColor: theme.colors.background,
    borderRadius: theme.radius.sm,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: 10,
    color: theme.colors.text,
  },
  button: {
    backgroundColor: theme.colors.primaryDark,
    borderRadius: theme.radius.sm,
    paddingHorizontal: theme.spacing.md,
    justifyContent: "center",
  },
  buttonText: {
    color: theme.colors.background,
    fontWeight: "600",
  },
});
