#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import aiohttp
import asyncio
import logging

load_dotenv()
HOME_HOST = os.getenv("HOME_HOST")
HOME_PORT = os.getenv("HOME_PORT")
HOME_USERNAME = os.getenv("HOME_USERNAME")
HOME_PASSWORD = os.getenv("HOME_PASSWORD")

url = f"http://{HOME_HOST}:{HOME_PORT}/api-token-auth/"
data = {"username": HOME_USERNAME, "password": HOME_PASSWORD}


async def get_token():
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as resp:
            parsed = await resp.json()
            return parsed["token"]
