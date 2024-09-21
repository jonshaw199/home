#!/usr/bin/env python3

import json
import logging
import re
from websocket_client import WebsocketClient
from mqtt_client import MqttClient
from threading import Thread

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(threadName)s] [%(filename)s:%(lineno)d] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()],
)


class TransformerRegistry:
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
                    transformed_message = transformer(message_json)
                    return (
                        json.dumps(transformed_message),
                        dest,
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


@TransformerRegistry.register(r"^plugs/[0-9a-fA-F-]{36}/command$")
def transform_plug_message(message):
    # Example transformation for plug messages
    message["transformed"] = True  # Add a field for demonstration
    logging.info("Transformed plug message")
    return message


class Controller:
    def __init__(self):
        self.websocket_client = WebsocketClient(self.handle_message_ws)
        self.mqtt_client = MqttClient(
            self.handle_connect_mqtt, self.handle_message_mqtt
        )

    def handle_message_ws(self, message):
        logging.info("Handle message: %s", message)
        try:
            transformed_message, topic = TransformerRegistry.transform(
                message
            )  # Transform message and get topic
            self.mqtt_client.publish(topic, transformed_message)
        except Exception as e:
            logging.error(f"Error handling message: {e}")

    def handle_connect_mqtt(self):
        # Subscribe to everything; our job is to keep the server in the loop
        self.mqtt_client.subscribe("#")

    def handle_message_mqtt(self, topic, message):
        logging.info("Handle message: %s", message)
        # We are subscribed to everything; pass along messages to server
        self.websocket_client.send(message)

    def start(self):
        mqtt_thread = Thread(target=self.mqtt_client.start)
        mqtt_thread.name = "MQTT Client Thread"
        mqtt_thread.start()
        self.websocket_client.start()


if __name__ == "__main__":
    Controller().start()
