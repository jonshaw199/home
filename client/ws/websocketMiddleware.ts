// websocketMiddleware.ts
import { Middleware } from "redux";
import WebSocketManager from "./WebSocketManager"; // Import your WebSocketManager
import {
  WS_CONNECT,
  WS_DISCONNECT,
  WS_SEND_MESSAGE,
  WS_MESSAGE_RECEIVED,
} from "./websocketActionTypes";

// Define the middleware
const websocketMiddleware: Middleware = (store) => {
  const wsManager = WebSocketManager.getInstance(); // Get the WebSocketManager singleton instance

  // Listener for WebSocket messages
  const handleWebSocketMessage = (message: string) => {
    // Dispatch an action with the received message
    store.dispatch({ type: WS_MESSAGE_RECEIVED, payload: message });
  };

  return (next) => (action: any) => {
    switch (action.type) {
      case WS_CONNECT:
        // Connect to WebSocket using WebSocketManager
        wsManager.connect(action.payload.url);
        wsManager.addMessageListener(handleWebSocketMessage);
        break;

      case WS_DISCONNECT:
        // Disconnect from WebSocket using WebSocketManager
        wsManager.removeMessageListener(handleWebSocketMessage);
        wsManager.disconnect();
        break;

      case WS_SEND_MESSAGE:
        // Send a message using WebSocketManager
        wsManager.sendMessage(action.payload.message);
        break;

      default:
        break;
    }

    // Pass the action to the next middleware/reducer
    return next(action);
  };
};

export default websocketMiddleware;