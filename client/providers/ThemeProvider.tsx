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
};

const theme: Theme = {
  primary: "#0c7b93", // Jedi Blue
  secondary: "#d3d3d3", // Bespin Cloud Gray
  light: "#f0f8ff", // Hoth White
  danger: "#8b0000", // Sith Red
  warning: "#f5de84", // (yellowish)
  success: "#228b22", // Endor Green
  dark: "#2f4f4f", // Empire Dark Gray
  muted: "#f5f5dc", // Naboo Beige
  info: "#b0c4de", // Alderaan Blue
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
