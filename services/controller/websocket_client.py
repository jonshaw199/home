import os
import websocket
import rel
from dotenv import load_dotenv
from auth import Auth
import logging
import time
from collections import deque

load_dotenv()
HOME_HOST = os.getenv("HOME_HOST")
HOME_PORT = os.getenv("HOME_PORT")


class WebsocketClient:
    def __init__(self, message_handler):
        self.message_handler = message_handler
        self.message_queue = deque()  # Queue to store unsent messages
        self.ws = None
        self.is_reconnecting = False
        self.max_queue_size = 100  # Limit the queue size to 100 messages
        self.connect()

    def connect(self):
        token = Auth().get_token()
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            f"ws://{HOME_HOST}:{HOME_PORT}/ws/controllers?token={token}",
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

    def on_message(self, ws, message):
        self.message_handler(message)

    def on_error(self, ws, error):
        logging.error(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        logging.info(
            f"### Connection closed (status: {close_status_code}, message: {close_msg}). Reconnecting... ###"
        )
        self.reconnect()

    def reconnect(self):
        if not self.is_reconnecting:
            self.is_reconnecting = True
            while True:
                try:
                    logging.info("Attempting to reconnect...")
                    self.connect()
                    self.ws.run_forever(dispatcher=rel)
                    break  # Break loop if reconnection succeeds
                except Exception as e:
                    logging.error(f"Reconnection failed: {e}. Retrying in 5 seconds...")
                    time.sleep(5)
            self.is_reconnecting = False

    def on_open(self, ws):
        logging.info("Opened connection")
        self.resend_queued_messages()

    def send(self, message):
        logging.info(f"Sending websocket message: {message}")
        try:
            self.ws.send(message)
        except Exception as e:
            logging.error(f"Send failed: {e}")
            self.queue_message(message)  # Queue the message for retry
            self.ws.close()

    # Queue the message with a size limit
    def queue_message(self, message):
        if len(self.message_queue) >= self.max_queue_size:
            logging.warning("Message queue size exceeded. Removing oldest message.")
            self.message_queue.popleft()  # Remove the oldest message
        self.message_queue.append(message)  # Add new message to the queue

    def resend_queued_messages(self):
        while self.message_queue:
            message = self.message_queue.popleft()
            logging.info(f"Resending queued message: {message}")
            self.send(message)

    def start(self):
        self.ws.run_forever(
            dispatcher=rel, ping_interval=30, ping_timeout=10, ping_payload="keepalive"
        )
        rel.signal(2, rel.abort)  # Handle Keyboard Interrupt (Ctrl+C)
        rel.dispatch()
