import { Device } from "@/models";
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

  return (
    <Pressable {...pressableProps} style={style.pressable}>
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
