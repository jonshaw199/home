import { useAppSelector } from "@/store";
import React from "react";
import { StyleSheet, View } from "react-native";
import DeviceTile from "./device/DeviceTile";

export default function Devices() {
  const devices = useAppSelector((state) => state.devices.data);

  const style = styles();

  return (
    <View style={style.container}>
      {Object.values(devices).map((device) => (
        <DeviceTile key={device.id} device={device} />
      ))}
    </View>
  );
}

const styles = () =>
  StyleSheet.create({
    container: {
      display: "flex",
      flexDirection: "row",
      gap: 10,
      flexWrap: "wrap",
    },
  });
