#!/usr/bin/env python3

import logging
import asyncio
import json
import os
from aiohttp import web
from dotenv import load_dotenv
from websocket_client import WebsocketClient
from mqtt_client import AsyncMqttClient
from websocket_transformer import WebsocketTransformerRegistry
from mqtt_transformer import MqttTransformerRegistry
from auth import get_token
from routine_manager import RoutineManager
from cache import Cache
from request_handler import RequestHandler
from local_server import LocalServer

logging.basicConfig(level=logging.DEBUG)  # Ensure this is set at the beginning

load_dotenv()
HOME_HOST = os.getenv("HOME_HOST")
HOME_PORT = os.getenv("HOME_PORT")

# TODO: When status message (for example) received via websocket, send PUT request to update


def transform_index_response(items):
    return {item["uuid"]: item for item in items}


class Controller:
    def __init__(self):
        self.websocket_client = WebsocketClient(self.handle_ws_client_msg)
        self.mqtt_client = AsyncMqttClient(self.handle_message_mqtt)
        self.routine_manager = RoutineManager(self.handle_routine_msg)
        self.cache = Cache()
        self.request_handler = RequestHandler(
            self.cache, f"http://{HOME_HOST}:{HOME_PORT}"
        )
        self.devices = {}
        self.routines = {}
        self.actions = {}
        self.local_server = LocalServer(
            handle_http_request=self.handle_http_request,
            handle_ws_message=self.handle_ws_server_msg,
        )

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

            # Send to django server
            asyncio.create_task(self.websocket_client.send(outMsgStr))

            # Send to local clients
            asyncio.create_task(self.websocket_server.send(outMsgStr))

            def handle_transformed_msg(msg, topic):
                asyncio.create_task(self.mqtt_client.publish(topic, msg))

            # Transform and send to mqtt broker
            WebsocketTransformerRegistry.transform(
                outMsgStr, handle_transformed_msg, devices=self.devices
            )
        except Exception as e:
            logging.error(f"Error handling routine message: {e}")

    def handle_ws_server_msg(self, message):
        logging.info("Handle WebSocket server message: %s", message)

        try:
            # Trigger any related routines; no need to transform this msg
            asyncio.create_task(self.routine_manager.handle_message(message))

            # Send back to local clients
            asyncio.create_task(self.websocket_server.send(message))

            # Send to django server
            asyncio.create_task(self.websocket_client.send(message))

            def handle_transformed_msg(msg, topic):
                asyncio.create_task(self.mqtt_client.publish(topic, msg))

            # Transform and send to mqtt broker
            WebsocketTransformerRegistry.transform(
                message, handle_transformed_msg, devices=self.devices
            )
        except Exception as e:
            logging.error(f"Error handling websocket message: {e}")

    def handle_ws_client_msg(self, message):
        logging.info("Handle WebSocket client message: %s", message)

        try:
            # Trigger any related routines; no need to transform this msg
            asyncio.create_task(self.routine_manager.handle_message(message))

            # Send to local clients
            asyncio.create_task(self.websocket_server.send(message))

            # Do not need to send back to django server; it should have distributed this message to everyone that needs it

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
                asyncio.create_task(self.websocket_server.send(msg))
                asyncio.create_task(self.routine_manager.handle_message(msg))

            # Transform and send to websocket server, websocket clients,and routine manager for triggering related routines, if any
            MqttTransformerRegistry.transform(
                message, topic, handle_transformed_msg, devices=self.devices
            )
        except Exception as e:
            logging.error(f"Error handling MQTT message: {e}")

    async def handle_http_request(self, request):
        path = request.path
        method = request.method
        data = await request.json() if method in ["POST", "PUT", "PATCH"] else None

        logging.info(
            f"Handling HTTP request; path: {path}; method: {method}; data: {data}"
        )

        token = await get_token()

        # Proxy or cache the request through the request handler
        response_data = await self.request_handler.handle_request(
            method, path, data, token
        )

        return web.json_response(response_data)

    def setup_routes(self, app):
        app.router.add_route("*", "/api/{tail:.*}", self.handle_http_request)

    async def start(self):
        token = await get_token()

        # Fetch devices
        devices = await self.request_handler.fetch("devices", token=token)
        self.devices = transform_index_response(devices)

        # Initially fetch and register routines
        routines = await self.request_handler.fetch("routines", token=token)
        actions = await self.request_handler.fetch("actions", token=token)
        await self.routine_manager.register_routines(routines, actions)

        # Start all tasks concurrently
        await asyncio.gather(
            self.local_server.start(),
            self.mqtt_client.subscribe("#"),
            self.websocket_client.connect(token),
        )


async def main():
    controller = Controller()
    await controller.start()


if __name__ == "__main__":
    asyncio.run(main())
