import { Action, System } from "@/models";
import { createModelSlice } from "./createModelSlice";
import { websocketMsgReceivedAction } from "@/ws/websocketActions";

const systemSlice = createModelSlice<System>(
  "systems",
  "systems",
  (builder) => {
    builder.addCase(websocketMsgReceivedAction, (state, { payload }) => {
      // If this is a `system__status` message, update state
      try {
        const json = JSON.parse(payload || "");
        if (json.action === Action.STATUS_SYSTEM) {
          const system = Object.values(state.data).find(
            ({ device }) => device === json.src
          );
          if (system) {
            console.info("Updating state for system ID:", system.id);
            return {
              ...state,
              data: {
                ...state.data,
                [system.id]: {
                  ...state.data[system.id],
                  cpuUsage: json.body.cpu_usage,
                  memUsage: json.body.memory_usage,
                },
              },
            };
          }
        }
      } catch (e) {}

      return state;
    });
  }
);

export const systemSliceReducer = systemSlice.reducer;
export const systemSliceActions = systemSlice.actions;
