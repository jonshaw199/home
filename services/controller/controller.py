#!/usr/bin/env python3

import logging
import asyncio
import json
import os
from aiohttp import web, ClientSession
from dotenv import load_dotenv
from websocket_client import WebsocketClient
from mqtt_client import AsyncMqttClient
from websocket_transformer import WebsocketTransformerRegistry
from mqtt_transformer import MqttTransformerRegistry
from auth import Auth
from routine_manager import RoutineManager
from cache import Cache
from resource_handler import ResourceHandler
from local_server import LocalServer

logging.basicConfig(level=logging.DEBUG)  # Ensure this is set at the beginning

load_dotenv()
HOME_HOST = os.getenv("HOME_HOST")
HOME_PORT = os.getenv("HOME_PORT")

HEALTH_CHECK_URL = f"http://{HOME_HOST}:{HOME_PORT}/api/"
HEALTH_CHECK_INTERVAL_S = 60

# TODO: When status message (for example) received via websocket, send PUT request to update


def transform_index_response(items):
    return {item["uuid"]: item for item in items}


class Controller:
    def __init__(self):
        self.auth = Auth()
        self.websocket_client = WebsocketClient(
            self.handle_ws_client_msg, self.auth.get_token
        )
        self.mqtt_client = AsyncMqttClient(self.handle_message_mqtt)
        self.routine_manager = RoutineManager(self.handle_routine_msg)
        self.cache = Cache()
        self.resource_handler = ResourceHandler(
            self.cache, f"http://{HOME_HOST}:{HOME_PORT}", self.auth.get_token
        )
        self.devices = {}
        self.routines = {}
        self.actions = {}
        self.local_server = LocalServer(
            handle_http_request=self.handle_http_request,
            handle_ws_message=self.handle_ws_server_msg,
        )
        self.online = True  # Optimistic
        self.token = None

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
            asyncio.create_task(self.local_server.broadcast_ws(outMsgStr))

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
            asyncio.create_task(self.local_server.broadcast_ws(message))

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
            asyncio.create_task(self.local_server.broadcast_ws(message))

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
                asyncio.create_task(self.local_server.broadcast_ws(msg))
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

        # Proxy or cache the request through the request handler
        response_data = await self.resource_handler.handle_request(
            method, path, data, self.online
        )

        return web.json_response(response_data)

    def setup_routes(self, app):
        app.router.add_route("*", "/api/{tail:.*}", self.handle_http_request)

    async def do_if_online(self, online_func, offline_func=None):
        try:
            return await online_func()
        except Exception:
            self.online = False
            if offline_func:
                return offline_func()

    async def initialize_resources(self):
        devices = await self.resource_handler.fetch("devices", online=self.online)
        routines = await self.resource_handler.fetch("routines", online=self.online)
        actions = await self.resource_handler.fetch("actions", online=self.online)

        self.devices = transform_index_response(devices)
        self.routines = transform_index_response(routines)
        self.actions = transform_index_response(actions)

        await self.routine_manager.register_routines(self.routines, self.actions)

    async def check_server_availability(self):
        """Background task to check if the Django server is reachable."""
        while True:
            logging.info("Checking remote server availability")

            try:
                async with ClientSession() as session:
                    async with session.get(HEALTH_CHECK_URL) as resp:
                        self.online = resp.status == 200
                        logging.info(f"Server online status: {self.online}")
            except Exception as e:
                logging.error(f"Server check failed: {e}")
                self.online = False

            # Wait for the next check interval
            await asyncio.sleep(
                HEALTH_CHECK_INTERVAL_S
            )  # Check every HEALTH_CHECK_INTERVAL_S seconds

    async def start(self):
        self.token = await self.auth.get_token()

        await self.initialize_resources()

        # Start all tasks concurrently
        await asyncio.gather(
            self.local_server.start(),
            self.mqtt_client.subscribe("#"),
            self.websocket_client.connect(),
            self.check_server_availability(),  # Start server availability check
        )


async def main():
    controller = Controller()
    await controller.start()


if __name__ == "__main__":
    asyncio.run(main())
