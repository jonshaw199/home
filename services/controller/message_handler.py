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

            # Check if data is a dictionary with an "action" key
            if not isinstance(data, dict) or "action" not in data:
                logging.warning("Received a message without an 'action'; ignoring.")
                return

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


async def get_device_resource(resource_handler, device_id):
    """Fetches the full device resource, returning a dictionary with relevant UUIDs."""
    response = await resource_handler.handle_request("GET", f"devices/{device_id}")
    if response and isinstance(response, dict):
        return response
    logging.error(f"Failed to retrieve device resource for {device_id}")
    return {}


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

    # Fetch the full device resource to get the associated UUID
    device = await get_device_resource(self.resource_handler, device_id)
    light_id = device.get("light")

    if light_id:
        # Prepare the data for the PUT request, excluding None values
        light_data = filter_none_values(
            {
                "brightness": body.get("brightness"),
                "is_on": body.get("is_on"),
                "color": body.get("color"),
            }
        )

        # Make a PUT request to update light settings
        await self.resource_handler.handle_request(
            "PUT", f"lights/{light_id}", light_data
        )
        logging.info(f"Set light settings for device {device_id}")
    else:
        logging.error(f"No light found for device {device_id}")


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
    is_on = body.get("is_on")

    # Fetch the full device resource to get the associated UUID
    device = await get_device_resource(self.resource_handler, device_id)
    plug_id = device.get("plug")

    if plug_id:
        # Prepare data for the PUT request
        plug_data = filter_none_values({"is_on": is_on})

        # Make a PUT request to update plug settings
        await self.resource_handler.handle_request("PUT", f"plugs/{plug_id}", plug_data)
        logging.info(f"Set plug status for device {device_id}")
    else:
        logging.error(f"Plug not found for device {device_id}")


@register_handler(HANDLER_ENVIRONMENTAL_STATUS)
async def handle_environmental_status(self, message):
    logging.info("Handling environmental status message")
    """Handles updating the environmental sensor status."""
    body = message.get("body")
    src = message.get("src")

    # Fetch the full device resource to get the associated UUID
    device = await get_device_resource(self.resource_handler, src)
    environmental_id = device.get("environmental")

    if environmental_id:
        environmental_data = filter_none_values(
            {
                "temperature_c": body.get("temperature_c"),
                "humidity": body.get("humidity"),
            }
        )
        # Make a PUT request to update environmental sensor settings
        await self.resource_handler.handle_request(
            "PUT", f"environmentals/{environmental_id}", environmental_data
        )
        logging.info(f"Updated environmental sensor for device {src}")
    else:
        logging.error(f"No environmental found for device {src}")


@register_handler(HANDLER_DIAL_STATUS)
async def handle_dial_status(self, message):
    logging.info("Handling dial status message")
    """Handles updating the dial device status."""
    src = message.get("src")

    # Fetch the full device resource to get the associated UUID
    device = await get_device_resource(self.resource_handler, src)
    dial_id = device.get("dial")

    if dial_id:
        # If future data updates are needed, add to this dictionary
        dial_data = {}
        # Make a PUT request to update dial device status (currently a placeholder)
        await self.resource_handler.handle_request(
            "PUT", f"devices/{dial_id}", dial_data
        )
        logging.info(f"Updated dial status for device {src}")
    else:
        logging.error(f"No dial found for device {src}")


@register_handler(HANDLER_SYSTEM_STATUS)
async def handle_system_status(self, message):
    logging.info(f"Handling system status message: {message}")
    """Handles updating the system status."""
    body = message.get("body")
    src = message.get("src")

    # Fetch the full device resource to get the associated UUID
    device = await get_device_resource(self.resource_handler, src)
    system_id = device.get("system")

    if system_id:
        system_data = filter_none_values(
            {
                "cpu_usage": body.get("cpu_usage"),
                "cpu_temp": body.get("cpu_temperature"),
                "mem_usage": body.get("memory_usage"),
                "disk_usage": body.get("disk_usage"),
                "network_sent": body.get("network_sent"),
                "network_received": body.get("network_received"),
            }
        )
        # Make a PUT request to update system metrics
        await self.resource_handler.handle_request(
            "PUT", f"systems/{system_id}", system_data
        )
        logging.info(f"Updated system metrics for device {src}")
    else:
        logging.error(f"No system found for device {src}")


@register_handler(HANDLER_PLUG_STATUS)
async def handle_plug_status(self, message):
    logging.info("Handling plug status message")
    """Handles updating the plug's on/off status."""
    body = message.get("body")
    src = message.get("src")

    # Fetch the full device resource to get the associated UUID
    device = await get_device_resource(self.resource_handler, src)
    plug_id = device.get("plug")

    if plug_id:
        plug_data = filter_none_values({"is_on": body.get("is_on")})
        # Make a PUT request to update plug status
        await self.resource_handler.handle_request("PUT", f"plugs/{plug_id}", plug_data)
        logging.info(f"Updated plug status for device {src}")
    else:
        logging.error(f"No plug found for device {src}")
