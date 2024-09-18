import AuthWall from "@/components/AuthWall";
import Drawer from "@/components/drawer/Drawer";

export default function Layout() {
  return (
    <AuthWall redirect="/login">
      <Drawer />
    </AuthWall>
  );
}
