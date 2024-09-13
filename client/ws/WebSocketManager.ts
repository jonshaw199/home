class WebSocketManager {
  private static instance: WebSocketManager;
  private socket: WebSocket | null = null;
  private messageListeners: ((message: string) => void)[] = [];
  private reconnectInterval: number = 5000; // 5 seconds
  private isReconnecting: boolean = false;
  private shouldReconnect: boolean = true; // To control reconnect attempts
  private queuedMessages: string[] = []; // To queue unsent messages
  private readonly maxQueueSize: number = 100; // Limit the queue size to 100

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
      this.isReconnecting = false;
      this.resendQueuedMessages(); // Resend any queued messages
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

      if (this.shouldReconnect) {
        this.reconnect(url);
      }
    };
  }

  // Reconnect to the WebSocket server after a delay
  private reconnect(url: string) {
    if (this.isReconnecting) return;

    this.isReconnecting = true;

    console.log(
      `Attempting to reconnect in ${this.reconnectInterval / 1000} seconds...`
    );
    setTimeout(() => {
      console.log("Reconnecting to WebSocket...");
      this.connect(url);
    }, this.reconnectInterval);
  }

  // Send a message through the WebSocket, queue if not open
  public sendMessage(message: string) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      console.log("Sending WebSocket message:", message);
      this.socket.send(message);
    } else {
      console.error("WebSocket is not open. Queuing message:", message);
      this.queueMessage(message); // Queue the message
    }
  }

  // Add a message to the queue, and enforce the queue size limit
  private queueMessage(message: string) {
    if (this.queuedMessages.length >= this.maxQueueSize) {
      console.warn("Message queue size exceeded. Removing oldest message.");
      this.queuedMessages.shift(); // Remove the oldest message from the front of the queue
    }
    this.queuedMessages.push(message);
  }

  // Resend queued messages
  private resendQueuedMessages() {
    while (this.queuedMessages.length > 0) {
      const message = this.queuedMessages.shift(); // Get the first queued message
      if (message) {
        this.sendMessage(message); // Attempt to send it again
      }
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

  // Close the WebSocket connection and stop reconnecting
  public disconnect() {
    this.shouldReconnect = false; // Stop reconnect attempts
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

export default WebSocketManager;
