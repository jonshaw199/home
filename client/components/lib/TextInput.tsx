import React from "react";
import {
  TextInput as RNTextInput,
  StyleSheet,
  TextInputProps as RNTextInputProps,
} from "react-native";

const defaultSize: TextInputProps["size"] = "md";

type TextInputProps = RNTextInputProps & {
  size?: "sm" | "md" | "lg";
};

const TextInput = (props: TextInputProps) => {
  const { style, ...rest } = props;

  return <RNTextInput {...rest} style={[styles(props).input, style]} />;
};

const styles = (props: TextInputProps) =>
  StyleSheet.create({
    input: {
      borderWidth: 1,
      borderRadius: 5,
      borderColor: "grey",
      height: getHeight(props.size),
      fontSize: getFontSize(props.size),
      padding: 10,
    },
  });

const getHeight = (size: TextInputProps["size"] = defaultSize) => {
  switch (size) {
    case "sm":
      return 37;
    case "md":
      return 43;
    case "lg":
      return 50;
  }
};

const getFontSize = (size: TextInputProps["size"] = defaultSize) => {
  switch (size) {
    case "sm":
      return 15;
    case "md":
      return 17;
    case "lg":
      return 19;
  }
};

export default TextInput;
