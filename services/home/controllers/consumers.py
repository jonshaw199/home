#!/usr/bin/env python3

import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(threadName)s] [%(filename)s:%(lineno)d] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class ControllerConsumer(JsonWebsocketConsumer):
    def __init__(self):
        self.group_name = ''
        super().__init__()

    def connect(self):
        user = self.scope['user']

        if user.is_authenticated:
            self.group_name = f'group_{user.id}'
            async_to_sync(self.channel_layer.group_add)(
                self.group_name,
                self.channel_name
            )
            self.accept()
        else:
            logging.warn("User unknown; closing connection")
            self.close()

    def disconnect(self, close_code):
        if self.group_name:
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name,
                self.channel_name
            )

    def receive(self, text_data=None, bytes_data=None):
        logging.info(f"Received message: {text_data}")
        try:
            content = json.loads(text_data)
            self.receive_json(content)
        except json.JSONDecodeError:
            logging.warn("Invalid JSON; closing connection")
            self.send_json({"error": "Invalid JSON; closing connection..."})
            self.close()

    # Receive message from WebSocket
    def receive_json(self, content):
        logging.info(f"Received message: {content}")

    # Receive message from group
    def group_message(self, content):
        if "message" in content:
            # Send message to WebSocket
            self.send_json(content["message"])
        else:
            self.send_json({"error": "Invalid message; missing 'message' key"})
