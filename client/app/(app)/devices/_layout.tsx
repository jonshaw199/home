// app/devices/_layout.tsx
import { useRouteInfo } from "expo-router/build/hooks";
import { Stack } from "expo-router/stack";

export default function DevicesLayout() {
  const { segments } = useRouteInfo();

  return (
    <Stack screenOptions={{ headerShown: segments.length > 2 }}>
      <Stack.Screen name="index" options={{ title: "Device List" }} />
      <Stack.Screen name="[id]" options={{ title: "Device Details" }} />
    </Stack>
  );
}
