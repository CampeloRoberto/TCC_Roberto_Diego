import { StatusBar } from "expo-status-bar";

import { BuscaScreen } from "./src/screens/BuscaScreen";

export default function App() {
  return (
    <>
      <BuscaScreen />
      <StatusBar style="dark" />
    </>
  );
}
