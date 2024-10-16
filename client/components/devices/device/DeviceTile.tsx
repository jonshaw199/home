import { Device, DeviceTypes } from "@/models";
import DialTile from "./tiles/DialTile";
import BaseTile from "./tiles/BaseTile";
import PlugTile from "./tiles/PlugTile";
import EnvironmentalTile from "./tiles/EnvironmentalTile";
import PcTile from "./tiles/PcTile";
import { useMemo } from "react";
import LightTile from "./tiles/LightTile";
import { useAppSelector } from "@/store";

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

export default function DeviceTile({ device }: DeviceTileProps) {
  const deviceTypes = useAppSelector((state) => state.deviceTypes.data);

  return useMemo(() => {
    let C = BaseTile;

    if (device.deviceType in deviceTypes) {
      const deviceTypeName = deviceTypes[device.deviceType].name;
      if (deviceTypeName in tileMap) {
        C = tileMap[deviceTypeName as DeviceTypes];
      }
    }

    return <C device={device} />;
  }, [device, deviceTypes]);
}
