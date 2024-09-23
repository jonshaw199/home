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
        while 1:
            try:
                await self._connect(token)
            except Exception as e:
                logging.error(f"Websocket connect error: {e}")
                await asyncio.sleep(1)
                logging.warn("Attempting to reconnect to WebSocket server...")

    async def _connect(self, token):
        if token:
            self.token = token
        uri = f"ws://{HOME_HOST}:{HOME_PORT}/ws/controllers?token={self.token}"
        headers = {
            "Origin": f"http://{HOME_HOST}:{HOME_PORT}",
        }

        logging.info(f"Connecting to uri: {uri}")

        self.websocket = await websockets.connect(uri, extra_headers=headers)
        logging.info(f"Connected to WebSocket server: {uri}")
        await self.receive_messages()  # Start receiving messages

    async def receive_messages(self):
        try:
            async for message in self.websocket:
                logging.info(f"Received message: {message}")
                self.on_message(message)  # Call the provided callback
        except Exception as e:
            logging.error(f"Error receiving message: {e}")
            raise e

    async def send(self, message):
        logging.info(f"Sending websocket message: {message}")
        try:
            await self.websocket.send(message)
        except Exception as e:
            logging.error(f"Error sending websocket message: {e}")
