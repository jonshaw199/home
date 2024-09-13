import BaseTile, { BaseTileProps } from "./BaseTile";

export type DialTileProps = Pick<BaseTileProps, "device">;

export default function DialTile(props: DialTileProps) {
  return <BaseTile {...props} />;
}
