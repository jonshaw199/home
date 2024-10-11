import { Light } from "@/models";
import { createModelSlice } from "./createModelSlice";
import { websocketMsgReceivedAction } from "@/ws/websocketActions";

const lightSlice = createModelSlice<Light>("lights", "lights", (builder) => {
  builder.addCase(websocketMsgReceivedAction, (state, { payload }) => {
    // If this is a `light__status` message, update state
    // TODO

    return state;
  });
});

export const lightSliceReducer = lightSlice.reducer;
export const lightSliceActions = lightSlice.actions;
