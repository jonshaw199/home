import WebSocketManager from "@/ws/WebSocketManager";
import BaseTile, { BaseTileProps } from "./BaseTile";
import { useAppSelector } from "@/store";
import { useMemo } from "react";

const HANDLER_SHELLY_PLUG = "shellyplug__set";

export type PlugTileProps = Pick<BaseTileProps, "device">;

export default function PlugTile({ device }: PlugTileProps) {
  const plugs = useAppSelector((state) => state.plugs.data);

  const plug = useMemo(() => {
    if (device.plug && device.plug in plugs) {
      return plugs[device.plug];
    }
  }, [device, plugs]);

  const handlePress = () => {
    if (plug) {
      const ws = WebSocketManager.getInstance();
      const msg = {
        action: HANDLER_SHELLY_PLUG,
        body: {
          device_id: device.id,
          is_on: !plug.isOn,
        },
      };

      try {
        ws.sendMessage(JSON.stringify(msg));
      } catch (e) {
        console.error("Error when sending Plug message", e);
      }
    } else {
      console.warn(`Plug not found for device ${device.id}`);
    }
  };

  return <BaseTile device={device} pressableProps={{ onPress: handlePress }} />;
}
