import ColorPicker from "@/components/lib/ColorPicker";
import { Device, Light } from "@/models";
import { useAppDispatch, useAppSelector } from "@/store";
import { lightSliceActions } from "@/store/slices/lightSlice";
import { WS_SEND_MESSAGE } from "@/ws/websocketActionTypes";
import { Button, Slider, Switch, Text } from "@rneui/themed";
import { useMemo, useState } from "react";
import { Linking, View } from "react-native";

const MSG_SRC = process.env.EXPO_PUBLIC_MSG_SRC;

const ACTION_LIGHT_SET = "light__set";

function _LightDetails({ device, light }: { device: Device; light: Light }) {
  const [isOn, setIsOn] = useState(!!light.isOn);
  const [color, setColor] = useState(light.color || "#000000");
  const [brightness, setBrightness] = useState(light.brightness || 0);

  const dispatch = useAppDispatch();

  const sendIsOnMsg = (isOn: boolean) => {
    if (!device.light)
      return console.error("Unable to send is_on message; light undefined");

    const message = {
      src: MSG_SRC,
      dest: `lights/${device.id}/command`,
      action: ACTION_LIGHT_SET,
      body: {
        device_id: device.id,
        is_on: isOn,
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
        field: "isOn",
        value: message.body.is_on,
      })
    );
  };

  const handleIsOnChange = (isOn: boolean) => {
    console.info(`Set is_on: ${isOn}`);
    setIsOn(isOn);
    sendIsOnMsg(isOn);
  };

  const sendColorMsg = (hex: string) => {
    if (!device.light)
      return console.error("Unable to send color message; light undefined");

    const message = {
      src: MSG_SRC,
      dest: `lights/${device.id}/command`,
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

  const sendBrightnessMsg = (brightness: number) => {
    if (!device.light)
      return console.error(
        "Unable to send brightness message; light undefined"
      );

    const message = {
      src: MSG_SRC,
      dest: `lights/${device.id}/command`,
      action: ACTION_LIGHT_SET,
      body: {
        device_id: device.id,
        brightness: Math.floor(brightness), // Send integer
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
        field: "brightness",
        value: message.body.brightness,
      })
    );
  };

  const handleBrightnessChange = (brightness: number) => {
    console.info(`Set brightness: ${brightness}`);
    setBrightness(brightness);
    sendBrightnessMsg(brightness);
  };

  const goToWled = async () => {
    if (device.vendorId) {
      try {
        const url = `http://wled-${device.vendorId}.local/`;
        const canGo = await Linking.canOpenURL(url);
        if (canGo) {
          Linking.openURL(url);
        } else {
          console.error(`Cannot go to url ${url}`);
        }
      } catch (e) {
        console.error("Error going to WLED:", e);
      }
    } else {
      console.error("Vendor ID not found; cannot go to WLED");
    }
  };

  return (
    <View style={{ display: "flex", gap: 15 }}>
      <View
        style={{
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          gap: 10,
        }}
      >
        <Text>On/Off:</Text>
        <Switch value={isOn} onValueChange={handleIsOnChange} />
      </View>
      <View>
        <Text>Color:</Text>
        <ColorPicker initialColor={color} onChange={handleColorChange} />
      </View>
      <View>
        <Text>Brightness:</Text>
        <Slider
          minimumValue={0}
          maximumValue={255}
          value={brightness}
          onSlidingComplete={handleBrightnessChange}
          thumbStyle={{ width: 25, height: 25 }}
        />
      </View>
      <View
        style={{
          display: "flex",
          flexDirection: "row",
          justifyContent: "flex-end",
        }}
      >
        <Button onPress={goToWled}>Go To WLED</Button>
      </View>
    </View>
  );
}

type LightDetailsProps = {
  device: Device;
};

export default function LightDetails({ device }: LightDetailsProps) {
  const lights = useAppSelector((state) => state.lights.data);

  const light = useMemo(() => {
    if (device.light && device.light in lights) {
      return lights[device.light];
    }
  }, [device, lights]);

  return light ? <_LightDetails device={device} light={light} /> : null;
}
