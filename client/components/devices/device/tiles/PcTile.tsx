import { Device } from "@/models";
import BaseTile from "./BaseTile";
import { Entypo } from "@expo/vector-icons";

export type PcTileProps = { device: Device };

export default function PcTile({ device }: PcTileProps) {
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
      pressableProps={{ style: { backgroundColor: "rgba(0, 255, 129, 0.3)" } }}
      textProps={{ style: { color: "rgba(0, 175, 100, 1)" } }}
    />
  );
}
