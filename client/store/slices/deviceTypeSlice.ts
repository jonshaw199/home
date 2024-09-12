import { DeviceType } from "@/models";
import { createModelSlice } from "./createModelSlice";

const deviceTypeSlice = createModelSlice<DeviceType>(
  "deviceTypes",
  "deviceTypes"
);

export const deviceTypeSliceReducer = deviceTypeSlice.reducer;
export const deviceTypeSliceActions = deviceTypeSlice.actions;
