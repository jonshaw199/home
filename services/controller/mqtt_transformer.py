import re
import logging


class MqttTransformerRegistry:
    transformers = {}

    @classmethod
    def register(cls, pattern):
        def decorator(transformer_callback):
            cls.transformers[pattern] = transformer_callback
            return transformer_callback  # Return the callback unmodified

        return decorator

    @classmethod
    def transform(cls, message, topic):
        dest = topic

        # Check if a transformer exists by matching regex patterns against 'dest'
        for pattern, transformer in cls.transformers.items():
            if re.match(pattern, dest):
                logging.info(f"Applying transformer for pattern: {pattern}")
                # Apply the transformer and return the transformed message
                transformed_message = transformer(message, topic)
                return transformed_message

        # If no transformer is found, return the original message
        logging.info("No transformer found; returning")
        return message
