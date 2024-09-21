from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
import logging
import json
from devices.models import Device
from datetime import datetime
from django.db import transaction

"""
Expected message shape:

{
    "src": string, // This is typically the ID of the source device
    "dest": string, // For WS<->MQTT, this is the topic
    "action": string, // i.e. "get-status", "set", etc.
    "body": {
        ... // Optional data to include with the action
    }
}
"""

HANDLER_SYSTEM_STATUS = "system__status"
HANDLER_ENVIRONMENTAL_STATUS = "environmental__status"
HANDLER_DIAL_STATUS = "dial__status"
HANDLER_PLUG_STATUS = "plug__status"


class BaseMessageHandler:
    handlers = {}

    @classmethod
    def register(cls, message_type):
        def decorator(handler_cls):
            cls.handlers[message_type] = handler_cls()
            return handler_cls

        return decorator

    def handle(self, content, consumer):
        raise NotImplementedError("Handle method not implemented.")


@BaseMessageHandler.register(HANDLER_ENVIRONMENTAL_STATUS)
class EnvironmentalStatusMessageHandler(BaseMessageHandler):
    @staticmethod
    def update_environmental(data):
        try:
            # Update fields with data from JSON object
            src = data.get("src")
            body = data.get("body")
            device = Device.objects.get(uuid=src)
            device.last_status_update = datetime.now()
            device.environmental.temperature_c = body.get("temperature_c")
            device.environmental.humidity = body.get("humidity")
            with transaction.atomic():
                device.save()
                device.environmental.save()
        except Exception as e:
            logging.error(
                f"An error occurred when processing environmental status message: {e}"
            )

    def handle(self, content, consumer):
        logging.info(f"Handling environmental status message: {content}")
        EnvironmentalStatusMessageHandler.update_environmental(content)
        consumer.broadcast_to_location_group(content)


@BaseMessageHandler.register(HANDLER_DIAL_STATUS)
class DialStatusMessageHandler(BaseMessageHandler):
    @staticmethod
    def update_device(data):
        try:
            # Update fields with data from JSON object
            src = data.get("src")
            # body = data.get("body") # No body
            device = Device.objects.get(uuid=src)
            device.last_status_update = datetime.now()
            device.save()
        except Exception as e:
            logging.error(f"An error occurred when processing dial status message: {e}")

    def handle(self, content, consumer):
        logging.info(f"Handling environmental status message: {content}")
        DialStatusMessageHandler.update_device(content)
        consumer.broadcast_to_location_group(content)


@BaseMessageHandler.register(HANDLER_SYSTEM_STATUS)
class SystemStatusMessageHandler(BaseMessageHandler):
    @staticmethod
    def update_system(data):
        try:
            # Update fields with data from JSON object
            src = data.get("src")
            body = data.get("body")
            device = Device.objects.get(uuid=src)
            device.last_status_update = datetime.now()
            device.system.cpu_usage = body.get("cpu_usage", device.system.cpu_usage)
            device.system.cpu_temp = body.get("cpu_temperature", device.system.cpu_temp)
            device.system.mem_usage = body.get("memory_usage", device.system.mem_usage)
            device.system.disk_usage = body.get("disk_usage", device.system.disk_usage)
            device.system.network_sent = body.get(
                "network_sent", device.system.network_sent
            )
            device.system.network_received = body.get(
                "network_received", device.system.network_received
            )
            with transaction.atomic():
                device.save()
                device.system.save()
        except Exception as e:
            logging.error(
                f"An error occurred when processing system status message: {e}"
            )

    def handle(self, content, consumer):
        logging.info(f"Handling system status message: {content}")
        SystemStatusMessageHandler.update_system(content)
        consumer.broadcast_to_location_group(content)


@BaseMessageHandler.register(HANDLER_PLUG_STATUS)
class PlugStatusMessageHandler(BaseMessageHandler):
    @staticmethod
    def update_plug(data):
        try:
            src = data.get("src")
            body = data.get("body")
            device = Device.objects.get(uuid=src)
            device.last_status_update = datetime.now()
            device.plug.is_on = body.get("is_on")
            with transaction.atomic():
                device.save()
                device.plug.save()
        except Exception as e:
            logging.error(f"An error occurred when processing plug status message: {e}")

    def handle(self, content, consumer):
        logging.info(f"Handling plug status message: {content}")
        PlugStatusMessageHandler.update_plug(content)
        consumer.broadcast_to_location_group(content)


class ControllerConsumer(JsonWebsocketConsumer):
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
            logging.error("Invalid JSON")
            self.send_json({"error": "Invalid JSON"})
            # self.close()
        except ValueError as e:
            logging.error(f"Invalid message; unable to process; error: {e}")

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
            handler.handle(content, self)
        else:
            logging.warning(f"No handler found for ID: {handler_id}")

    def get_handler_id(self, content):
        return content.get("action")

    def broadcast_to_location_group(self, content):
        src = content.get("src")
        if src:
            try:
                device = Device.objects.filter(uuid=src).values("location__id").first()
            except:
                logging.error(f"Error querying for Device UUID {src}")
                return

            if device and "location__id" in device:
                group_name = f"location_{device['location__id']}_group"
                if group_name in self.group_names:
                    logging.info(
                        f"Broadcasting message to group; message: {content}; group: {group_name}"
                    )
                    content["sender"] = self.channel_name
                    async_to_sync(self.channel_layer.group_send)(
                        group_name, {"type": "group_message", "message": content}
                    )
            else:
                logging.warn(f"Location ID not found for device ID: {src}")
        else:
            logging.warn("Key 'src' does not exist; unable to broadcast")
