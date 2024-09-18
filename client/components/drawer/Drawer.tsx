import React, { useCallback, useEffect } from "react";
import { View, Button, StyleSheet } from "react-native";
import {
  DrawerContentScrollView,
  DrawerItemList,
  DrawerContentComponentProps,
} from "@react-navigation/drawer";
import { Drawer as ExpoDrawer } from "expo-router/drawer";
import { useAppDispatch, useAppSelector } from "@/store";
import { deviceSliceActions } from "@/store/slices/deviceSlice";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { deviceTypeSliceActions } from "@/store/slices/deviceTypeSlice";
import { plugSliceActions } from "@/store/slices/plugSlice";
import { WS_CONNECT } from "@/ws/websocketActionTypes";
import { environmentalSliceActions } from "@/store/slices/environmentalSlice";
import { selectSession, signOut } from "@/store/slices/sessionSlice";

// Custom Drawer Content Component with TypeScript types
const CustomDrawerContent: React.FC<DrawerContentComponentProps> = (props) => {
  const dispatch = useAppDispatch();

  return (
    <DrawerContentScrollView
      {...props}
      contentContainerStyle={styles.drawerContainer}
    >
      <View style={styles.navItemsContainer}>
        <DrawerItemList {...props} />
      </View>
      <View style={styles.buttonContainer}>
        <Button title="Log Out" onPress={() => dispatch(signOut())} />
      </View>
    </DrawerContentScrollView>
  );
};

export default function Drawer() {
  const dispatch = useAppDispatch();
  const session = useAppSelector(selectSession);

  const connectWebSocket = useCallback(
    (token: string) => {
      // Initialize WebSocket connection
      const url = process.env.EXPO_PUBLIC_HOME_WS_URL;
      if (!url) throw "WebSocket URL not found; cannot connect";
      dispatch({ type: WS_CONNECT, payload: { url: `${url}?token=${token}` } });
    },
    [dispatch]
  );

  // Initial load
  useEffect(() => {
    if (session) {
      dispatch(deviceTypeSliceActions.fetchAll());
      dispatch(deviceSliceActions.fetchAll());
      dispatch(plugSliceActions.fetchAll());
      dispatch(environmentalSliceActions.fetchAll());
      connectWebSocket(session);
    } else {
      console.error("Session is null; unable to load");
    }
  }, [session, dispatch]);

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
