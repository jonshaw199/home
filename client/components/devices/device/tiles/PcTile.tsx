import BaseTile, { BaseTileProps } from "./BaseTile";

export type PcTileProps = BaseTileProps;

export default function PcTile(props: PcTileProps) {
  return <BaseTile {...props} />;
}
