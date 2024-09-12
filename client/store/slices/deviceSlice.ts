import { Device } from "@/models";
import { createModelSlice } from "./createModelSlice";

const deviceSlice = createModelSlice<Device>("devices", "devices");

export const deviceSliceReducer = deviceSlice.reducer;
export const deviceSliceActions = deviceSlice.actions;
