#!/usr/bin/env python3

import logging
import asyncio

from websocket_client import WebsocketClient
from mqtt_client import AsyncMqttClient
from webocket_transformer import WebsocketTransformerRegistry
from mqtt_transformer import MqttTransformerRegistry
from auth import get_token
from routine_manager import RoutineManager, fetch_routines


logging.basicConfig(level=logging.DEBUG)  # Ensure this is set at the beginning


class Controller:
    def __init__(self):
        self.websocket_client = WebsocketClient(self.handle_message_ws)
        self.mqtt_client = AsyncMqttClient(self.handle_message_mqtt)
        self.routine_manager = RoutineManager()

    def handle_message_ws(self, message):
        logging.info("Handle message: %s", message)

        try:
            transformed_message, topic = WebsocketTransformerRegistry.transform(message)
            logging.info(
                f"Publishing transformed message {transformed_message} to topic {topic}"
            )
            asyncio.create_task(
                self.mqtt_client.publish(topic, transformed_message)
            )  # Schedule the MQTT publish
        except Exception as e:
            logging.error(f"Error handling WS message: {e}")

    def handle_message_mqtt(self, topic, message):
        logging.info("Handle message: %s (topic: %s)", message, topic)

        try:
            transformed_message = MqttTransformerRegistry.transform(message, topic)
            logging.info(f"Sending transformed message {transformed_message}")
            asyncio.create_task(
                self.websocket_client.send(transformed_message)
            )  # Schedule the WebSocket send

        except Exception as e:
            logging.error(f"Error handling MQTT message: {e}")

    async def start(self):
        token = await get_token()

        routines = await fetch_routines(token)
        self.routine_manager.register_routines(routines)

        # Start both MQTT and WebSocket clients concurrently
        await asyncio.gather(
            self.mqtt_client.subscribe("#"),  # Start subscribing to MQTT topics
            self.websocket_client.connect(token),  # Connect to the WebSocket server
        )


async def main():
    controller = Controller()
    await controller.start()


if __name__ == "__main__":
    asyncio.run(main())
