import { Plug } from "@/models";
import { createModelSlice } from "./createModelSlice";

const plugSlice = createModelSlice<Plug>("plugs", "plugs");

export const plugSliceReducer = plugSlice.reducer;
export const plugSliceActions = plugSlice.actions;
