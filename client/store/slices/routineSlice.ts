import { Routine } from "@/models";
import { createModelSlice } from "./createModelSlice";

const routineSlice = createModelSlice<Routine>("routines", "routines");

export const routineSliceReducer = routineSlice.reducer;
export const routineSliceActions = routineSlice.actions;
