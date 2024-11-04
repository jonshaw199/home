#!/usr/bin/env python3

import logging
import asyncio
import json
import os
from aiohttp import web, ClientSession
from dotenv import load_dotenv
from websocket_client import WebsocketClient
from mqtt_client import AsyncMqttClient
from websocket_transformer import (
    WebsocketTransformerRegistry,
    register_websocket_transformers,
)
from mqtt_transformer import MqttTransformerRegistry, register_mqtt_transformers
from auth import Auth
from routine_manager import RoutineManager
from cache import Cache
from resource_handler import ResourceHandler
from local_server import LocalServer
from message_handler import MessageHandler

logging.basicConfig(level=logging.INFO)

load_dotenv()
HOME_HOST = os.getenv("HOME_HOST")
HOME_PORT = os.getenv("HOME_PORT")
DEVICE_ID = os.getenv("DEVICE_ID")

HEALTH_CHECK_URL = f"http://{HOME_HOST}:{HOME_PORT}/status/"
HEALTH_CHECK_INTERVAL_S = 60


def transform_index_response(items):
    return {item["uuid"]: item for item in items}


class Controller:
    def __init__(self):
        self.online = False
        self.token = None

        self.auth = Auth()
        self.websocket_client = WebsocketClient(
            self.handle_ws_client_msg, self.auth.get_token
        )
        self.mqtt_client = AsyncMqttClient(self.handle_message_mqtt)
        self.routine_manager = RoutineManager(self.handle_routine_msg)
        self.cache = Cache()
        self.resource_handler = ResourceHandler(
            self.cache,
            f"http://{HOME_HOST}:{HOME_PORT}",
            self.get_is_online,
            self.auth.get_token,
        )
        self.message_handler = MessageHandler(self.resource_handler)
        self.local_server = LocalServer(
            self.handle_local_server_api_request,
            self.handle_ws_server_msg,
            self.handle_local_server_auth_request,
        )

        self.websocket_transformer = WebsocketTransformerRegistry(self.resource_handler)
        register_websocket_transformers(self.websocket_transformer)
        self.mqtt_transformer = MqttTransformerRegistry(self.resource_handler)
        register_mqtt_transformers(self.mqtt_transformer)

    def get_is_online(self):
        return self.online

    async def handle_local_server_auth_request(self, request):
        logging.info("Handling local server auth request")

        if self.online:
            try:
                url = f"http://{HOME_HOST}:{HOME_PORT}{request.path}"
                data = await request.json()

                # Forward the request to the Django server
                async with ClientSession() as session:
                    async with session.post(url, json=data) as response:
                        # Forward the response back to the client
                        return web.Response(
                            status=response.status,
                            body=await response.read(),
                            headers={
                                key: value for key, value in response.headers.items()
                            },
                        )
            except Exception as e:
                logging.error(f"Error proxying request to Django server: {e}")
                return web.Response(status=500, text="Internal Server Error")
        else:
            return web.Response(
                status=200,
                text='{"status": "ok", "message": "Controller is up and running"}',
            )

    async def handle_local_server_api_request(self, request):
        logging.info("Handling local server api request")

        try:
            path = request.path
            method = request.method
            data = await request.json() if method in ["POST", "PUT", "PATCH"] else None

            logging.info(f"Request path: {path}; method: {method}; data: {data}")

            response = await self.resource_handler.handle_request(method, path, data)
            return web.json_response(response)
        except Exception as e:
            logging.error(f"Error handling local server api request: {e}")

    def handle_routine_msg(self, routine, action, eval_data):
        logging.info("Handle routine message")

        try:
            outMsg = {
                "src": DEVICE_ID,
                "src_type": "device",
                "dest": eval_data.get("dest"),
                "action": action,
                "body": eval_data.get("body"),
            }
            outMsgStr = json.dumps(outMsg)

            # Handle message
            asyncio.create_task(self.message_handler.handle(outMsgStr))

            # Send to django server
            asyncio.create_task(self.websocket_client.send(outMsgStr))

            # Send to local clients
            asyncio.create_task(self.local_server.broadcast_ws(outMsgStr))

            def handle_transformed_msg(msg, topic):
                asyncio.create_task(self.mqtt_client.publish(topic, msg))

            # Transform and send to mqtt broker
            asyncio.create_task(
                self.websocket_transformer.transform(outMsgStr, handle_transformed_msg)
            )
        except Exception as e:
            logging.error(f"Error handling routine message: {e}")

    def handle_ws_server_msg(self, message):
        logging.info("Handle WebSocket server message: %s", message)

        try:
            # Handle message
            asyncio.create_task(self.message_handler.handle(message))

            # Trigger any related routines; no need to transform this msg
            asyncio.create_task(self.routine_manager.handle_message(message))

            # Send back to local clients
            asyncio.create_task(self.local_server.broadcast_ws(message))

            # Send to django server
            asyncio.create_task(self.websocket_client.send(message))

            def handle_transformed_msg(msg, topic):
                asyncio.create_task(self.mqtt_client.publish(topic, msg))

            # Transform and send to mqtt broker
            asyncio.create_task(
                self.websocket_transformer.transform(message, handle_transformed_msg)
            )
        except Exception as e:
            logging.error(f"Error handling websocket message: {e}")

    def handle_ws_client_msg(self, message):
        logging.info("Handle WebSocket client message: %s", message)

        try:
            # Handle message
            asyncio.create_task(self.message_handler.handle(message))

            # Trigger any related routines; no need to transform this msg
            asyncio.create_task(self.routine_manager.handle_message(message))

            # Send to local clients
            asyncio.create_task(self.local_server.broadcast_ws(message))

            # Do not need to send back to django server; it should have distributed this message to everyone that needs it

            def handle_transformed_msg(msg, topic):
                asyncio.create_task(self.mqtt_client.publish(topic, msg))

            # Transform and send to mqtt broker
            asyncio.create_task(
                self.websocket_transformer.transform(message, handle_transformed_msg)
            )
        except Exception as e:
            logging.error(f"Error handling websocket message: {e}")

    def handle_message_mqtt(self, topic, message):
        logging.info("Handle MQTT message: %s (topic: %s)", message, topic)

        try:

            def handle_transformed_msg(msg):
                asyncio.create_task(self.message_handler.handle(message))
                asyncio.create_task(self.websocket_client.send(msg))
                asyncio.create_task(self.local_server.broadcast_ws(msg))
                asyncio.create_task(self.routine_manager.handle_message(msg))

            # Transform and send to websocket server, websocket clients,and routine manager for triggering related routines, if any
            asyncio.create_task(
                self.mqtt_transformer.transform(message, topic, handle_transformed_msg)
            )
        except Exception as e:
            logging.error(f"Error handling MQTT message: {e}")

    async def initialize_routines(self):
        try:
            routines = await self.resource_handler.fetch("routines")
            transformed_routines = transform_index_response(routines)
            actions = await self.resource_handler.fetch("actions")
            transformed_actions = transform_index_response(actions)
            await self.routine_manager.register_routines(
                transformed_routines, transformed_actions
            )
        except Exception as e:
            logging.error(f"Error initializing routines: {e}")

    async def check_server_availability(self):
        logging.info("Checking remote server availability")

        try:
            async with ClientSession() as session:
                async with session.get(HEALTH_CHECK_URL) as resp:
                    self.online = resp.status == 200
                    logging.info(f"Server online status: {self.online}")
        except Exception as e:
            logging.error(f"Server check failed: {e}")
            self.online = False
        return self.online

    async def continuously_check_server_availability(self):
        """Background task to check if the Django server is reachable."""
        while True:
            prev_online_status = self.online
            await self.check_server_availability()

            # offline -> online
            if not prev_online_status and self.online:
                try:
                    await self.handle_back_online()
                except Exception as e:
                    logging.error(f"Error when handling reconnection: {e}")

            # online -> offline
            if prev_online_status and not self.online:
                try:
                    await self.handle_back_offline()
                except Exception as e:
                    logging.error(f"Error when handling disconnection: {e}")

            # Wait for the next check interval
            await asyncio.sleep(
                HEALTH_CHECK_INTERVAL_S
            )  # Check every HEALTH_CHECK_INTERVAL_S seconds

    async def handle_back_online(self):
        logging.info("Back online!")
        try:
            self.token = await self.auth.get_token()
            await self.initialize_routines()
        except Exception as e:
            logging.error(f"Error handling back online: {e}")

    async def handle_online_startup(self):
        logging.info("Handling online startup")
        # For now, same logic as back online
        await self.handle_back_online()

    async def handle_back_offline(self):
        logging.info("Back offline!")
        # Nothing to do here for now

    async def handle_offline_startup(self):
        logging.info("Handling offline startup")
        # Nothing to do here for now

    async def start(self):
        # Perform a one-time initial check for server availability to set self.online
        await self.check_server_availability()

        # Attempt to authenticate only if online
        if self.online:
            try:
                await self.handle_online_startup()
            except Exception as e:
                logging.error(f"Error during online initialization: {e}")
                await self.handle_offline_startup()
        else:
            await self.handle_offline_startup()

        # Start tasks, some of which depend on the server
        await asyncio.gather(
            self.local_server.start(),
            self.mqtt_client.subscribe("#"),
            self.websocket_client.connect(),
            self.continuously_check_server_availability(),  # Start ongoing availability check
        )


async def main():
    controller = Controller()
    await controller.start()


if __name__ == "__main__":
    asyncio.run(main())
