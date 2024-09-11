import { useAppDispatch } from "@/hooks/redux";
import { deviceSliceActions } from "@/slices/deviceSlice";
import React, { useEffect } from "react";
import { Platform, StatusBar, StyleSheet, Text } from "react-native";

const Home = () => {
  const style = styles();
  const dispatch = useAppDispatch();

  useEffect(() => {
    dispatch(deviceSliceActions.fetchAll());
  }, []);

  return <Text style={style.container}>Home</Text>;
};

const styles = () =>
  StyleSheet.create({
    container: {
      paddingTop: Platform.OS === "android" ? StatusBar.currentHeight : 0,
    },
  });

export default Home;
