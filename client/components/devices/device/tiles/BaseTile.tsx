import { Device } from "@/models";
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
  const style = styles();

  const _pressableProps: PressableProps = {
    onPress: () => router.push(`/devices/${device.id}`),
    ...pressableProps,
  };

  return (
    <Pressable {..._pressableProps} style={style.pressable}>
      <View style={style.container}>
        <Text>{device.name}</Text>
        {children}
      </View>
    </Pressable>
  );
}

const styles = () => {
  const borderRadius = 30;

  return StyleSheet.create({
    pressable: {
      borderRadius,
    },
    container: {
      borderRadius,
      backgroundColor: "lightgrey",
      padding: 15,
      height: 85,
      width: 200,
    },
  });
};
