import BaseTile, { BaseTileProps } from "./BaseTile";
import { useAppSelector, useAppDispatch } from "@/store";
import { useMemo } from "react";
import { WS_SEND_MESSAGE } from "@/ws/websocketActionTypes";

const HANDLER_SHELLY_PLUG = "shellyplug__set";

export type PlugTileProps = Pick<BaseTileProps, "device">;

export default function PlugTile({ device }: PlugTileProps) {
  const dispatch = useAppDispatch();
  const plugs = useAppSelector((state) => state.plugs.data);

  const plug = useMemo(() => {
    if (device.plug && device.plug in plugs) {
      return plugs[device.plug];
    }
  }, [device, plugs]);

  const handlePress = () => {
    if (plug) {
      const message = {
        action: HANDLER_SHELLY_PLUG,
        body: {
          device_id: device.id,
          is_on: !plug.isOn,
        },
      };
      dispatch({
        type: WS_SEND_MESSAGE,
        payload: { message: JSON.stringify(message) },
      });
    } else {
      console.warn(`Plug not found for device ${device.id}`);
    }
  };

  return (
    <BaseTile device={device} pressableProps={{ onPress: handlePress }}>
      {plug?.isOn}
    </BaseTile>
  );
}
