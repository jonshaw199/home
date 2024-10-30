# local_server.py

import logging
from aiohttp import web, WSCloseCode
import os
from dotenv import load_dotenv

load_dotenv()
LOCAL_SERVER_PORT = os.getenv("LOCAL_SERVER_PORT")


class LocalServer:
    def __init__(self, handle_http_request, handle_ws_message):
        self.handle_http_request = handle_http_request
        self.handle_ws_message = handle_ws_message
        self.clients = set()  # Keep track of WebSocket clients

    # HTTP and WebSocket setup and route handling
    def setup_routes(self, app):
        app.router.add_route("*", "/api/{tail:.*}", self.handle_http_request)
        app.router.add_get("/ws/clients", self.websocket_handler)

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.clients.add(ws)
        logging.info("New WebSocket client connected")

        try:
            async for message in ws:
                if message.type == web.WSMsgType.TEXT:
                    await self.handle_ws_message(message.data)
                    await self.broadcast_ws(message.data)
                elif message.type == web.WSMsgType.ERROR:
                    logging.error(
                        f"WebSocket connection closed with exception {ws.exception()}"
                    )
        finally:
            self.clients.remove(ws)
            await ws.close(code=WSCloseCode.GOING_AWAY)
            logging.info("WebSocket client disconnected")

        return ws

    async def broadcast_ws(self, message):
        for client in self.clients:
            await client.send_str(message)

    async def start(self):
        app = web.Application()
        self.setup_routes(app)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", LOCAL_SERVER_PORT)
        await site.start()
        logging.info(f"LocalServer running on port {LOCAL_SERVER_PORT}")
