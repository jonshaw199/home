from aiohttp import ClientSession
import logging
from dotenv import load_dotenv
import os

load_dotenv()
API_PREFIX = os.getenv("API_PREFIX", "")


class RequestHandler:
    def __init__(self, cache, server_url, message_queue=None):
        self.cache = cache
        self.server_url = server_url
        self.message_queue = message_queue  # Stub for future message broker
        self.is_online = True  # TODO

    async def fetch(self, resource_type, resource_id=None, token=None):
        logging.info(f"GET {resource_type}: {resource_id or 'All'}")

        if self.is_online:
            # Proxy the GET request to the Django server
            url = f"{self.server_url}{API_PREFIX}/{resource_type}"
            if resource_id:
                url += f"/{resource_id}"
            headers = {
                "Authorization": f"Token {token}",
                "Content-Type": "application/json",
            }

            async with ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
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
        else:
            # Handle GET request offline
            logging.warning(f"Offline - serving {resource_type} from cache")
            return self.cache.get(resource_type, resource_id)

    async def post(self, resource_type, data, token=None):
        logging.info(f"POST {resource_type}: {data}")

        if self.is_online:
            # Proxy POST request to the Django server
            url = f"{self.server_url}{API_PREFIX}/{resource_type}"
            headers = {
                "Authorization": f"Token {token}",
                "Content-Type": "application/json",
            }

            async with ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 201:
                        created_resource = await response.json()
                        self.cache.add(resource_type, created_resource)
                        return created_resource
                    else:
                        logging.error(
                            f"Failed to create {resource_type}. Status: {response.status}"
                        )
                        return None
        else:
            # Handle POST request offline - add to cache and queue for later sync
            logging.warning(
                f"Offline - saving {resource_type} locally and queueing for later"
            )
            self.cache.add(resource_type, data)
            if self.message_queue:
                self.message_queue.add_to_queue("POST", resource_type, data)

    async def put(self, resource_type, resource_id, data, token=None):
        logging.info(f"PUT {resource_type}; id: {resource_id}; data: {data}")

        if self.is_online:
            # Proxy PUT request to the Django server
            url = f"{self.server_url}{API_PREFIX}/{resource_type}/{resource_id}"
            headers = {
                "Authorization": f"Token {token}",
                "Content-Type": "application/json",
            }

            async with ClientSession() as session:
                async with session.put(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        updated_resource = await response.json()
                        self.cache.update(resource_type, resource_id, updated_resource)
                        return updated_resource
                    else:
                        logging.error(
                            f"Failed to update {resource_type}. Status: {response.status}"
                        )
                        return None
        else:
            # Handle PUT request offline - update cache and queue for later sync
            logging.warning(
                f"Offline - updating {resource_type} locally and queueing for later"
            )
            self.cache.update(resource_type, resource_id, data)
            if self.message_queue:
                self.message_queue.add_to_queue("PUT", resource_type, resource_id, data)

    async def delete(self, resource_type, resource_id, token=None):
        logging.info(f"DELETE {resource_type}; id: {resource_id}")

        if self.is_online:
            # Proxy DELETE request to the Django server
            url = f"{self.server_url}{API_PREFIX}/{resource_type}/{resource_id}"
            headers = {
                "Authorization": f"Token {token}",
                "Content-Type": "application/json",
            }

            async with ClientSession() as session:
                async with session.delete(url, headers=headers) as response:
                    if response.status == 204:
                        self.cache.delete(resource_type, resource_id)
                    else:
                        logging.error(
                            f"Failed to delete {resource_type}. Status: {response.status}"
                        )
        else:
            # Handle DELETE request offline - remove from cache and queue for later sync
            logging.warning(
                f"Offline - deleting {resource_type} locally and queueing for later"
            )
            self.cache.delete(resource_type, resource_id)
            if self.message_queue:
                self.message_queue.add_to_queue("DELETE", resource_type, resource_id)

    async def handle_request(self, method, path, data=None, token=None):
        # Determine resource type and ID from the path (basic parsing, adjust as needed)
        path_parts = path.removeprefix(API_PREFIX).strip("/").split("/")
        resource_type = path_parts[0]
        resource_id = path_parts[1] if len(path_parts) > 1 else None

        if method == "GET":
            return await self.fetch(resource_type, resource_id, token)
        elif method == "POST":
            return await self.post(resource_type, data, token)
        elif method == "PUT":
            return await self.put(resource_type, resource_id, data, token)
        elif method == "DELETE":
            return await self.delete(resource_type, resource_id, token)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
