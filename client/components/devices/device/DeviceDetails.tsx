import { Device } from "@/models";
import { Text } from "react-native";
import LightDetails from "./details/LightDetails";
import { Card } from "@rneui/themed";

export type DeviceDetailsProps = {
  device: Device;
};

export default function DeviceDetails({ device }: DeviceDetailsProps) {
  return (
    <>
      <Card>
        <Card.Title>General Settings</Card.Title>
        <Text>ID: {device.id}</Text>
        <Text>Name: {device.name}</Text>
        <Text>Last Status Update: {device.lastStatusUpdate || "Never"}</Text>
      </Card>

      {device.light && (
        <Card>
          <Card.Title>Light Settings</Card.Title>
          <LightDetails device={device} />
        </Card>
      )}
    </>
  );
}
