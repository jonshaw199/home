import React, { useCallback, useEffect } from "react";
import { View, StyleSheet, TouchableOpacity, Text } from "react-native";
import {
  DrawerContentScrollView,
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
import { useRouteInfo } from "expo-router/build/hooks";
import { Theme, useTheme } from "@/providers/ThemeProvider";
import { Feather, MaterialCommunityIcons } from "@expo/vector-icons";
import { systemSliceActions } from "@/store/slices/systemSlice";
import { lightSliceActions } from "@/store/slices/lightSlice";
import { routineSliceActions } from "@/store/slices/routineSlice";
import { routineActionSliceActions } from "@/store/slices/routineActionSlice";

// Custom drawer item component
const CustomDrawerItem: React.FC<{
  label: string;
  onPress: () => void;
  active: boolean;
  icon?: React.ReactNode;
}> = ({ label, onPress, active, icon }) => {
  const theme = useTheme();
  const style = styles(theme);

  return (
    <TouchableOpacity
      onPress={onPress}
      style={[style.drawerItem, active ? style.drawerItemActive : {}]}
    >
      {icon}
      <Text
        style={[style.drawerItemText, active ? style.drawerItemActiveText : {}]}
      >
        {label}
      </Text>
    </TouchableOpacity>
  );
};

const navIconSize = 25;

// Custom Drawer Content Component with TypeScript types
const CustomDrawerContent: React.FC<DrawerContentComponentProps> = (props) => {
  const dispatch = useAppDispatch();
  const theme = useTheme();
  const style = styles(theme);

  return (
    <DrawerContentScrollView
      {...props}
      contentContainerStyle={style.drawerContainer}
    >
      <View style={style.navItemsContainer}>
        {Object.values(props.descriptors).map(({ options, route }, index) => (
          <CustomDrawerItem
            key={index}
            label={options.title || route.name}
            onPress={() => props.navigation.navigate(route.name)}
            active={props.state.index === index}
            icon={
              options.drawerIcon &&
              options.drawerIcon({
                color: props.state.index === index ? theme.light : theme.dark,
                focused: props.state.index === index,
                size: navIconSize,
              })
            }
          />
        ))}
        <CustomDrawerItem
          key="drawer_item__log_out"
          label="Log Out"
          onPress={() => dispatch(signOut())}
          active={false}
          icon={
            <Feather name="log-out" color={theme.dark} size={navIconSize} />
          }
        />
      </View>
    </DrawerContentScrollView>
  );
};

export default function Drawer() {
  const theme = useTheme();
  const style = styles(theme);
  const dispatch = useAppDispatch();
  const session = useAppSelector(selectSession);
  const { segments } = useRouteInfo();

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
      dispatch(systemSliceActions.fetchAll());
      dispatch(lightSliceActions.fetchAll());
      dispatch(routineSliceActions.fetchAll());
      dispatch(routineActionSliceActions.fetchAll());
      connectWebSocket(session);
    } else {
      console.error("Session is null; unable to load");
    }
  }, [session, connectWebSocket, dispatch]);

  // This is the app layout
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <ExpoDrawer
        // Only show drawer nav at top level
        screenOptions={{
          headerShown: segments.length < 3,
          headerStyle: style.drawerHeader,
        }}
        drawerContent={(props) => <CustomDrawerContent {...props} />}
      >
        <ExpoDrawer.Screen
          name="index"
          options={{
            title: "Home",
            drawerIcon: ({ color, size }) => (
              <Feather name="home" color={color} size={size} />
            ),
          }}
        />
        <ExpoDrawer.Screen
          name="devices"
          options={{
            title: "Devices",
            drawerIcon: ({ color, size }) => (
              <MaterialCommunityIcons
                name="devices"
                color={color}
                size={size}
              />
            ),
          }}
        />
        <ExpoDrawer.Screen
          name="routines"
          options={{
            title: "Routines",
            drawerIcon: ({ color, size }) => (
              <MaterialCommunityIcons name="clock" color={color} size={size} />
            ),
          }}
        />
      </ExpoDrawer>
    </GestureHandlerRootView>
  );
}

// Styles
const styles = (theme: Theme) =>
  StyleSheet.create({
    drawerContainer: {
      flex: 1,
      justifyContent: "space-between",
      backgroundColor: theme.light,
    },
    drawerHeader: {
      backgroundColor: theme.light,
    },
    buttonContainer: {
      padding: 10,
    },
    navItemsContainer: {
      flex: 1,
    },
    drawerItem: {
      paddingVertical: 16,
      paddingHorizontal: 16,
      display: "flex",
      flexDirection: "row",
      alignItems: "center",
      gap: 15,
    },
    drawerItemText: {
      color: theme.dark, // Default text color
      fontSize: 18,
      marginTop: 4,
    },
    drawerItemActive: {
      backgroundColor: theme.primary, // Active item background color
    },
    drawerItemActiveText: {
      color: theme.light, // Active item text color
    },
  });
