import { createAction } from "@reduxjs/toolkit";
import { WS_MESSAGE_RECEIVED } from "./websocketActionTypes";

export const websocketMsgReceivedAction = createAction<
  string | null | undefined
>(WS_MESSAGE_RECEIVED);
