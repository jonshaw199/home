import { Device, DeviceTypes } from "@/models";
import DialTile from "./tiles/DialTile";
import BaseTile from "./tiles/BaseTile";
import PlugTile from "./tiles/PlugTile";

type DeviceTileProps = {
  device: Device;
};

export default function DeviceTile({ device }: DeviceTileProps) {
  switch (device.deviceType) {
    case DeviceTypes.DIAL:
      return <DialTile device={device} />;
    case DeviceTypes.SMART_PLUG:
      return <PlugTile device={device} />;
    default:
      return <BaseTile device={device} />;
  }
}
