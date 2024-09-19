import { Device } from "@/models";
import { Theme, useTheme } from "@/providers/ThemeProvider";
import { router } from "expo-router";
import {
  StyleSheet,
  Text,
  View,
  Pressable,
  PressableProps,
} from "react-native";

export type BaseTileProps = {
  device: Device;
  pressableProps?: PressableProps;
  children?: React.ReactNode;
};

export default function BaseTile({
  device,
  pressableProps = {},
  children,
}: BaseTileProps) {
  const theme = useTheme();
  const style = styles(theme);

  const _pressableProps: PressableProps = {
    onPress: () => router.push(`/devices/${device.id}`),
    ...pressableProps,
  };

  return (
    <Pressable {..._pressableProps} style={style.pressable}>
      <View style={style.container}>
        <Text style={style.name}>{device.name}</Text>
        {children}
      </View>
    </Pressable>
  );
}

const styles = (theme: Theme) => {
  const borderRadius = 30;

  return StyleSheet.create({
    pressable: {
      borderRadius,
    },
    container: {
      borderRadius,
      backgroundColor: theme.light,
      padding: 12,
      height: 85,
      width: 200,
    },
    name: {
      color: theme.primary,
      fontWeight: 700,
    },
  });
};
