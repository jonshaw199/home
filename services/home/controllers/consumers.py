from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
import logging
import json
from devices.models import Device
from datetime import datetime

SHELLY_PLUG_ID_PREFIX = "shellyplugus"


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


@BaseMessageHandler.register("devices__device_status")
class DeviceStatusMessageHandler(BaseMessageHandler):
    @staticmethod
    def update_device(data):
        device_id = data.get("device_id")
        if device_id is None:
            raise ValueError("Device ID is required")

        # Retrieve the device instance
        try:
            device = Device.objects.get(pk=device_id)
        except Device.DoesNotExist:
            raise ValueError(f"Device with ID {device_id} does not exist")

        if hasattr(device, "system"):
            # Update fields with data from JSON object
            device.system.cpu_usage = data.get("cpu_usage", device.system.cpu_usage)
            device.system.cpu_temp = data.get("cpu_temperature", device.system.cpu_temp)
            device.system.mem_usage = data.get("memory_usage", device.system.mem_usage)
            device.system.disk_usage = data.get("disk_usage", device.system.disk_usage)
            device.system.network_sent = data.get(
                "network_sent", device.system.network_sent
            )
            device.system.network_received = data.get(
                "network_received", device.system.network_received
            )
            # device.system.status_updated_at = datetime.now()  # Update the status_updated_at field

            # Save the updated device instance
            device.system.save()
        else:
            logging.warn(f"System not found for Device ID {device_id}")

    def handle(self, content):
        logging.info(f"Handling device status message: {content}")
        DeviceStatusMessageHandler.update_device(content)


@BaseMessageHandler.register("shellyplugs__NotifyStatus")
class ShellyPlugStatusMessageHandler(BaseMessageHandler):
    def handle(self, content):
        logging.info(f"Handling Shelly Plug status message: {content}")


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
            logging.error("Invalid JSON; closing connection")
            self.send_json({"error": "Invalid JSON; closing connection..."})
            self.close()
        except ValueError:
            logging.error("Invalid message; unable to process")

    def receive_json(self, content):
        logging.info(f"Received JSON message: {content}")
        self.handle_json(content)
        self.broadcast_to_location_group(content)

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
        # Shelly
        if (
            "src" in content
            and "method" in content
            and content.get("src").startswith(SHELLY_PLUG_ID_PREFIX)
        ):
            return f'shellyplugs__{content.get("method")}'

        # Other integrations...

        # Internal
        domain = content.get("msg_domain")
        type = content.get("msg_type")
        return "__".join([x for x in [domain, type] if x is not None])

    def broadcast_to_location_group(self, content):
        # Get location_id from content, otherwise query for location_id using given device_id
        # Need either location_id or device_id
        location_id = content.get("location_id")
        if not location_id:
            device_id = content.get("device_id")
            if device_id:
                data = (
                    Device.objects.filter(pk=device_id).values("location__id").first()
                )
                if "location__id" in data:
                    location_id = data["location__id"]
                else:
                    logging.warn(f"Location ID not found for device ID: {device_id}")
        if location_id:
            group_name = f"location_{location_id}_group"
            if group_name in self.group_names:
                logging.info(
                    f"Broadcasting message to group; message: {content}; group: {group_name}"
                )
                content["sender"] = self.channel_name
                async_to_sync(self.channel_layer.group_send)(
                    group_name, {"type": "group_message", "message": content}
                )
            else:
                logging.warn(f"User not part of group for location {location_id}")
        else:
            logging.error(
                "Location ID not provided or cannot be determined; unable to broadcast message"
            )
