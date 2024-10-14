import React from "react";
import { StyleSheet } from "react-native";
import _ColorPicker, {
  Panel3,
  Preview,
  Swatches,
} from "reanimated-color-picker";

type ColorPickerProps = {
  initialColor?: string;
  onChange: (hex: string) => void;
};

export default function ColorPicker({
  initialColor,
  onChange,
}: ColorPickerProps) {
  return (
    <_ColorPicker
      style={styles.picker}
      value={initialColor}
      onComplete={({ hex }) => onChange(hex.substring(0, 7))}
    >
      <Panel3 style={styles.panel} />
      <Swatches style={styles.swatches} />
      <Preview hideInitialColor />
    </_ColorPicker>
  );
}

const styles = StyleSheet.create({
  picker: {
    width: "100%",
    gap: 10,
    alignItems: "center",
  },
  panel: {
    maxWidth: 300,
    width: "100%",
  },
  swatches: {
    justifyContent: "flex-start",
  },
});
