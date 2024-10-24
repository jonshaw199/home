import logging
import asyncio
import websockets

logging.basicConfig(level=logging.INFO)


class WebsocketServer:
    def __init__(self, on_message):
        self.on_message = on_message
        self.websocket = None
        self.clients = set()

    async def start_server(self, host="0.0.0.0", port=8080):
        logging.info(f"Starting WebSocket server on {host}:{port}")
        server = await websockets.serve(self._handle_client, host, port)
        await server.wait_closed()

    async def _handle_client(self, websocket, path):
        logging.info("New client connected")
        self.clients.add(websocket)

        try:
            async for message in websocket:
                logging.info(f"Received message from client: {message}")
                self.on_message(message)  # Call the provided callback
                await self._broadcast(message)  # Optionally, broadcast to other clients
        except websockets.exceptions.ConnectionClosed as e:
            logging.warning(f"Client connection closed: {e}")
        finally:
            self.clients.remove(websocket)

    async def _broadcast(self, message):
        """Broadcast the message to all connected clients."""
        if self.clients:
            logging.info(f"Broadcasting message to {len(self.clients)} clients")
            await asyncio.gather(
                *[client.send(message) for client in self.clients if client.open]
            )

    async def send(self, message):
        """Send a message to all clients."""
        if self.clients:
            logging.info(f"Sending message to {len(self.clients)} clients")
            await asyncio.gather(
                *[client.send(message) for client in self.clients if client.open]
            )
        else:
            logging.warning("No clients to send message to")
