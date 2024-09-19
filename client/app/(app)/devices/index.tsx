import Devices from "@/components/devices/Devices";
import { Theme, useTheme } from "@/providers/ThemeProvider";
import React from "react";
import { StyleSheet, View } from "react-native";

const DevicesScreen = () => {
  const theme = useTheme();
  const style = styles(theme);

  return (
    <View style={style.container}>
      <Devices />
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

export default DevicesScreen;
