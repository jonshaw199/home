#!/usr/bin/env python3

import json
import logging
from websocket_client import WebsocketClient
from mqtt_client import MqttClient
from threading import Thread

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(threadName)s] [%(filename)s:%(lineno)d] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()],
)

ROOT_TOPIC = "ROOT_TOPIC"
INTEGRATION_ACTION = "integration"


class Controller:
    def __init__(self):
        self.websocket_client = WebsocketClient(self.handle_message_ws)
        self.mqtt_client = MqttClient(
            self.handle_connect_mqtt, self.handle_message_mqtt
        )

    def handle_message_ws(self, message):
        logging.info("Handle message: %s", message)
        parsed = json.loads(message)
        topic = parsed["dest"] if "dest" in parsed else ROOT_TOPIC
        # Our devices use a standardized json payload but not integrated ones
        if parsed.get("action") == INTEGRATION_ACTION:
            body = parsed.get("body")
            if isinstance(body, dict):
                to_send = json.dumps(parsed["body"])
            elif isinstance(body, str):
                to_send = body
            else:
                to_send = ""
        else:
            to_send = message
        self.mqtt_client.publish(topic, to_send)

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
