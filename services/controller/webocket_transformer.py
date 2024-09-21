import json
import re
import logging


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
                    # Apply the transformer and return the transformed message
                    transformed_message, transformed_dest = transformer(message_json)
                    return (
                        json.dumps(transformed_message),
                        transformed_dest,
                    )  # Return transformed message as a string

            # If no transformer is found, return the original message and topic
            logging.info("No transformer found; returning")
            return message, dest

        except json.JSONDecodeError:
            logging.error("Invalid JSON in message")
            return (
                message,
                "invalid_topic",
            )  # Return original message with invalid topic if parsing fails


@WebsocketTransformerRegistry.register(r"^plugs/[0-9a-fA-F-]{36}/command$")
def transform_plug_message(message):
    # Example transformation for plug messages
    message["transformed"] = True  # Add a field for demonstration
    logging.info("Transformed plug message")
    return (message, message["dest"])
