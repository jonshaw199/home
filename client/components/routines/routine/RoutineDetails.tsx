import { ID, Routine, RoutineAction } from "@/models";
import { useAppSelector } from "@/store";
import { Card } from "@rneui/themed";
import { useMemo } from "react";
import { Text, View } from "react-native";

function Action({ actionId }: { actionId: ID }) {
  const actions = useAppSelector((state) => state.routineActions.data);

  const action = useMemo(() => {
    if (actionId in actions) {
      return actions[actionId];
    }
  }, [actionId, actions]);

  if (!action) {
    return null;
  }

  return (
    <View>
      <Text>ID: {action.id}</Text>
      <Text>Name: {action.name}</Text>
      <Text>Active: {action.active ? "Yes" : "No"}</Text>
      <Text>Type: {action.type}</Text>
      <Text>Params: {action.evalParams}</Text>
    </View>
  );
}

export default function RoutineDetails({ routine }: { routine: Routine }) {
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
        <View>
          {routine.actions?.map((action) => (
            <Action actionId={action} key={`Action_${action}`} />
          ))}
        </View>
      </Card>
    </>
  );
}
