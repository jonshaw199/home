#!/usr/bin/env python3

import os
import websocket
import rel
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

class WebsocketClient:
    def __init__(self, message_handler):
        self.message_handler = message_handler

    def on_message(self, ws, message):
        self.message_handler(message)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(self, ws):
        print("Opened connection")

    def connect_ws(self):
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(
            f'ws://localhost:8000/ws/controllers?token={TOKEN}',
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

        ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
        rel.signal(2, rel.abort)  # Keyboard Interrupt
        rel.dispatch()
