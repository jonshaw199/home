from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
import logging
import json
from devices.models import Device

"""
Expected message shape:

{
    "src": string, // This is typically the ID of the source device
    "dest": string, // For WS<->MQTT, this is the topic
    "action": string, // i.e. "get-status", "set", etc.
    "body": {
        <cpu_usage>,
        <cpu_temperature>,
        <memory_usage>,
        <disk_usage>,
        <network_sent>,
        <network_received>
    }
}
"""

SHELLY_PLUG_ID_PREFIX = "shellyplugus"


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


@BaseMessageHandler.register("system__status")
class DeviceStatusMessageHandler(BaseMessageHandler):
    @staticmethod
    def update_device(data):
        src = data.get("src")
        if src is None:
            raise ValueError("src is required")

        # Retrieve the device instance
        try:
            device = Device.objects.get(uuid=src)
        except Device.DoesNotExist:
            raise ValueError(f"Device with UUID {src} does not exist")

        if not hasattr(device, "system"):
            logging.warn(f"System not found for Device UUID {src}")
            return

        body = data.get("body")

        if body is None:
            logging.warn("Status not provided")
            return

        # Update fields with data from JSON object
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
        # device.system.status_updated_at = datetime.now()  # Update the status_updated_at field

        # Save the updated device instance
        device.system.save()

    def handle(self, content, consumer):
        logging.info(f"Handling device status message: {content}")
        DeviceStatusMessageHandler.update_device(content)
        consumer.broadcast_to_location_group(content)


@BaseMessageHandler.register("shellyplugs__NotifyStatus")
class ShellyPlugStatusMessageHandler(BaseMessageHandler):
    def handle(self, content, consumer):
        logging.info(f"Handling Shelly Plug status message: {content}")
        # TODO: adapt message content, then call `broadcast` with it


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
        # Shelly
        if (
            "src" in content
            and "method" in content
            and content.get("src").startswith(SHELLY_PLUG_ID_PREFIX)
        ):
            return f'shellyplugs__{content.get("method")}'

        # Other integrations...

        # Internal
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
