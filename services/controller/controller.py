#!/usr/bin/env python3

import logging
import asyncio
import json
import os
from aiohttp import ClientSession
from dotenv import load_dotenv
from websocket_client import WebsocketClient
from mqtt_client import AsyncMqttClient
from websocket_transformer import WebsocketTransformerRegistry
from mqtt_transformer import MqttTransformerRegistry
from auth import get_token
from routine_manager import RoutineManager, fetch_routines

logging.basicConfig(level=logging.DEBUG)  # Ensure this is set at the beginning

load_dotenv()
HOME_HOST = os.getenv("HOME_HOST")
HOME_PORT = os.getenv("HOME_PORT")


def transform_devices(devices):
    return {device["uuid"]: device for device in devices}


async def fetch_devices(token):
    """Fetch routines from the API."""
    url = f"http://{HOME_HOST}:{HOME_PORT}/api/devices"
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
    }

    async with ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                devices = await response.json()
                logging.info(f"Fetched devices: {devices}")
                transformed = transform_devices(devices)
                logging.info(f"Transformed devices: {transformed}")
                return transformed
            else:
                logging.error(f"Failed to fetch devices. Status: {response.status}")
                return {}


class Controller:
    def __init__(self):
        self.websocket_client = WebsocketClient(self.handle_message_ws)
        self.mqtt_client = AsyncMqttClient(self.handle_message_mqtt)
        self.routine_manager = RoutineManager(self.handle_routine_msg)
        self.devices = {}

    def handle_routine_msg(self, routine, action, eval_data):
        logging.info("Handle routine message")

        try:
            outMsg = {
                "src": routine.get("name"),
                "dest": eval_data.get("dest"),
                "action": action,
                "body": eval_data.get("body"),
            }
            outMsgStr = json.dumps(outMsg)

            # Send to websocket server as-is
            asyncio.create_task(self.websocket_client.send(outMsgStr))

            def handle_transformed_msg(msg, topic):
                asyncio.create_task(self.mqtt_client.publish(topic, msg))

            # Transform and send to mqtt broker
            WebsocketTransformerRegistry.transform(
                outMsgStr, handle_transformed_msg, devices=self.devices
            )
        except Exception as e:
            logging.error(f"Error handling routine message: {e}")

    def handle_message_ws(self, message):
        logging.info("Handle WebSocket message: %s", message)

        try:
            # Trigger any related routines; no need to transform this msg
            asyncio.create_task(self.routine_manager.handle_message(message))

            def handle_transformed_msg(msg, topic):
                asyncio.create_task(self.mqtt_client.publish(topic, msg))

            # Transform and send to mqtt broker
            WebsocketTransformerRegistry.transform(
                message, handle_transformed_msg, devices=self.devices
            )
        except Exception as e:
            logging.error(f"Error handling websocket message: {e}")

    def handle_message_mqtt(self, topic, message):
        logging.info("Handle MQTT message: %s (topic: %s)", message, topic)

        try:

            def handle_transformed_msg(msg):
                asyncio.create_task(self.websocket_client.send(msg))
                asyncio.create_task(self.routine_manager.handle_message(msg))

            # Transform and send to websocket server as well as routine manager for triggering related routines, if any
            MqttTransformerRegistry.transform(
                message, topic, handle_transformed_msg, devices=self.devices
            )
        except Exception as e:
            logging.error(f"Error handling MQTT message: {e}")

    async def start(self):
        token = await get_token()

        # Initially fetch devices
        self.devices = await fetch_devices(token)

        # Periodically update devices
        # TODO: use realtime  updates for this
        async def periodic_device_updates():
            while True:
                await asyncio.sleep(300)
                self.devices = await fetch_devices(token)

        # Initially fetch and register routines
        routines = await fetch_routines(token)
        await self.routine_manager.register_routines(routines)

        # Periodically update routines
        # TODO: use realtime  updates for this
        async def periodic_routine_updates():
            while True:
                await asyncio.sleep(300)
                routines = await fetch_routines(token)
                await self.routine_manager.register_routines(routines)

        # Start all tasks concurrently
        await asyncio.gather(
            self.mqtt_client.subscribe("#"),
            self.websocket_client.connect(token),
            periodic_device_updates(),
            periodic_routine_updates(),
        )


async def main():
    controller = Controller()
    await controller.start()


if __name__ == "__main__":
    asyncio.run(main())
