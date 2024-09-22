import json
import re
import logging

ACTION_PLUG_SET = "plug__set"


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

    @classmethod
    def transform(cls, message):
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
                    transformed_message, transformed_dest = transformer(message_json)

                    # Check if the transformed message is a dictionary (i.e., it needs to be JSON serialized)
                    if isinstance(transformed_message, (dict, list)):
                        transformed_message = json.dumps(transformed_message)

                    return transformed_message, transformed_dest

            # If no transformer is found, return the original message and topic
            logging.info("No transformer found; returning")
            return message, dest

        except Exception as e:
            logging.error(f"Error transforming message: {e}")
            return message, "invalid_topic"


@WebsocketTransformerRegistry.register(r"^plugs/[0-9a-fA-F-]{36}/command$")
def transform_plug_message(message):
    action = message["action"]
    body = message["body"]
    is_on = body["is_on"]
    device_id = body["device_id"]

    if action == ACTION_PLUG_SET:
        logging.info(f"Transforming plug set message {is_on}")
        transformed = "on" if is_on else "off"
        topic = f"plugs/{device_id}/command/switch:0"
        return (transformed, topic)

    logging.warn(f"Unrecognized action: {action}")
    return (message, message["dest"])
