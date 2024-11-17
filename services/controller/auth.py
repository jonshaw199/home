#!/usr/bin/env python3

import os
import aiohttp

HOME_HOST = os.getenv("HOME_HOST")
HOME_PORT = os.getenv("HOME_PORT")
HOME_USERNAME = os.getenv("HOME_USERNAME")
HOME_PASSWORD = os.getenv("HOME_PASSWORD")

url = f"http://{HOME_HOST}:{HOME_PORT}/api-token-auth/"
data = {"username": HOME_USERNAME, "password": HOME_PASSWORD}


class Auth:
    def __init__(self):
        self.token = None

    async def _get_token(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as resp:
                parsed = await resp.json()
                return parsed["token"]

    async def get_token(self):
        if not self.token:
            self.token = await self._get_token()
        return self.token
