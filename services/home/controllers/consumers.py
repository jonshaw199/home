from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
import logging
import json
from devices.models import Device
from core.models import Profile


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
            # self.send_json({"error": "Invalid JSON"})
            # self.close()
        except ValueError as e:
            logging.error(f"Invalid message; unable to process; error: {e}")

    def receive_json(self, content):
        logging.info(f"Received JSON message: {content}")
        # Nothing to do here; business logic moved to contoller
        # self.handle_json(content)
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

    def broadcast_to_location_group(self, content):
        src = content.get("src")
        src_type = content.get("src_type", "device")

        group_names = set()

        try:
            if src_type == "device":
                # Retrieve the device's location
                device = Device.objects.filter(uuid=src).values("location__id").first()
                if device and "location__id" in device:
                    group_names.add(f"location_{device['location__id']}_group")
                else:
                    logging.warning(f"Location ID not found for device ID: {src}")

            elif src_type == "profile":
                # Retrieve the profile based on the UUID
                profile = (
                    Profile.objects.filter(uuid=src)
                    .prefetch_related("locations")
                    .first()
                )
                if profile:
                    for location in profile.locations.all():
                        group_names.add(f"location_{location.id}_group")
                else:
                    logging.warning(f"No profile found for ID: {src}")

        except Exception as e:
            logging.error(f"Error querying for src {src} of type {src_type}: {e}")
            return

        # Broadcast to each determined location group
        for group_name in group_names:
            if group_name in self.group_names:
                logging.info(
                    f"Broadcasting message to group; message: {content}; group: {group_name}"
                )
                content["sender"] = self.channel_name
                async_to_sync(self.channel_layer.group_send)(
                    group_name, {"type": "group_message", "message": content}
                )
