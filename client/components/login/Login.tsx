import React from "react";
import { StyleSheet, View } from "react-native";
import TextInput from "@/components/lib/TextInput";
import Button from "@/components/lib/Button";

export type LoginProps = {
  onLogin: (_: { username: string; password: string }) => void;
};

const Login = ({ onLogin }: LoginProps) => {
  const [username, setUsername] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [loggingIn, setLoggingIn] = React.useState(false);

  const loginBtnDisabled = React.useMemo(
    () => !(username && password) || loggingIn,
    [username, password, loggingIn]
  );

  const handleLogin = async () => {
    const promised = Promise.resolve(onLogin({ username, password }));

    try {
      setLoggingIn(true);
      await promised;
    } catch (e) {
      console.error(`Error logging in: ${e}`);
    } finally {
      setLoggingIn(false);
    }
  };

  const style = styles();

  return (
    <View style={style.container}>
      <TextInput
        value={username}
        onChangeText={setUsername}
        placeholder="Username"
        size="lg"
      />
      <TextInput
        value={password}
        onChangeText={setPassword}
        placeholder="Password"
        size="lg"
        secureTextEntry
        onSubmitEditing={handleLogin}
      />
      <Button
        title="Log In"
        disabled={loginBtnDisabled}
        onPress={handleLogin}
      />
    </View>
  );
};

const styles = () =>
  StyleSheet.create({
    container: {
      flexDirection: "column",
      gap: 10,
    },
  });

export default Login;
