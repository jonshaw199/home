import { Device } from "@/models";
import { Text } from "react-native";

export type DeviceDetailsProps = {
  device: Device;
};

export default function DeviceDetails({ device }: DeviceDetailsProps) {
  return <Text>Name: {device.name}</Text>;
}
