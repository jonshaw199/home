import { Routine } from "@/models";
import { Text } from "react-native";

export default function RoutineDetails({ routine }: { routine: Routine }) {
  return <Text>Name: {routine.name}</Text>;
}
