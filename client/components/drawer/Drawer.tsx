import React, { useEffect } from "react";
import { View, Button, StyleSheet } from "react-native";
import {
  DrawerContentScrollView,
  DrawerItemList,
  DrawerContentComponentProps,
} from "@react-navigation/drawer";
import { useSession } from "@/context/SessionContext";
import { Drawer as ExpoDrawer } from "expo-router/drawer";
import { useAppDispatch } from "@/store";
import { deviceSliceActions } from "@/store/slices/deviceSlice";
import { GestureHandlerRootView } from "react-native-gesture-handler";

// Custom Drawer Content Component with TypeScript types
const CustomDrawerContent: React.FC<DrawerContentComponentProps> = (props) => {
  const { signOut } = useSession();

  return (
    <DrawerContentScrollView
      {...props}
      contentContainerStyle={styles.drawerContainer}
    >
      <View style={styles.navItemsContainer}>
        {/* Drawer Items */}
        <DrawerItemList {...props} />
      </View>

      {/* Button at the bottom */}
      <View style={styles.buttonContainer}>
        <Button title="Log Out" onPress={signOut} />
      </View>
    </DrawerContentScrollView>
  );
};

export default function Drawer() {
  const dispatch = useAppDispatch();

  // Initial load
  useEffect(() => {
    dispatch(deviceSliceActions.fetchAll());
  }, [dispatch]);

  // This is the app layout
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <ExpoDrawer drawerContent={(props) => <CustomDrawerContent {...props} />}>
        <ExpoDrawer.Screen name="index" options={{ title: "Home" }} />
        <ExpoDrawer.Screen
          name="devices/index"
          options={{ title: "Devices" }}
        />
      </ExpoDrawer>
    </GestureHandlerRootView>
  );
}

// Styles
const styles = StyleSheet.create({
  drawerContainer: {
    flex: 1,
    justifyContent: "space-between",
  },
  navItemsContainer: {},
  buttonContainer: {
    padding: 10,
    borderTopWidth: 1,
    borderTopColor: "#ccc",
  },
});
