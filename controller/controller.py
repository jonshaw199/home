#!/usr/bin/env python3

import subprocess
from websocket_client import WebsocketClient

def message_handler(message):
    print(message)
    subprocess.run([
        'mosquitto_pub',
        '-t',
        'test/topic',
        '-m',
        'test'
    ], check=True)

if __name__ == "__main__":
    websocket_client = WebsocketClient(message_handler)
    websocket_client.connect_ws()
