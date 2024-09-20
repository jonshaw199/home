import { Action, Environmental } from "@/models";
import { createModelSlice } from "./createModelSlice";
import { websocketMsgReceivedAction } from "@/ws/websocketActions";

const environmentalSlice = createModelSlice<Environmental>(
  "environmentals",
  "environmentals",
  (builder) => {
    builder.addCase(websocketMsgReceivedAction, (state, { payload }) => {
      // If this is a `system__status` message, update state
      try {
        const json = JSON.parse(payload || "");
        if (json.action === Action.STATUS_ENVIRONMENTAL) {
          const environmental = Object.values(state.data).find(
            ({ device }) => device === json.src
          );
          if (environmental) {
            console.info(
              "Updating state for environmental ID:",
              environmental.id
            );
            return {
              ...state,
              data: {
                ...state.data,
                [environmental.id]: {
                  ...state.data[environmental.id],
                  temperatureC: json.body.temperature_c,
                  temperatureF: (json.body.temperature_c * 9) / 5 + 32,
                  humidity: json.body.humidity,
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

export const environmentalSliceReducer = environmentalSlice.reducer;
export const environmentalSliceActions = environmentalSlice.actions;
