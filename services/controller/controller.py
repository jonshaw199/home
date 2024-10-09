#!/usr/bin/env python3

import logging
import asyncio
import json
from websocket_client import WebsocketClient
from mqtt_client import AsyncMqttClient
from websocket_transformer import WebsocketTransformerRegistry
from mqtt_transformer import MqttTransformerRegistry
from auth import get_token
from routine_manager import RoutineManager, fetch_routines

logging.basicConfig(level=logging.DEBUG)  # Ensure this is set at the beginning


class Controller:
    def __init__(self):
        self.websocket_client = WebsocketClient(self.handle_message_ws)
        self.mqtt_client = AsyncMqttClient(self.handle_message_mqtt)
        self.routine_manager = RoutineManager(self.handle_routine_msg)

    def handle_routine_msg(self, routine, action, eval_data):
        outMsg = {
            "src": routine.get("name"),
            "dest": eval_data.get("dest"),
            "action": action,
            "body": eval_data.get("body"),
        }
        outMsgStr = json.dumps(outMsg)
        topic = outMsg["dest"]
        # Send to both websocket server and mqtt broker
        asyncio.create_task(self.mqtt_client.publish(topic, outMsgStr))
        asyncio.create_task(self.websocket_client.send(outMsgStr))

    def handle_message_ws(self, message):
        logging.info("Handle WebSocket message: %s", message)

        try:
            # Pass the message type to RoutineManager to trigger any related routines
            # Do this before transforming as the message should be in the expected format
            asyncio.create_task(
                self.routine_manager.handle_message(transformed_message)
            )

            transformed_message, topic = WebsocketTransformerRegistry.transform(message)
            logging.info(
                f"Publishing transformed message {transformed_message} to topic {topic}"
            )
            asyncio.create_task(self.mqtt_client.publish(topic, transformed_message))
        except Exception as e:
            logging.error(f"Error handling WS message: {e}")

    def handle_message_mqtt(self, topic, message):
        logging.info("Handle MQTT message: %s (topic: %s)", message, topic)

        try:
            transformed_message = MqttTransformerRegistry.transform(message, topic)
            logging.info(f"Sending transformed message {transformed_message}")
            asyncio.create_task(self.websocket_client.send(transformed_message))

            # Pass the message type to RoutineManager to trigger any related routines
            asyncio.create_task(
                self.routine_manager.handle_message(transformed_message)
            )
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
