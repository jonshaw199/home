import React from "react";
import { Platform, StatusBar, StyleSheet, Text } from "react-native";

const Home = () => {
  const style = styles();

  return <Text style={style.container}>Home</Text>;
};

const styles = () =>
  StyleSheet.create({
    container: {
      paddingTop: Platform.OS === "android" ? StatusBar.currentHeight : 0,
    },
  });

export default Home;
