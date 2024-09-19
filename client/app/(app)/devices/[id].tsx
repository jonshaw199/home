import DeviceDetails from "@/components/devices/device/DeviceDetails";
import { Theme, useTheme } from "@/providers/ThemeProvider";
import { useAppSelector } from "@/store";
import { Redirect, useLocalSearchParams } from "expo-router";
import React, { useMemo } from "react";
import { StyleSheet, View } from "react-native";

const DeviceDetailsScreen = () => {
  const theme = useTheme();
  const style = styles(theme);
  const { id } = useLocalSearchParams();
  const devices = useAppSelector((state) => state.devices.data);

  const device = useMemo(() => {
    if (typeof id == "string" && id in devices) {
      return devices[id];
    }
  }, [id, devices]);

  if (!device) {
    return <Redirect href="/" />;
  }

  return (
    <View style={style.container}>
      <DeviceDetails device={device} />
    </View>
  );
};

const styles = (theme: Theme) =>
  StyleSheet.create({
    container: {
      backgroundColor: "white",
      flex: 1,
    },
  });

export default DeviceDetailsScreen;
