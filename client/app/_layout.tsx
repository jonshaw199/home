import { Slot } from "expo-router";
import { store, useAppDispatch } from "@/store";
import { Provider } from "react-redux";
import { ThemeProvider } from "@/providers/ThemeProvider";
import { ReactNode, useEffect } from "react";
import { initializeBaseUrl } from "@/store/slices/urlSlice";

function Inner({ children }: { children: ReactNode }) {
  const dispatch = useAppDispatch();

  useEffect(() => {
    dispatch(initializeBaseUrl());
  }, [dispatch]);

  return children;
}

export default function Root() {
  return (
    <ThemeProvider>
      <Provider store={store}>
        <Inner>
          <Slot />
        </Inner>
      </Provider>
    </ThemeProvider>
  );
}
