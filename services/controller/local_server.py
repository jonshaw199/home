# local_server.py

import logging
from aiohttp import web, WSCloseCode
from aiohttp_cors import setup, ResourceOptions
import os
import ssl

LOCAL_SERVER_PORT = os.getenv("LOCAL_SERVER_PORT")
SSL_ENABLED = os.getenv("SSL_ENABLED")


class LocalServer:
    def __init__(self, handle_api_request, handle_ws_message, handle_auth_request):
        self.handle_api_request = handle_api_request
        self.handle_ws_message = handle_ws_message
        self.handle_auth_request = handle_auth_request
        self.clients = set()  # Keep track of WebSocket clients

    # HTTP and WebSocket setup and route handling
    def setup_routes(self, app):
        # Define specific HTTP methods for /api route to avoid CORS conflict
        app.router.add_route("GET", "/api/{tail:.*}", self.handle_api_request)
        app.router.add_route("POST", "/api/{tail:.*}", self.handle_api_request)
        app.router.add_route("PUT", "/api/{tail:.*}", self.handle_api_request)
        app.router.add_route("DELETE", "/api/{tail:.*}", self.handle_api_request)

        # Status
        app.router.add_get("/status/", self.status_handler)

        # WebSocket route
        app.router.add_get("/ws/controllers", self.websocket_handler)

        # Auth
        app.router.add_post("/api-token-auth/", self.handle_auth_request)

    async def status_handler(self, request):
        """Simple handler for the /status/ endpoint"""
        return web.Response(
            status=200,
            text='{"status": "ok", "message": "Controller is up and running"}',
        )

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.clients.add(ws)
        logging.info("New WebSocket client connected")

        try:
            async for message in ws:
                if message.type == web.WSMsgType.TEXT:
                    self.handle_ws_message(message.data)
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
            try:
                await client.send_str(message)
            except Exception as e:
                logging.error(
                    f"Error sending message to client; message: {message}; client: {client}; error: {e}"
                )

    async def start(self):
        app = web.Application()
        self.setup_routes(app)

        # Configure CORS settings
        cors = setup(
            app,
            defaults={
                "*": ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods=[
                        "GET",
                        "POST",
                        "PUT",
                        "DELETE",
                        "OPTIONS",
                    ],  # Specify allowed methods
                )
            },
        )

        # Apply CORS to each route
        for route in list(app.router.routes()):
            cors.add(route)

        runner = web.AppRunner(app)
        await runner.setup()

        ssl_context = None
        if SSL_ENABLED:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(
                certfile="certs/cert.pem", keyfile="certs/key.pem"
            )
        site = web.TCPSite(
            runner, "0.0.0.0", LOCAL_SERVER_PORT, ssl_context=ssl_context
        )
        await site.start()
        logging.info(f"LocalServer running on port {LOCAL_SERVER_PORT}")
