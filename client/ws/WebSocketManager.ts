type Listener = {
  onMessage?: (message: string) => void;
  onError?: (event: Event) => void;
  onClose?: (event: CloseEvent) => void;
};

class WebSocketManager {
  private static instance: WebSocketManager;
  private socket: WebSocket | null = null;
  private listeners: Listener[] = [];

  private constructor() {
    // Private constructor for Singleton pattern
  }

  // Get the singleton instance of the WebSocketManager
  public static getInstance(): WebSocketManager {
    if (!WebSocketManager.instance) {
      WebSocketManager.instance = new WebSocketManager();
    }
    return WebSocketManager.instance;
  }

  // Connect to the WebSocket server
  public connect(url: string) {
    if (this.socket) {
      console.warn("WebSocket is already connected");
      return;
    }

    console.log("Connecting to WebSocket at", url);
    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      console.log("WebSocket connection opened");
    };

    this.socket.onmessage = (event: WebSocketMessageEvent) => {
      const message = event.data;
      console.log("Received message:", message);
      this.listeners.forEach(
        ({ onMessage }) => onMessage && onMessage(message)
      );
    };

    this.socket.onerror = (event) => {
      console.error("WebSocket error:", event);
      this.listeners.forEach(({ onError }) => onError && onError(event));
    };

    this.socket.onclose = (event) => {
      console.log("WebSocket connection closed");
      this.socket = null;
      this.listeners.forEach(({ onClose }) => onClose && onClose(event));
    };
  }

  // Send a message through the WebSocket, queue if not open
  public sendMessage(message: string) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      console.log("Sending WebSocket message:", message);
      this.socket.send(message);
    } else {
      console.error("WebSocket is not open; unable to send message: ", message);
    }
  }

  // Add a listener to receive messages
  public addListener(listener: Listener) {
    this.listeners.push(listener);
  }

  // Remove a message listener
  public removeListener(listener: Listener) {
    this.listeners = this.listeners.filter((l) => l !== listener);
  }

  // Close the WebSocket connection and stop reconnecting
  public disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

export default WebSocketManager;
