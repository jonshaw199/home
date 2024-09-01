from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
import logging
import json

class ControllerConsumer(JsonWebsocketConsumer):
    def __init__(self):
        self.group_names = []  # List to store multiple group names
        super().__init__()

    def connect(self):
        user = self.scope['user']

        if user.is_authenticated:
            accessible_locations = self.get_accessible_locations(user)
            for location_id in accessible_locations:
                group_name = f'location_{location_id}_group'
                if group_name not in self.group_names:
                    self.group_names.append(group_name)
                    async_to_sync(self.channel_layer.group_add)(
                        group_name,
                        self.channel_name
                    )
            self.accept()
        else:
            logging.warn("User unknown; closing connection")
            self.close()

    def disconnect(self, close_code):
        for group_name in self.group_names:
            async_to_sync(self.channel_layer.group_discard)(
                group_name,
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

    def receive_json(self, content):
        logging.info(f"Received JSON message: {content}")

        # Example: Perform a database operation (stubbed here)
        self.perform_database_operation(content)

        device_id = content.get('device_id')
        if device_id:
          location_id = None # TODO
          group_name = f'location_{location_id}_group'
          if group_name in self.group_names:
              async_to_sync(self.channel_layer.group_send)(
                  group_name,
                  {
                      'type': 'group_message',
                      'message': content
                  }
              )
          else:
              logging.warn(f"User not part of group for location {location_id}")
        else:
          logging.warn('Device ID not provided; cannot process message')

    def group_message(self, event):
        # Send message to WebSocket
        self.send_json(event['message'])

    def get_accessible_locations(self, user):
        # Placeholder method to get accessible locations
        # Replace with actual logic to retrieve user's accessible locations
        return [1, 2, 3]  # Example

    def perform_database_operation(self, content):
        # Placeholder for database operation
        # Implement the actual DB operation you need
        logging.info("Performing a database operation with the content")

