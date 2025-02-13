import Login, { LoginProps } from "@/components/login/Login";
import { useAppDispatch } from "@/store";
import { signIn } from "@/store/slices/sessionSlice";
import { router } from "expo-router";
import React from "react";
import { StyleSheet, View, Text } from "react-native";

export default function LoginScreen() {
  const [error, setError] = React.useState("");

  const dispatch = useAppDispatch();

  const handleLogin: LoginProps["onLogin"] = async ({ username, password }) => {
    try {
      setError("");
      await dispatch(signIn({ username, password }));
      router.replace("/");
    } catch (e) {
      console.error("Login failed;", e);
      setError("Login failed");
    }
  };

  const style = styles();

  return (
    <View style={style.container}>
      <Login onLogin={handleLogin} />
      {error ? <Text style={style.error}>{error}</Text> : null}
    </View>
  );
}

const styles = () =>
  StyleSheet.create({
    container: {
      padding: 10,
      //flexGrow: 1,
      justifyContent: "center",
      gap: 10,
    },
    error: {
      color: "red",
      fontSize: 18,
    },
  });
