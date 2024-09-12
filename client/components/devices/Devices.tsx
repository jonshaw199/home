import { useAppDispatch } from "@/hooks/redux";
import { deviceSliceActions } from "@/store/slices/deviceSlice";
import React, { useEffect } from "react";
import { Platform, StatusBar, StyleSheet, Text } from "react-native";

const Devices = () => {
  const style = styles();
  const dispatch = useAppDispatch();

  useEffect(() => {
    dispatch(deviceSliceActions.fetchAll());
  }, []);

  return <Text style={style.container}>Devices</Text>;
};

const styles = () =>
  StyleSheet.create({
    container: {
      paddingTop: Platform.OS === "android" ? StatusBar.currentHeight : 0,
    },
  });

export default Devices;
