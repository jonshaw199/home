class WebSocketManager {
  private static instance: WebSocketManager;
  private socket: WebSocket | null = null;
  private messageListeners: ((message: string) => void)[] = [];

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

    console.log(url);
    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      console.log("WebSocket connection opened");
    };

    this.socket.onmessage = (event: WebSocketMessageEvent) => {
      const message = event.data;
      console.log("Received message:", message);
      this.messageListeners.forEach((listener) => listener(message));
    };

    this.socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    this.socket.onclose = () => {
      console.log("WebSocket connection closed");
      this.socket = null;
    };
  }

  // Send a message through the WebSocket
  public sendMessage(message: string) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(message);
    } else {
      console.error("WebSocket is not open");
    }
  }

  // Add a listener to receive messages
  public addMessageListener(listener: (message: string) => void) {
    this.messageListeners.push(listener);
  }

  // Remove a message listener
  public removeMessageListener(listener: (message: string) => void) {
    this.messageListeners = this.messageListeners.filter((l) => l !== listener);
  }

  // Close the WebSocket connection
  public disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

export default WebSocketManager;
