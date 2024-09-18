import BaseTile, { BaseTileProps } from "./BaseTile";
import { useAppSelector, useAppDispatch } from "@/store";
import { useMemo } from "react";
import { WS_SEND_MESSAGE } from "@/ws/websocketActionTypes";
import { plugSliceActions } from "@/store/slices/plugSlice";
import { Text } from "react-native";
import { router } from "expo-router";

const HANDLER_SHELLY_PLUG = "shellyplug__set";

export type PlugTileProps = BaseTileProps;

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
      // Send message
      dispatch({
        type: WS_SEND_MESSAGE,
        payload: { message: JSON.stringify(message) },
      });
      // Update state optimistically
      dispatch(
        plugSliceActions.updateResourceField({
          id: plug.id,
          field: "isOn",
          value: message.body.is_on,
        })
      );
    } else {
      console.warn(`Plug not found for device ${device.id}`);
    }
  };

  return (
    <BaseTile
      device={device}
      pressableProps={{
        onPress: handlePress,
        onLongPress: () => router.push(`./${device.id}`),
      }}
    >
      <Text>{plug?.isOn ? "On" : "Off"}</Text>
    </BaseTile>
  );
}
