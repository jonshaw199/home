import React from "react";
import { Button as RNButton, ButtonProps as RNButtonProps } from "react-native";

type ButtonProps = RNButtonProps;

const Button = (props: ButtonProps) => {
  return <RNButton {...props} />;
};

export default Button;
