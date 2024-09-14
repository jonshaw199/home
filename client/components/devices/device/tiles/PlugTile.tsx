import BaseTile, { BaseTileProps } from "./BaseTile";

export type PlugTileProps = Pick<BaseTileProps, "device">;

export default function PlugTile(props: PlugTileProps) {
  const handlePress = () => {
    console.log("test");
  };
  return <BaseTile {...props} pressableProps={{ onPress: handlePress }} />;
}
