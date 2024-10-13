import { Slot } from "expo-router";
import { store } from "@/store";
import { Provider } from "react-redux";
import { ThemeProvider } from "@/providers/ThemeProvider";
import ScreenWrapper from "@/components/lib/ScreenWrapper";

export default function Root() {
  return (
    <ThemeProvider>
      <Provider store={store}>
        <ScreenWrapper>
          <Slot />
        </ScreenWrapper>
      </Provider>
    </ThemeProvider>
  );
}
