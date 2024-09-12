import { useAppSelector } from "@/store";
import React from "react";
import { View } from "react-native";
import DeviceTile from "./DeviceTile";

const Devices = () => {
  const { devices, deviceTypes } = useAppSelector((state) => ({
    devices: state.devices.data,
    deviceTypes: state.deviceTypes.data,
  }));

  console.log(deviceTypes);

  return (
    <View>
      {Object.values(devices).map((device) => (
        <DeviceTile key={device.id} device={device} />
      ))}
    </View>
  );
};

export default Devices;
