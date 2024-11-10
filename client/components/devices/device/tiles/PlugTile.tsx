import BaseTile, { BaseTileProps } from "./BaseTile";
import { useAppSelector, useAppDispatch } from "@/store";
import { useMemo } from "react";
import { WS_SEND_MESSAGE } from "@/ws/websocketActionTypes";
import { plugSliceActions } from "@/store/slices/plugSlice";
import { Octicons } from "@expo/vector-icons";
import { selectSession } from "@/store/slices/sessionSlice";

const HANDLER_SHELLY_PLUG = "plug__set";

export type PlugTileProps = BaseTileProps;

export default function PlugTile({ device }: PlugTileProps) {
  const dispatch = useAppDispatch();
  const plugs = useAppSelector((state) => state.plugs.data);
  const { profile } = useAppSelector(selectSession);

  const plug = useMemo(() => {
    if (device.plug && device.plug in plugs) {
      return plugs[device.plug];
    }
  }, [device, plugs]);

  const handleLongPress = () => {
    if (plug) {
      const message = {
        src: profile,
        src_type: "profile",
        dest: `plugs/${device.id}/command`,
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
        onLongPress: handleLongPress,
        style: { backgroundColor: "rgba(220, 0, 0, 0.2)" },
      }}
      icon={<Octicons name="plug" size={20} color="rgba(220, 0, 0, 0.7)" />}
      status={plug?.isOn ? "On" : "Off"}
      textProps={{ style: { color: "rgba(220, 0, 0, 0.7)" } }}
    />
  );
}
