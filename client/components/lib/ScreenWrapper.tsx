// ScreenWrapper.js
import React, { ReactNode } from "react";
import { SafeAreaView, StyleSheet } from "react-native";

// TODO: add ScrollView
const ScreenWrapper = ({ children }: { children: ReactNode }) => {
  return <SafeAreaView style={styles.container}>{children}</SafeAreaView>;
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});

export default ScreenWrapper;
