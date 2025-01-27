import { ActionType, Light } from "@/models";
import { createModelSlice } from "./createModelSlice";
import { websocketMsgReceivedAction } from "@/ws/websocketActions";

const getLightUpdates = (jsonMsg: any) => {
  const updates: any = {};
  if ("is_on" in jsonMsg.body) updates.isOn = jsonMsg.body.is_on;
  if ("brightness" in jsonMsg.body)
    updates.brightness = jsonMsg.body.brightness;
  if ("color" in jsonMsg.body) updates.color = jsonMsg.body.color;
  return updates;
};

const lightSlice = createModelSlice<Light>("lights", "lights", (builder) => {
  builder.addCase(websocketMsgReceivedAction, (state, { payload }) => {
    try {
      const json = JSON.parse(payload || "");
      if (json.action === ActionType.SET_LIGHT) {
        const light = Object.values(state.data).find(
          ({ device }) => device === json.body.device_id
        );
        if (light) {
          console.info("Updating state for light ID:", light.id);
          console.log(getLightUpdates(json));
          return {
            ...state,
            [light.id]: {
              ...state.data[light.id],
              ...getLightUpdates(json),
            },
          };
        } else {
          console.warn("Light not found for ID:", json.src);
        }
      }
    } catch (e) {
      console.error("Error handling websocket message:", e);
    }

    return state;
  });
});

export const lightSliceReducer = lightSlice.reducer;
export const lightSliceActions = lightSlice.actions;
