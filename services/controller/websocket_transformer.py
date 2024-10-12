import json
import re
import logging

ACTION_PLUG_SET = "plug__set"
ACTION_LIGHT_SET = "light__set"

LIGHT_PREFIX = "wled"


class WebsocketTransformerRegistry:
    transformers = {}

    @classmethod
    def register(cls, pattern):
        """
        Class method to register a transformer based on a regex pattern.
        :param pattern: A regex pattern for matching message['dest']
        """

        def decorator(transformer_callback):
            cls.transformers[pattern] = transformer_callback
            return transformer_callback  # Return the callback unmodified

        return decorator

    # Call back with transformed message instead of returning to handle cases where 1 original message equals multiple transformed messages
    @classmethod
    def transform(cls, message, cb, **kwargs):
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
            for pattern, transformer in cls.transformers.items():
                if re.match(pattern, dest):
                    logging.info(f"Applying transformer for pattern: {pattern}")
                    # Apply the transformer and get the transformed message and destination
                    return transformer(message_json, cb, **kwargs)

            # If no transformer is found, use the original message and topic
            logging.info("No transformer found; consuming as-is")
            cb(message, dest)

        except Exception as e:
            logging.error(f"Error transforming message: {e}")


@WebsocketTransformerRegistry.register(r"^plugs/[0-9a-fA-F-]{36}/command$")
def transform_plug_message(message, cb, **kwargs):
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


@WebsocketTransformerRegistry.register(r"^lights/[0-9a-fA-F-]{36}/command$")
def transform_light_message(message, cb, **kwargs):
    logging.info("Transforming light message")
    action = message["action"]
    devices = kwargs.get("devices", {})

    if action == ACTION_LIGHT_SET:
        body = message["body"]
        device_id = body["device_id"]
        if device_id in devices:
            device = devices[device_id]
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
            logging.error(f"Device ID {device_id} not found in devices")
    else:
        logging.info(f"Leaving plug message as-is for action: {action}")
        cb(message, message["dest"])
