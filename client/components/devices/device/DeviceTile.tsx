import { Device, DeviceTypes } from "@/models";
import DialTile from "./tiles/DialTile";
import BaseTile from "./tiles/BaseTile";
import PlugTile from "./tiles/PlugTile";
import EnvironmentalTile from "./tiles/EnvironmentalTile";
import PcTile from "./tiles/PcTile";
import { useMemo } from "react";
import LightTile from "./tiles/LightTile";

type DeviceTileProps = {
  device: Device;
};

const tileMap = {
  [DeviceTypes.DIAL]: DialTile,
  [DeviceTypes.PC]: PcTile,
  [DeviceTypes.ENVIRONMENTAL]: EnvironmentalTile,
  [DeviceTypes.PLUG]: PlugTile,
  [DeviceTypes.LIGHT]: LightTile,
};

const getDeviceTile = ({ device }: { device: Device }) => {
  if (device.deviceType in tileMap) {
    const C = tileMap[device.deviceType as DeviceTypes];
    return <C device={device} />;
  }
  return <BaseTile device={device} />;
};

export default function DeviceTile({ device }: DeviceTileProps) {
  return useMemo(() => getDeviceTile({ device }), [device]);
}
