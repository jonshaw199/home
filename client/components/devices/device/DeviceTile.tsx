import { Device, DeviceTypes } from "@/models";
import DialTile from "./tiles/DialTile";
import BaseTile from "./tiles/BaseTile";

type DeviceTileProps = {
  device: Device;
};

export default function DeviceTile({ device }: DeviceTileProps) {
  switch (device.deviceType) {
    case DeviceTypes.DIAL:
      return <DialTile device={device} />;
    default:
      return <BaseTile device={device} />;
  }
}
