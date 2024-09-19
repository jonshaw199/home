// ThemeProvider.tsx
import React, { createContext, useContext } from "react";

export type Theme = {
  primary: string;
  secondary: string;
  success: string;
  danger: string;
  warning: string;
  info: string;
  light: string;
  dark: string;
  muted: string;
  white: string;
  black: string;
};

const theme: Theme = {
  primary: "#0c7b93", // Jedi Blue
  secondary: "#8b0000", // Sith Red
  success: "#228b22", // Endor Green
  danger: "#000000", // Dark Side Black
  warning: "#d2b48c", // Tatooine Sand
  info: "#f0f8ff", // Hoth White
  light: "#d3d3d3", // Rebel Light Gray
  dark: "#2f4f4f", // Empire Dark Gray
  muted: "#778899", // Bespin Cloud Gray
  white: "#ffffff", // Stormtrooper White
  black: "#000000", // Galactic Black
};

type ThemeContextType = typeof theme;

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  return (
    <ThemeContext.Provider value={theme}>{children}</ThemeContext.Provider>
  );
};

// Custom hook to use the theme
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};
