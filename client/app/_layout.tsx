import { Slot } from "expo-router";
import { store } from "@/store";
import { Provider } from "react-redux";
import { ThemeProvider } from "@/providers/ThemeProvider";

export default function Root() {
  return (
    <ThemeProvider>
      <Provider store={store}>
        <Slot />
      </Provider>
    </ThemeProvider>
  );
}
