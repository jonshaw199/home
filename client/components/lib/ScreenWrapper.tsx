import { ReactNode } from "react";
import { SafeAreaView, ScrollView, StyleSheet } from "react-native";

export default function ScreenWrapper({ children }: { children: ReactNode }) {
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollView}>
        {children}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flexGrow: 1,
    padding: 10,
  },
});
