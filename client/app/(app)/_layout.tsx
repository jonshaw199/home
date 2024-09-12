import AuthWall from "@/components/AuthWall";
import Drawer from "@/components/drawer/Drawer";
import { store } from "@/store";
import { Provider } from "react-redux";

export default function Layout() {
  return (
    <AuthWall redirect="/login">
      <Provider store={store}>
        <Drawer />
      </Provider>
    </AuthWall>
  );
}
