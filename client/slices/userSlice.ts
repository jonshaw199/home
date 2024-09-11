import { User } from "@/models";
import { createModelSlice } from "./createModelSlice";

const userSlice = createModelSlice<User>("user", "user");

export const userSliceReducer = userSlice.reducer;
export const userSliceActions = userSlice.actions;
