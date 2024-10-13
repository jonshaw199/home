import { Device } from "@/models";
import { Theme, useTheme } from "@/providers/ThemeProvider";
import { MaterialIcons } from "@expo/vector-icons";
import { router } from "expo-router";
import { ReactNode, useMemo } from "react";
import {
  StyleSheet,
  Text,
  View,
  Pressable,
  PressableProps,
  TextProps,
} from "react-native";

export type BaseTileProps = {
  device: Device;
  icon?: ReactNode;
  pressableProps?: PressableProps;
  textProps?: TextProps;
  status?: string;
};

export default function BaseTile({
  device,
  icon,
  pressableProps = {},
  textProps = {},
  status,
}: BaseTileProps) {
  const theme = useTheme();
  const style = styles(theme);

  const pressableStyleProp = useMemo(() => {
    if (pressableProps.style) {
      if (typeof pressableProps.style == "function") {
        return pressableProps.style({ pressed: false });
      } else {
        return pressableProps.style;
      }
    }
  }, [pressableProps]);

  const _pressableProps: PressableProps = useMemo(
    () => ({
      onPress: () => router.push(`/devices/${device.id}`),
      //style: [style.pressable, pressableStyleProp],
      ...pressableProps,
    }),
    [device, style, pressableStyleProp, theme, pressableProps]
  );

  return (
    <Pressable
      {..._pressableProps}
      style={[style.pressable, pressableStyleProp]}
    >
      {icon || <MaterialIcons name="device-unknown" size={22} />}
      <View style={style.body}>
        <Text {...textProps} style={[style.name, textProps.style]}>
          {device.name}
        </Text>
        <Text {...textProps} style={[style.status, textProps.style]}>
          {status || " "}
        </Text>
      </View>
    </Pressable>
  );
}

const styles = (theme: Theme) => {
  return StyleSheet.create({
    pressable: {
      borderRadius: 30,
      backgroundColor: "rgba(0, 120, 240, 0.2)",
      height: 85,
      width: 220,
      display: "flex",
      flexDirection: "row",
      gap: 10,
      alignItems: "center",
      padding: 20,
      userSelect: "none",
    },
    body: {
      display: "flex",
      flexDirection: "column",
      gap: 1,
      width: "100%",
    },
    name: {
      fontWeight: 700,
      fontSize: 14,
      color: theme.dark,
    },
    status: {
      fontSize: 14,
      color: theme.dark,
    },
  });
};
