#!/usr/bin/env python3

import json
import logging
from websocket_client import WebsocketClient
from mqtt_client import MqttClient
from threading import Thread

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(threadName)s] [%(filename)s:%(lineno)d] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Topics: 
#   - location_id/domain_id/device_id
#   - location_id/domain_id
#   - location_id
#   - <root topic>
#   - location_id/domain_id/device_id/something/else...   <--- Can do something like this in future if necessary
RESERVED_MSG_KEYS = ["location_id", "domain_id", "device_id"]
ROOT_TOPIC = "ROOT_TOPIC"

class Controller:
    def __init__(self):
        self.websocket_client = WebsocketClient(self.handle_message_ws)
        self.mqtt_client = MqttClient(self.handle_connect_mqtt, self.handle_message_mqtt)
        
    def handle_message_ws(self, message):
        logging.info("Handle message: %s", message)
        topic = self.build_topic(message)
        if topic:
            self.mqtt_client.publish(topic, message)
        else:
            # Assuming the message isn't important to the server if no topic
            logging.error(f"Cannot publish websocket message to mqtt (no topic provided): {message}")

    def handle_connect_mqtt(self):
        # Subscribe to everything; our job is to keep the server in the loop
        self.mqtt_client.subscribe("#")

    def handle_message_mqtt(self, topic, message):
        logging.info("Handle message: %s", message)
        # We are subscribed to everything; pass along messages to server
        # TODO: Do we need to include "topic" as well?
        self.websocket_client.send(message)

    def build_topic(self, message):
        json_msg = json.loads(message)
        # {location_id: 1, domain_id: 2, device_id: 3} -> [1, 2, 3]
        # {location_id: 1, domain_id: 2} -> [1, 2]
        # {location_id: 1, device_id: 3} -> [1]
        # {device_id: 2} -> []
        arr = []
        for k in RESERVED_MSG_KEYS:
          if k in message and message[k]:
            arr.append(message[k])
          else:
            break
        return '/'.join(arr) if arr else ROOT_TOPIC

    def start(self):
        mqtt_thread = Thread(target=self.mqtt_client.start)
        mqtt_thread.name = 'MQTT Client Thread'
        mqtt_thread.start()
        self.websocket_client.start()

if __name__ == "__main__":
    Controller().start()

