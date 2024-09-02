from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
import logging
import json
from devices.models import Device
from core.models import Location


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


@BaseMessageHandler.register('device_status')
class DeviceStatusMessageHandler(BaseMessageHandler):
    @staticmethod
    def update_device(data):
        device_id = data.get('device_id')
        if device_id is None:
            raise ValueError("Device ID is required")

        # Retrieve the device instance
        try:
            device = Device.objects.get(pk=device_id)
        except Device.DoesNotExist:
            raise ValueError(f"Device with ID {device_id} does not exist")

        # Update fields with data from JSON object
        device.cpu_usage = data.get('cpu_usage', device.cpu_usage)
        device.cpu_temp = data.get('cpu_temperature', device.cpu_temp)
        device.mem_usage = data.get('memory_usage', device.mem_usage)
        device.disk_usage = data.get('disk_usage', device.disk_usage)
        device.network_sent = data.get('network_sent', device.network_sent)
        device.network_received = data.get('network_received', device.network_received)
        device.status_updated_at = timezone.now()  # Update the status_updated_at field

        # Save the updated device instance
        device.save()

    def handle(self, content):
        logging.info(f"Handling device status message: {content}")
        update_device(content) 


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
            self.receive_json(content)
        except json.JSONDecodeError:
            logging.error("Invalid JSON; closing connection")
            self.send_json({"error": "Invalid JSON; closing connection..."})
            self.close()

    def receive_json(self, content):
        logging.info(f"Received JSON message: {content}")
        self.handle_json(content)
        self.broadcast_to_location_group(content) 

    def group_message(self, event):
        # Send message to WebSocket
        self.send_json(event["message"])

    def get_accessible_location_ids(self, user):
        # TODO
        # return list(Location.objects.values_list('id', flat=True))
        return [1]

    def handle_json(self, content):
        message_type = content.get('type')
        handler = BaseMessageHandler.handlers.get(message_type)

        if handler:
            handler.handle(content)
        else:
            logging.warning(f"No handler found for message type: {message_type}")

    def broadcast_to_location_group(self, content):
        # Get location_id from content, otherwise query for location_id using given device_id
        # Need either location_id or device_id
        location_id = content.get("location_id")
        if not location_id:
            device_id = content.get("device_id")
            if device_id:
                data = Device.objects.filter(pk=device_id).values('location__id').first()
                if 'location__id' in data:
                    location_id = data['location__id']
                else:
                    logging.warn(f'Location ID not found for device ID: {device_id}')
        if location_id:
            group_name = f"location_{location_id}_group"
            if group_name in self.group_names:
                async_to_sync(self.channel_layer.group_send)(
                    group_name, {"type": "group_message", "message": content}
                )
            else:
                logging.warn(f"User not part of group for location {location_id}")
        else:
            logging.error("Location ID not provided or cannot be determined; unable to broadcast message")
