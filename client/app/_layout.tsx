import { Slot } from "expo-router";
import { store } from "@/store";
import { Provider } from "react-redux";

export default function Root() {
  return (
    <Provider store={store}>
      <Slot />;
    </Provider>
  );
}
