# message_handler.py

import json
import logging


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


HANDLER_PLUG_SET = "plug__set"
HANDLER_LIGHT_SET = "light__set"

HANDLER_SYSTEM_STATUS = "system__status"
HANDLER_ENVIRONMENTAL_STATUS = "environmental__status"
HANDLER_DIAL_STATUS = "dial__status"
HANDLER_PLUG_STATUS = "plug__status"


# Define a decorator for registering action handlers
def register_handler(action):
    def decorator(func):
        MessageHandler.register(action, func)
        return func

    return decorator


def filter_none_values(data):
    """Removes key-value pairs from a dictionary where the value is None."""
    return {k: v for k, v in data.items() if v is not None}


class MessageHandler:
    handlers = {}

    def __init__(self, resource_handler):
        self.resource_handler = resource_handler

    @classmethod
    def register(cls, action, func):
        """Registers a handler function for a specific action."""
        cls.handlers[action] = func

    async def handle(self, message):
        """Attempts to parse the message and dispatch to the appropriate handler based on action."""
        try:
            # Parse JSON data and extract action
            data = json.loads(message)
            action = data.get("action")

            if action in self.handlers:
                # Dispatch to the appropriate handler
                handler = self.handlers[action]
                await handler(self, data)
            else:
                logging.warning(f"No handler found for action: {action}")
        except json.JSONDecodeError:
            logging.warning("Received an invalid JSON message; ignoring.")
        except Exception as e:
            logging.error(f"An error occurred while handling the message: {e}")


"""
body: {
    "device_id": string, // UUID
    "is_on"?: boolean,
    "brightness"?: number,
    "color"?: string
}
"""


@register_handler(HANDLER_LIGHT_SET)
async def handle_light_set(self, message):
    """Handles setting brightness and other properties for lights."""
    body = message.get("body")
    device_id = body.get("device_id")

    # Prepare the data for the PUT request, excluding None values
    light_data = filter_none_values(
        {
            "brightness": body.get("brightness"),
            "is_on": body.get("is_on"),
            "color": body.get("color"),
        }
    )

    # Make a PUT request to update light settings
    await self.resource_handler.handle_request("PUT", f"lights/{device_id}", light_data)
    logging.info(f"Set light settings for device {device_id}")


"""
body: {
    "device_id": string, // UUID
    "is_on": boolean
}
"""


@register_handler(HANDLER_PLUG_SET)
async def handle_plug_set(self, message):
    """Handles setting the on/off state for plugs."""
    body = message.get("body")
    device_id = body.get("device_id")

    # Prepare data for the PUT request
    plug_data = filter_none_values({"is_on": body.get("is_on")})

    # Make a PUT request to update plug settings
    await self.resource_handler.handle_request("PUT", f"plugs/{device_id}", plug_data)
    logging.info(f"Set plug status for device {device_id}")


@register_handler(HANDLER_ENVIRONMENTAL_STATUS)
async def handle_environmental_status(self, message):
    """Handles updating the environmental sensor status."""
    body = message.get("body")
    src = body.get("src")
    environmental_data = filter_none_values(
        {
            "temperature_c": body["body"].get("temperature_c"),
            "humidity": body["body"].get("humidity"),
        }
    )
    # Make a PUT request to update environmental sensor settings
    await self.resource_handler.handle_request(
        "PUT", f"environmentals/{src}/", environmental_data
    )
    logging.info(f"Updated environmental sensor for device {src}")


@register_handler(HANDLER_DIAL_STATUS)
async def handle_dial_status(self, message):
    """Handles updating the dial device status."""
    body = message.get("body")
    src = body.get("src")

    # If future data updates are needed, add to this dictionary
    dial_data = {}

    # Make a PUT request to update dial device status (currently a placeholder)
    await self.resource_handler.handle_request("PUT", f"devices/{src}/", dial_data)
    logging.info(f"Updated dial status for device {src}")


@register_handler(HANDLER_SYSTEM_STATUS)
async def handle_system_status(self, message):
    """Handles updating the system status."""
    body = message.get("body")
    src = body.get("src")
    system_data = filter_none_values(
        {
            "cpu_usage": body["body"].get("cpu_usage"),
            "cpu_temp": body["body"].get("cpu_temperature"),
            "mem_usage": body["body"].get("memory_usage"),
            "disk_usage": body["body"].get("disk_usage"),
            "network_sent": body["body"].get("network_sent"),
            "network_received": body["body"].get("network_received"),
        }
    )
    # Make a PUT request to update system metrics
    await self.resource_handler.handle_request("PUT", f"systems/{src}/", system_data)
    logging.info(f"Updated system metrics for device {src}")


@register_handler(HANDLER_PLUG_STATUS)
async def handle_plug_status(self, message):
    """Handles updating the plug's on/off status."""
    body = message.get("body")
    src = body.get("src")
    plug_data = filter_none_values({"is_on": body["body"].get("is_on")})

    # Make a PUT request to update plug status
    await self.resource_handler.handle_request("PUT", f"plugs/{src}/", plug_data)
    logging.info(f"Updated plug status for device {src}")
