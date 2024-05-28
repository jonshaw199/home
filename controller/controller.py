#!/usr/bin/env python3

import subprocess
import json
import logging
from websocket_client import WebsocketClient

def build_topic(message):
    json_msg = json.loads(message)
    is_valid = {"location", "device_type", "device_id"} <= json_msg.keys()
    if not is_valid:
        logging.error("Invalid message; missing keys")
        return
    location = json_msg["location"]
    device_type = json_msg["device_type"]
    device_id = json_msg["device_id"]
    return f"{location}/{device_type}/{device_id}"

def message_handler(message):
    logging.info("Handle message: %s", message)
    topic = build_topic(message)
    if topic:
        subprocess.run([
            'mosquitto_pub',
            '-t',
            topic,
            '-m',
            message
        ], check=True)
    else:
        logging.error("Cannot publish; invalid topic")

if __name__ == "__main__":
    websocket_client = WebsocketClient(message_handler)
    websocket_client.connect_ws()
