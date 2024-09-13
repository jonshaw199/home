import { Device } from "@/models";
import { useAppSelector } from "@/store";
import { StyleSheet, Text } from "react-native";

export type BaseTileProps = {
  device: Device;
};

export default function BaseTile({ device }: BaseTileProps) {
  const { deviceTypes } = useAppSelector((state) => ({
    deviceTypes: state.deviceTypes.data,
  }));

  const style = styles();

  return <Text style={style.container}>{device.name}</Text>;
}

const styles = () =>
  StyleSheet.create({
    container: {
      borderRadius: 30,
      backgroundColor: "lightgrey",
      padding: 15,
      height: 85,
      width: 200,
    },
  });
