// app/devices/_layout.tsx
import { Theme, useTheme } from "@/providers/ThemeProvider";
import { useRouteInfo } from "expo-router/build/hooks";
import { Stack } from "expo-router/stack";
import { StyleSheet } from "react-native";

export default function DevicesLayout() {
  const theme = useTheme();
  const style = styles(theme);
  const { segments } = useRouteInfo();

  return (
    <Stack
      screenOptions={{
        headerShown: segments.length > 2,
        headerStyle: style.stackHeader,
      }}
    >
      <Stack.Screen name="index" options={{ title: "Device List" }} />
      <Stack.Screen name="[id]" options={{ title: "Device Details" }} />
    </Stack>
  );
}

const styles = (theme: Theme) =>
  StyleSheet.create({
    stackHeader: {
      backgroundColor: theme.light,
    },
  });