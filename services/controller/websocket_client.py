import os
from dotenv import load_dotenv
import logging
import asyncio
import websockets

load_dotenv()
HOME_HOST = os.getenv("HOME_HOST")
HOME_PORT = os.getenv("HOME_PORT")

logging.basicConfig(level=logging.INFO)


class WebsocketClient:
    def __init__(self, on_message):
        self.token = ""
        self.on_message = on_message
        self.websocket = None

    async def connect(self, token=""):
        if token:
            self.token = token
        uri = f"ws://{HOME_HOST}:{HOME_PORT}/ws/controllers?token={self.token}"
        headers = {
            "Origin": f"http://{HOME_HOST}:{HOME_PORT}",
        }
        logging.info(f"Connecting to uri: {uri}")

        try:
            self.websocket = await websockets.connect(uri, extra_headers=headers)
            logging.info(f"Connected to WebSocket server: {uri}")
            await self.receive_messages()  # Start receiving messages
        except Exception as e:
            logging.error(f"Connection failed: {e}")
            await self.reconnect()

    async def reconnect(self):
        logging.info("Attempting to reconnect to WebSocket server...")
        await asyncio.sleep(5)  # Wait before reconnecting
        await self.connect()

    async def receive_messages(self):
        try:
            async for message in self.websocket:
                logging.info(f"Received message: {message}")
                self.on_message(message)  # Call the provided callback
        except websockets.ConnectionClosed as e:
            logging.warning(f"Connection closed: {e}")
            await self.reconnect()
        except Exception as e:
            logging.error(f"Error receiving message: {e}")
            await self.reconnect()

    async def send(self, message):
        try:
            if self.websocket and self.websocket.open:
                await self.websocket.send(message)
                logging.info(f"Sent message: {message}")
            else:
                logging.warning("WebSocket connection is not open. Reconnecting...")
                await self.reconnect()
                await self.websocket.send(message)
        except Exception as e:
            logging.error(f"Error sending message: {e}")
            await self.reconnect()
