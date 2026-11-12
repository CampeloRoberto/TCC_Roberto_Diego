import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider } from "react-native-safe-area-context";

import { BuscaScreen } from "./src/screens/BuscaScreen";
import { DetalheScreen } from "./src/screens/DetalheScreen";
import { theme } from "./src/theme";

export type RootStackParamList = {
  Busca: undefined;
  Detalhe: { id: number };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Stack.Navigator
          screenOptions={{
            headerStyle: { backgroundColor: theme.colors.primary },
            headerTintColor: theme.colors.background,
          }}
        >
          <Stack.Screen name="Busca" component={BuscaScreen} options={{ title: "SUS Med" }} />
          <Stack.Screen name="Detalhe" component={DetalheScreen} options={{ title: "Detalhe" }} />
        </Stack.Navigator>
      </NavigationContainer>
      <StatusBar style="dark" />
    </SafeAreaProvider>
  );
}
