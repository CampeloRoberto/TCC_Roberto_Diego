// Paleta do SUS Med: azul claro + branco + cruz vermelha (saúde).
// Mantida como tokens centralizados para não precisar retrabalho visual
// quando a interface for além de "apenas funcional".
export const theme = {
  colors: {
    primary: "#4FA8E0", // azul claro — cabeçalho, botão de busca, destaques
    primaryDark: "#2E7EB5",
    background: "#FFFFFF",
    surface: "#FFFFFF",
    border: "#D7E8F5",
    text: "#1A2B33",
    textMuted: "#5C7A8A",
    accent: "#D7263D", // vermelho — cruz de saúde, elementos de destaque pontuais
  },
  spacing: {
    sm: 8,
    md: 16,
    lg: 24,
  },
  radius: {
    sm: 6,
    md: 12,
  },
};
