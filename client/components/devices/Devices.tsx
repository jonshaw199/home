import React, { useEffect } from "react";
import { Platform, StatusBar, StyleSheet, Text } from "react-native";

const Devices = () => {
  const style = styles();

  return <Text style={style.container}>Devices</Text>;
};

const styles = () =>
  StyleSheet.create({
    container: {
      paddingTop: Platform.OS === "android" ? StatusBar.currentHeight : 0,
    },
  });

export default Devices;
