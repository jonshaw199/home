#!/usr/bin/env python3

import logging
from websocket_client import WebsocketClient
from mqtt_client import MqttClient
from threading import Thread
from webocket_transformer import WebsocketTransformerRegistry
from mqtt_transformer import MqttTransformerRegistry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] [%(filename)s:%(lineno)d] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()],
)


class Controller:
    def __init__(self):
        self.websocket_client = WebsocketClient(self.handle_message_ws)
        self.mqtt_client = MqttClient(
            self.handle_connect_mqtt, self.handle_message_mqtt
        )

    def handle_message_ws(self, message):
        logging.info("Handle message: %s", message)

        try:
            transformed_message, topic = WebsocketTransformerRegistry.transform(message)
            logging.info(
                f"Publishing transformed message {transformed_message} to topic {topic}"
            )
            self.mqtt_client.publish(topic, transformed_message)
        except Exception as e:
            logging.error(f"Error handling WS message: {e}")

    def handle_connect_mqtt(self):
        # Subscribe to everything
        self.mqtt_client.subscribe("#")

    def handle_message_mqtt(self, topic, message):
        logging.info("Handle message: %s", message)

        try:
            transformed_message = MqttTransformerRegistry.transform(message, topic)
            logging.info(f"Sending transformed message {transformed_message}")
            self.websocket_client.send(transformed_message)
        except Exception as e:
            logging.error(f"Error handling MQTT message: {e}")

    def start(self):
        mqtt_thread = Thread(target=self.mqtt_client.start)
        mqtt_thread.name = "MQTT Client Thread"
        mqtt_thread.start()
        self.websocket_client.start()


if __name__ == "__main__":
    Controller().start()
