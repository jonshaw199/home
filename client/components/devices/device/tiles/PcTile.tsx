import { Device } from "@/models";
import BaseTile from "./BaseTile";
import { Entypo } from "@expo/vector-icons";
import { useMemo } from "react";
import { useAppSelector } from "@/store";

export type PcTileProps = { device: Device };

export default function PcTile({ device }: PcTileProps) {
  const systems = useAppSelector((state) => state.systems.data);

  const system = useMemo(() => {
    if (device.system && device.system in systems) {
      return systems[device.system];
    }
  }, [device, systems]);

  const cpuUsage = useMemo(() => {
    if (system?.cpuUsage != null) {
      return `CPU ${Math.floor(system.cpuUsage)}%`;
    }
  }, [system]);

  const memUsage = useMemo(() => {
    if (system?.memUsage != null) {
      return `RAM ${Math.floor(system.memUsage)}%`;
    }
  }, [system]);

  return (
    <BaseTile
      device={device}
      icon={
        <Entypo
          name="classic-computer"
          size={22}
          color="rgba(0, 200, 100, 0.9)"
        />
      }
      status={[cpuUsage, memUsage].join(" ")}
      pressableProps={{ style: { backgroundColor: "rgba(0, 255, 129, 0.3)" } }}
      textProps={{ style: { color: "rgba(0, 175, 100, 1)" } }}
    />
  );
}
