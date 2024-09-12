import { useAppSelector } from "@/store";
import React from "react";
import { View } from "react-native";
import DeviceTile from "./DeviceTile";

const Devices = () => {
  const devices = useAppSelector((state) => state.devices.data);

  return (
    <View>
      {Object.values(devices).map((device) => (
        <DeviceTile key={device.id} device={device} />
      ))}
    </View>
  );
};

export default Devices;
