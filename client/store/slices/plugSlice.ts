import { Action, Plug } from "@/models";
import { createModelSlice } from "./createModelSlice";
import { websocketMsgReceivedAction } from "@/ws/websocketActions";

const plugSlice = createModelSlice<Plug>("plugs", "plugs", (builder) => {
  builder.addCase(websocketMsgReceivedAction, (state, { payload }) => {
    // If this is a `plug__status` message, update state
    try {
      const json = JSON.parse(payload || "");
      if (json.action === Action.STATUS_PLUG) {
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
      }
    } catch (e) {}

    return state;
  });
});

export const plugSliceReducer = plugSlice.reducer;
export const plugSliceActions = plugSlice.actions;
