import { Device } from "@/models";
import { Text } from "react-native";

type DeviceTileProps = {
  device: Device;
};

export default function DeviceTile({ device }: DeviceTileProps) {
  return <Text>{device.name}</Text>;
}
