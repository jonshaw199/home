import { Action, Device } from "@/models";
import { createModelSlice } from "./createModelSlice";
import { websocketMsgReceivedAction } from "@/ws/websocketActions";

const deviceSlice = createModelSlice<Device>(
  "devices",
  "devices",
  (builder) => {
    builder.addCase(websocketMsgReceivedAction, (state, { payload }) => {
      // If this is a `system__status` message, update state
      try {
        const json = JSON.parse(payload || "");
        if ("src" in json && json.src in state.data) {
          console.info("Updating state for device ID:", json.src);
          return {
            ...state,
            data: {
              ...state.data,
              [json.src]: {
                ...state.data[json.src],
                lastStatusUpdate: Date(),
              },
            },
          };
        }
      } catch (e) {}

      return state;
    });
  }
);

export const deviceSliceReducer = deviceSlice.reducer;
export const deviceSliceActions = deviceSlice.actions;
