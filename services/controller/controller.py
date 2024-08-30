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
            logging.error("Cannot publish; invalid topic")

    def handle_connect_mqtt(self):
        self.mqtt_client.subscribe("*")

    def handle_message_mqtt(self, topic, message):
        logging.info("Handle message: %s", message)
        self.websocket_client.send(message)

    def build_topic(self, message):
        json_msg = json.loads(message)
        is_valid = {"location", "device_type", "device_id"} <= json_msg.keys()
        if not is_valid:
            logging.error("Invalid message; missing keys")
            return
        location = json_msg["location"]
        device_type = json_msg["device_type"]
        device_id = json_msg["device_id"]
        return f"{location}/{device_type}/{device_id}"

    def start(self):
        mqtt_thread = Thread(target=self.mqtt_client.start)
        mqtt_thread.name = 'MQTT Client Thread'
        mqtt_thread.start()
        self.websocket_client.start()

if __name__ == "__main__":
    Controller().start()

