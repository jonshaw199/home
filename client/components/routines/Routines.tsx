import { useAppSelector } from "@/store";
import { FlatList } from "react-native";
import { Routine } from "@/models";
import { ListItem, Icon } from "@rneui/themed"; // Import Icon from @rneui/themed
import { useMemo } from "react";
import { router } from "expo-router"; // Import useNavigation from expo-router

export default function Routines() {
  const routines = useAppSelector((state) => state.routines.data);

  const routineList = useMemo(() => Object.values(routines), [routines]);

  const keyExtractor = (_: Routine, index: number) => index.toString();

  const renderItem = ({ item }: { item: Routine }) => (
    <ListItem
      bottomDivider
      onPress={() => router.push(`/routines/${item.id}`)} // Navigate on press
    >
      <Icon
        name="check-circle"
        type="feather"
        color={item.active ? "blue" : "gray"} // Active = blue, Inactive = gray
      />
      <ListItem.Content>
        <ListItem.Title>{item.name}</ListItem.Title>
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
