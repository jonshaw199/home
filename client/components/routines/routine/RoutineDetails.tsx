import { ID, Routine, RoutineAction } from "@/models";
import { useAppSelector } from "@/store";
import { Card, Icon } from "@rneui/themed"; // Import Icon for active/inactive indicator
import { useMemo } from "react";
import { Text, View, FlatList } from "react-native";

function Action({ action }: { action: RoutineAction }) {
  return (
    <View
      style={{ flexDirection: "row", alignItems: "center", marginBottom: 10 }}
    >
      <Icon
        name="check-circle"
        type="feather"
        color={action.active ? "blue" : "gray"} // Active = blue, Inactive = gray
        style={{ marginRight: 10 }}
      />
      <View>
        <Text>ID: {action.id}</Text>
        <Text>Name: {action.name}</Text>
        <Text>Type: {action.type}</Text>
        <Text>Params: {action.evalParams}</Text>
      </View>
    </View>
  );
}

export default function RoutineDetails({ routine }: { routine: Routine }) {
  const actions = useAppSelector((state) => state.routineActions.data);

  const routineActions = useMemo(() => {
    return routine.actions
      ?.map((actionId) => actions[actionId])
      .filter((action) => !!action); // Filter out undefined actions
  }, [routine.actions, actions]);

  const renderAction = ({ item }: { item: RoutineAction }) => (
    <Action action={item} />
  );

  return (
    <>
      <Card>
        <Card.Title>Routine</Card.Title>
        <Text>ID: {routine.id}</Text>
        <Text>Name: {routine.name}</Text>
        <Text>Active: {routine.active ? "Yes" : "No"}</Text>
        <Text>Triggers: {routine.triggers}</Text>
        <Text>Repeat: {routine.repeatInterval}</Text>
      </Card>

      <Card>
        <Card.Title>Actions</Card.Title>
        {/* Use FlatList for actions */}
        <FlatList
          data={routineActions}
          renderItem={renderAction}
          keyExtractor={(item) => `Action_${item.id}`}
        />
      </Card>
    </>
  );
}
