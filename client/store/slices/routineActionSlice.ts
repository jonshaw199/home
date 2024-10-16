import { RoutineAction } from "@/models";
import { createModelSlice } from "./createModelSlice";

const routineActionSlice = createModelSlice<RoutineAction>(
  "routineActions",
  "routineActions"
);

export const routineActionSliceReducer = routineActionSlice.reducer;
export const routineActionSliceActions = routineActionSlice.actions;
