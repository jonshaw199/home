#!/usr/bin/env python3

import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer


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
            print("user unknown")
            self.close()

    def disconnect(self, close_code):
        if self.group_name:
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name,
                self.channel_name
            )

    # Receive message from WebSocket
    def receive_json(self, content):
        # Send message to group (temp; for testing)
        content["type"] = "group.message"
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            content
        )

    # Receive message from group
    def group_message(self, content):
        # Send message to WebSocket
        self.send_json(content)
