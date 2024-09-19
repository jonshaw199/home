import { useAppSelector } from "@/store";
import BaseTile from "./BaseTile";
import { useMemo } from "react";
import { FontAwesome6 } from "@expo/vector-icons";
import { Device } from "@/models";

export type EnvironmentalTileProps = {
  device: Device;
};

export default function EnvironmentalTile({ device }: EnvironmentalTileProps) {
  const environmentals = useAppSelector((state) => state.environmentals.data);

  const environmental = useMemo(() => {
    if (device.environmental && device.environmental in environmentals) {
      return environmentals[device.environmental];
    }
  }, [device, environmentals]);

  const temp = useMemo(() => {
    if (environmental?.temperatureF != undefined) {
      return `${environmental.temperatureF}°F`;
    }
  }, [environmental]);

  const humidity = useMemo(() => {
    if (environmental?.humidity != undefined) {
      return `${environmental.humidity}%`;
    }
  }, [environmental]);

  return (
    <BaseTile
      device={device}
      icon={
        <FontAwesome6
          name="temperature-half"
          size={22}
          color="rgba(0, 120, 240, 0.8)"
        />
      }
      status={[temp, humidity].join(" - ")}
      pressableProps={{ style: { backgroundColor: "rgba(0, 120, 240, 0.25)" } }}
      textProps={{ style: { color: "rgba(0, 120, 240, 0.8)" } }}
    />
  );
}
