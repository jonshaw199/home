import BaseTile, { BaseTileProps } from "./BaseTile";
import { useAppSelector, useAppDispatch } from "@/store";
import { useMemo } from "react";
import { WS_SEND_MESSAGE } from "@/ws/websocketActionTypes";
import { Octicons } from "@expo/vector-icons";
import { lightSliceActions } from "@/store/slices/lightSlice";

const ACTION_LIGHT_SET = "light__set";

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
      const message = {
        action: ACTION_LIGHT_SET,
        body: {
          device_id: device.id,
          is_on: !light.isOn,
        },
      };
      // Send message
      dispatch({
        type: WS_SEND_MESSAGE,
        payload: { message: JSON.stringify(message) },
      });
      // Update state optimistically
      dispatch(
        lightSliceActions.updateResourceField({
          id: light.id,
          field: "isOn",
          value: message.body.is_on,
        })
      );
    } else {
      console.warn(`Light not found for device ${device.id}`);
    }
  };

  return (
    <BaseTile
      device={device}
      pressableProps={{
        onLongPress: handleLongPress,
        style: { backgroundColor: "rgba(0, 250, 250, 0.3)" },
      }}
      icon={
        <Octicons name="light-bulb" size={20} color="rgba(0, 125, 125, 0.8)" />
      }
      status={light?.isOn ? "On" : "Off"}
      textProps={{ style: { color: "rgba(0, 125, 125, 0.8)" } }}
    />
  );
}
