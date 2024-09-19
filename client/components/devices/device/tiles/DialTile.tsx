import { Device } from "@/models";
import BaseTile from "./BaseTile";
import { MaterialCommunityIcons } from "@expo/vector-icons";

export type DialTileProps = { device: Device };

export default function DialTile({ device }: DialTileProps) {
  return (
    <BaseTile
      device={device}
      icon={
        <MaterialCommunityIcons
          name="blur-radial"
          size={23}
          color="rgba(200, 100, 0, 0.9)"
        />
      }
      pressableProps={{ style: { backgroundColor: "rgba(255, 140, 0, 0.3)" } }}
      textProps={{ style: { color: "rgba(200, 100, 0, 1)" } }}
    />
  );
}
