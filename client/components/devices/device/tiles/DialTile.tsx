import BaseTile, { BaseTileProps } from "./BaseTile";

export type DialTileProps = BaseTileProps;

export default function DialTile(props: DialTileProps) {
  return <BaseTile {...props} />;
}
