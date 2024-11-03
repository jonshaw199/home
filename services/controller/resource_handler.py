from aiohttp import ClientSession
import logging
from dotenv import load_dotenv
import os

load_dotenv()
API_PREFIX = os.getenv("API_PREFIX", "")


class ResourceHandler:
    def __init__(self, cache, server_url, token_getter=None, message_queue=None):
        self.cache = cache
        self.server_url = server_url
        self.get_token = token_getter
        self.message_queue = message_queue  # Stub for future message broker

    async def get_common_headers(self):
        token = await self.get_token()
        return {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json",
        }

    async def fetch_online(self, resource_type, resource_id=None):
        logging.info(f"GET {resource_type}: {resource_id or 'All'}")

        # Proxy the GET request to the Django server
        url = f"{self.server_url}{API_PREFIX}/{resource_type}"
        if resource_id:
            url += f"/{resource_id}"
        common_headers = await self.get_common_headers()

        async with ClientSession() as session:
            async with session.get(url, headers=common_headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logging.info(f"Response data: {data}")
                    if resource_id:
                        self.cache.add(resource_type, data)
                    else:
                        for item in data:
                            self.cache.add(resource_type, item)
                    return data
                else:
                    logging.error(
                        f"Failed to fetch {resource_type}. Status: {response.status}"
                    )
                    return self.cache.get(resource_type, resource_id)

    async def fetch_offline(self, resource_type, resource_id=None):
        logging.info(f"GET offline {resource_type}: {resource_id or 'All'}")

        return self.cache.get(resource_type, resource_id)

    async def fetch(self, resource_type, resource_id=None, online=True):
        if online:
            return await self.fetch_online(resource_type, resource_id)
        return await self.fetch_offline(resource_type, resource_id)

    async def post_online(self, resource_type, data):
        logging.info(f"POST {resource_type}: {data}")

        # Proxy POST request to the Django server
        url = f"{self.server_url}{API_PREFIX}/{resource_type}"
        common_headers = await self.get_common_headers()

        async with ClientSession() as session:
            async with session.post(url, headers=common_headers, json=data) as response:
                if response.status == 201:
                    created_resource = await response.json()
                    self.cache.add(resource_type, created_resource)
                    return created_resource
                else:
                    logging.error(
                        f"Failed to create {resource_type}. Status: {response.status}"
                    )
                    return None

    async def post_offline(self, resource_type, data):
        # Handle POST request offline - add to cache and queue for later sync
        logging.info(f"Offline - saving {resource_type} locally and queueing for later")
        self.cache.add(resource_type, data)
        if self.message_queue:
            self.message_queue.add_to_queue("POST", resource_type, data)

    async def post(self, resource_type, data, online=True):
        if online:
            return await self.post_online(resource_type, data)
        return await self.post_offline(resource_type, data)

    async def put_online(self, resource_type, resource_id, data):
        logging.info(f"PUT {resource_type}; id: {resource_id}; data: {data}")

        # Proxy PUT request to the Django server
        url = f"{self.server_url}{API_PREFIX}/{resource_type}/{resource_id}"
        common_headers = await self.get_common_headers()

        async with ClientSession() as session:
            async with session.put(url, headers=common_headers, json=data) as response:
                if response.status == 200:
                    updated_resource = await response.json()
                    self.cache.update(resource_type, resource_id, updated_resource)
                    return updated_resource
                else:
                    logging.error(
                        f"Failed to update {resource_type}. Status: {response.status}"
                    )
                    return None

    async def put_offline(self, resource_type, resource_id, data):
        # Handle PUT request offline - update cache and queue for later sync
        logging.info(
            f"Offline - updating {resource_type} locally and queueing for later"
        )
        self.cache.update(resource_type, resource_id, data)
        if self.message_queue:
            self.message_queue.add_to_queue("PUT", resource_type, resource_id, data)

    async def put(self, resource_type, resource_id, data, online=True):
        if online:
            return await self.put_online(resource_type, resource_id, data)
        return await self.put_offline(resource_type, resource_id, data)

    async def delete_online(self, resource_type, resource_id):
        logging.info(f"DELETE {resource_type}; id: {resource_id}")

        # Proxy DELETE request to the Django server
        url = f"{self.server_url}{API_PREFIX}/{resource_type}/{resource_id}"
        common_headers = await self.get_common_headers()

        async with ClientSession() as session:
            async with session.delete(url, headers=common_headers) as response:
                if response.status == 204:
                    self.cache.delete(resource_type, resource_id)
                else:
                    logging.error(
                        f"Failed to delete {resource_type}. Status: {response.status}"
                    )

    async def delete_offline(self, resource_type, resource_id):
        # Handle DELETE request offline - remove from cache and queue for later sync
        logging.info(
            f"Offline - deleting {resource_type} locally and queueing for later"
        )
        self.cache.delete(resource_type, resource_id)
        if self.message_queue:
            self.message_queue.add_to_queue("DELETE", resource_type, resource_id)

    async def delete(self, resource_type, resource_id, online=True):
        if online:
            return await self.delete_online(resource_type, resource_id)
        return await self.delete_offline(resource_type, resource_id)

    async def _handle_request(self, method, path, data=None, online=True):
        logging.info(
            f"Handling HTTP request; path: {path}; method: {method}; data: {data}"
        )

        # Determine resource type and ID from the path (basic parsing, adjust as needed)
        path_parts = path.removeprefix(API_PREFIX).strip("/").split("/")
        resource_type = path_parts[0]
        resource_id = path_parts[1] if len(path_parts) > 1 else None

        if method == "GET":
            return await self.fetch(resource_type, resource_id, online)
        elif method == "POST":
            return await self.post(resource_type, data, online)
        elif method == "PUT":
            return await self.put(resource_type, resource_id, data, online)
        elif method == "DELETE":
            return await self.delete(resource_type, resource_id, online)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    async def handle_request(self, method, path, data=None, online=True):
        try:
            return await self._handle_request(method, path, data, online)
        except Exception as e:
            logging.error(f"Error handling request: {e}")
