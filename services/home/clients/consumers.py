from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
import logging
import json

"""
Expected message shape:

{
    "action": string, // i.e. "turn on light"
    "body": string | null
}
"""


class BaseMessageHandler:
    handlers = {}

    @classmethod
    def register(cls, message_type):
        def decorator(handler_cls):
            cls.handlers[message_type] = handler_cls()
            return handler_cls

        return decorator

    def handle(self, content):
        raise NotImplementedError("Handle method not implemented.")


class ClientConsumer(JsonWebsocketConsumer):
    def __init__(self):
        self.group_names = []  # List to store multiple group names
        super().__init__()

    def connect(self):
        user = self.scope["user"]

        if user.is_authenticated:
            accessible_location_ids = self.get_accessible_location_ids(user)
            for location_id in accessible_location_ids:
                group_name = f"location_{location_id}_group"
                if group_name not in self.group_names:
                    self.group_names.append(group_name)
                    async_to_sync(self.channel_layer.group_add)(
                        group_name, self.channel_name
                    )
            self.accept()
        else:
            logging.error("User unknown; closing connection")
            self.close()

    def disconnect(self, close_code):
        for group_name in self.group_names:
            async_to_sync(self.channel_layer.group_discard)(
                group_name, self.channel_name
            )

    def receive(self, text_data=None, bytes_data=None):
        logging.info(f"Received message: {text_data}")
        try:
            content = json.loads(text_data)
            if isinstance(content, dict):
                self.receive_json(content)
            else:
                raise ValueError(f"JSON content is not a dict: {content}")
        except json.JSONDecodeError:
            logging.error("Invalid JSON; closing connection")
            self.send_json({"error": "Invalid JSON; closing connection..."})
            self.close()
        except ValueError:
            logging.error("Invalid message; unable to process")

    def receive_json(self, content):
        logging.info(f"Received JSON message: {content}")
        self.handle_json(content)
        # self.broadcast_to_location_group(content)

    def group_message(self, event):
        message = event["message"]

        # Skip sending the message to the sender
        if message.get("sender") != self.channel_name:
            self.send_json(message)

    def get_accessible_location_ids(self, user):
        # Ensure the user has a profile and locations associated with it
        if hasattr(user, "profile"):
            # Get the locations directly assigned to the user
            user_locations = user.profile.locations.all()

            # Initialize an empty set to collect unique location IDs
            accessible_location_ids = set()

            # Loop through each location and get its descendants (including itself)
            for location in user_locations:
                descendant_ids = location.get_descendants(
                    include_self=True
                ).values_list("id", flat=True)
                # Add the IDs to the set (to ensure uniqueness)
                accessible_location_ids.update(descendant_ids)

            return accessible_location_ids

        # If the user has no profile or locations, return an empty set
        return set()

    def handle_json(self, content):
        handler_id = self.get_handler_id(content)
        handler = BaseMessageHandler.handlers.get(handler_id)
        if handler:
            handler.handle(content)
        else:
            logging.warning(f"No handler found for ID: {handler_id}")

    def get_handler_id(self, content):
        return content.get("action")
