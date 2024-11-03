import json
import re
import logging

ACTION_PLUG_SET = "plug__set"
ACTION_LIGHT_SET = "light__set"

LIGHT_PREFIX = "wled"

import json
import re
import logging


class WebsocketTransformerRegistry:
    def __init__(self, resource_handler):
        self.transformers = {}
        self.resource_handler = resource_handler

    def register(self, pattern):
        def decorator(transformer_callback):
            self.transformers[pattern] = transformer_callback
            return transformer_callback

        return decorator

    # Call back with transformed message instead of returning to handle cases where 1 original message equals multiple transformed messages
    async def transform(self, message, cb):
        """
        Transforms the message if a matching transformer exists and returns the transformed
        message and its destination topic. If no transformer is found, the original message and
        'dest' field from the message are returned.
        :param message: The message string to transform.
        :return: (transformed_message, topic) as strings.
        """
        try:
            # Convert the message string to JSON object for pattern matching on 'dest'
            message_json = json.loads(message)
            dest = message_json.get("dest", "")
            # Check if a transformer exists by matching regex patterns against 'dest'
            for pattern, transformer in self.transformers.items():
                if re.match(pattern, dest):
                    logging.info(f"Applying transformer for pattern: {pattern}")
                    # Apply the transformer and get the transformed message and destination
                    return await transformer(message_json, cb)
            # If no transformer is found, use the original message and topic
            logging.info("No transformer found; consuming as-is")
            cb(message, dest)
        except Exception as e:
            logging.error(f"Error transforming message: {e}")


# Define transformers outside the class, using instance methods to register
def register_websocket_transformers(registry):
    @registry.register(r"^plugs/[0-9a-fA-F-]{36}/command$")
    async def transform_plug_message(message, cb):
        logging.info("Transform plug message")
        action = message["action"]

        if action == ACTION_PLUG_SET:
            body = message["body"]
            is_on = body["is_on"]
            device_id = body["device_id"]
            logging.info(f"Transforming plug set message; is_on: {is_on}")
            transformed = "on" if is_on else "off"
            topic = f"plugs/{device_id}/command/switch:0"
            cb(transformed, topic)
        else:
            logging.info(f"Leaving plug message as-is for action: {action}")
            cb(message, message["dest"])

    @registry.register(r"^lights/[0-9a-fA-F-]{36}/command$")
    async def transform_light_message(message, cb):
        logging.info("Transforming light message")
        action = message["action"]

        if action == ACTION_LIGHT_SET:
            body = message["body"]
            device_id = body["device_id"]
            device = await registry.resource_handler.fetch("devices", device_id)

            vendor_id = device["vendor_id"]
            if not vendor_id:
                logging.error(f"Vendor ID not found for device {device_id}")
                return

            if "is_on" in body:
                transformed = "ON" if body["is_on"] else "OFF"
                topic = f"{LIGHT_PREFIX}/{vendor_id}"
                cb(transformed, topic)
            if "brightness" in body:
                transformed = body["brightness"]
                topic = f"{LIGHT_PREFIX}/{vendor_id}"
                cb(transformed, topic)
            if "color" in body:
                transformed = body["color"]
                topic = f"{LIGHT_PREFIX}/{vendor_id}/col"
                cb(transformed, topic)

        else:
            logging.info(f"Leaving plug message as-is for action: {action}")
            cb(message, message["dest"])
