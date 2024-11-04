import { ActionType, Plug } from "@/models";
import { createModelSlice } from "./createModelSlice";
import { websocketMsgReceivedAction } from "@/ws/websocketActions";

const plugSlice = createModelSlice<Plug>("plugs", "plugs", (builder) => {
  builder.addCase(websocketMsgReceivedAction, (state, { payload }) => {
    try {
      const json = JSON.parse(payload || "");

      switch (json.action) {
        case ActionType.STATUS_PLUG: {
          const plug = Object.values(state.data).find(
            ({ device }) => device === json.src
          );
          if (plug) {
            console.info("Updating state for plug ID:", plug.id);
            return {
              ...state,
              data: {
                ...state.data,
                [plug.id]: {
                  ...state.data[plug.id],
                  isOn: json.body.is_on,
                },
              },
            };
          }
          break;
        }
        case ActionType.SET_PLUG: {
          const plug = Object.values(state.data).find(
            ({ device }) => device === json.body.device_id
          );
          if (plug) {
            console.info("Updating state for plug:", plug.id);
            return {
              ...state,
              data: {
                ...state.data,
                [plug.id]: {
                  ...state.data[plug.id],
                  isOn: json.body.is_on,
                },
              },
            };
          }
          break;
        }
      }
    } catch (e) {
      console.error(`Error handling websocket message: ${e}`);
    }

    return state;
  });
});

export const plugSliceReducer = plugSlice.reducer;
export const plugSliceActions = plugSlice.actions;
