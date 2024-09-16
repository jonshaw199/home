import { Environmental } from "@/models";
import { createModelSlice } from "./createModelSlice";

const environmentalSlice = createModelSlice<Environmental>(
  "environmentals",
  "environmentals"
);

export const environmentalSliceReducer = environmentalSlice.reducer;
export const environmentalSliceActions = environmentalSlice.actions;
