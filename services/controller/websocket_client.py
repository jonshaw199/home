import os
import websocket
import rel
from dotenv import load_dotenv
from auth import Auth
import logging
import time

load_dotenv()
HOME_HOST = os.getenv("HOME_HOST")
HOME_PORT = os.getenv("HOME_PORT")


class WebsocketClient:
    def __init__(self, message_handler):
        self.message_handler = message_handler
        self.ws = None
        self.connect()

    def connect(self):
        try:
            token = Auth().get_token()
        except Exception as e:
            logging.error("Failed to get auth token")
            return

        websocket.enableTrace(True)

        try:
            self.ws = websocket.WebSocketApp(
                f"ws://{HOME_HOST}:{HOME_PORT}/ws/controllers?token={token}",
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
            )
        except Exception as e:
            logging.error("Failed to connect to websocket server")

    def on_message(self, ws, message):
        self.message_handler(message)

    def on_error(self, ws, error):
        logging.error(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        logging.info(
            f"### Connection closed (status: {close_status_code}, message: {close_msg}). ###"
        )
        self.ws = None

    def on_open(self, ws):
        logging.info("Opened connection")

    def send(self, message):
        logging.info(f"Sending websocket message: {message}")
        if self.ws:
            try:
                self.ws.send(message)
            except Exception as e:
                logging.error(f"Send failed: {e}")
                self.ws.close()
                self.ws = None
        else:
            logging.warn("Unable to send; not connected")

    def start(self):
        while 1:
            while self.ws:
                try:
                    self.ws.run_forever(
                        dispatcher=rel,
                        ping_interval=30,
                        ping_timeout=10,
                        ping_payload="keepalive",
                        # https://github.com/websocket-client/websocket-client/issues/863#issuecomment-1261353428
                        reconnect=5,
                    )
                except:
                    pass

            logging.warn("Attempting to reconnect to websocket...")
            self.connect()
            if not self.ws:
                logging.error(
                    "Failed to connect to websocket; sleeping then trying again..."
                )
                time.sleep(5)
