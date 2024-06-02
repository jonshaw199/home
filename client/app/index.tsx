import React from "react";
import { StyleSheet, View, Text } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { router } from "expo-router";
import Login, { LoginProps } from "@/components/login/Login";
import { getToken } from "@/services/auth";

export default function IndexScreen() {
  const [error, setError] = React.useState("");

  const handleLogin: LoginProps["onLogin"] = async ({ username, password }) => {
    try {
      setError("");
      const token = await getToken({ username, password });
      const tokenKey = process.env.EXPO_PUBLIC_HOME_AUTH_TOKEN_KEY!;
      await AsyncStorage.setItem(tokenKey, token);
      router.replace("/home");
    } catch (e) {
      console.error("Login failed;", e);
      setError("Login failed");
    }
  };

  const style = styles();

  return (
    <View style={style.container}>
      <Login onLogin={handleLogin} />
      {error && <Text style={style.error}>{error}</Text>}
    </View>
  );
}

const styles = () =>
  StyleSheet.create({
    container: {
      padding: 10,
      flexGrow: 1,
      justifyContent: "center",
      gap: 10,
    },
    error: {
      color: "red",
      fontSize: 18,
    },
  });
