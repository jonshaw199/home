import ColorPicker from "@/components/lib/ColorPicker";
import { Device } from "@/models";
import { useAppDispatch } from "@/store";
import { lightSliceActions } from "@/store/slices/lightSlice";
import { WS_SEND_MESSAGE } from "@/ws/websocketActionTypes";
import { useState } from "react";

const ACTION_LIGHT_SET = "light__set";

type LightDetailsProps = {
  device: Device;
};

export default function LightDetails({ device }: LightDetailsProps) {
  const [color, setColor] = useState<string>();
  const dispatch = useAppDispatch();

  const sendColorMsg = (hex: string) => {
    if (!device.light)
      return console.error("Unable to send color message; light undefined");

    const message = {
      action: ACTION_LIGHT_SET,
      body: {
        device_id: device.id,
        color: hex,
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
        id: device.light,
        field: "color",
        value: message.body.color,
      })
    );
  };

  const handleColorChange = (hex: string) => {
    console.info(`Set color: ${hex}`);
    setColor(hex);
    sendColorMsg(hex);
  };

  return <ColorPicker initialColor={color} onChange={handleColorChange} />;
}
