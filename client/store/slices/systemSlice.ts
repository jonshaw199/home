import { System } from "@/models";
import { createModelSlice } from "./createModelSlice";

const systemSlice = createModelSlice<System>("systems", "systems");

export const systemSliceReducer = systemSlice.reducer;
export const systemSliceActions = systemSlice.actions;
