import { useAppSelector } from "@/store";
import { FlatList } from "react-native";
import { Routine } from "@/models";
import { ListItem } from "@rneui/themed";
import { useMemo } from "react";

export default function Routines() {
  const routines = useAppSelector((state) => state.routines.data);

  const routineList = useMemo(() => Object.values(routines), [routines]);

  const keyExtractor = (routine: Routine, index: number) => index.toString();

  const renderItem = ({ item }: { item: Routine }) => (
    <ListItem bottomDivider>
      {/*<Avatar source={{uri: item.avatar_url}} />*/}
      <ListItem.Content>
        <ListItem.Title>{item.name}</ListItem.Title>
        {/*<ListItem.Subtitle>{item.subtitle}</ListItem.Subtitle>*/}
      </ListItem.Content>
      <ListItem.Chevron />
    </ListItem>
  );

  return (
    <FlatList
      keyExtractor={keyExtractor}
      data={routineList}
      renderItem={renderItem}
    />
  );
}
