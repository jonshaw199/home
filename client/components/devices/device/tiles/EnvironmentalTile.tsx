import BaseTile, { BaseTileProps } from "./BaseTile";

export type EnvironmentalTileProps = BaseTileProps;

export default function EnvironmentalTile(props: EnvironmentalTileProps) {
  return <BaseTile {...props} />;
}
