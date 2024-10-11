import BaseTile, { BaseTileProps } from "./BaseTile";
import { useAppSelector, useAppDispatch } from "@/store";
import { useMemo } from "react";
import { WS_SEND_MESSAGE } from "@/ws/websocketActionTypes";
import { plugSliceActions } from "@/store/slices/plugSlice";
import { Octicons } from "@expo/vector-icons";

const ACTION_LIGHT_SET_COLOR = "light__set_color";
const ACTION_LIGHT_SET_BRIGHTNESS = "light__set_brightness";

export type LightTileProps = BaseTileProps;

export default function LightTile({ device }: LightTileProps) {
  const dispatch = useAppDispatch();
  const lights = useAppSelector((state) => state.lights.data); // TODO

  const light = useMemo(() => {
    if (device.light && device.light in lights) {
      return lights[device.light];
    }
  }, [device, lights]);

  const handleLongPress = () => {
    if (light) {
      /*
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
      */
    } else {
      console.warn(`Light not found for device ${device.id}`);
    }
  };

  return (
    <BaseTile
      device={device}
      pressableProps={{
        onLongPress: handleLongPress,
        style: { backgroundColor: "rgba(220, 0, 0, 0.2)" },
      }}
      icon={
        <Octicons name="light-bulb" size={20} color="rgba(220, 0, 0, 0.8)" />
      }
      //status={light?.isOn ? "On" : "Off"}
      textProps={{ style: { color: "rgba(220, 0, 0, 0.7)" } }}
    />
  );
}
