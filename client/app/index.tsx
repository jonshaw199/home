import React from "react";
import { StyleSheet, View, Text } from "react-native";
import Login, { LoginProps } from "@/components/login/Login";

export default function Index() {
  const [error, setError] = React.useState("");

  const handleLogin: LoginProps["onLogin"] = async () => {
    try {
      setError("");
      // todo
      await new Promise((_, rej) => {
        setTimeout(() => {
          return rej("Error");
        }, 1000);
      });
    } catch (e) {
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
