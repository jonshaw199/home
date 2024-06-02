import React from "react";
import { Platform, StatusBar, StyleSheet, Text, View } from "react-native";

const Home = () => {
  const style = styles();

  return (
    <View style={style.container}>
      <Text>Home</Text>
    </View>
  );
};

const styles = () =>
  StyleSheet.create({
    container: {
      paddingTop: Platform.OS === "android" ? StatusBar.currentHeight : 0,
    },
  });

export default Home;
