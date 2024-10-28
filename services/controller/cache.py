import json
import os


class Cache:
    def __init__(self, file_path="cache_data.json"):
        self.cache = {}
        self.file_path = file_path
        self.load_cache()

    def load_cache(self):
        """Load cache from a JSON file, if it exists."""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                self.cache = json.load(file)
        else:
            self.cache = {}

    def save_cache(self):
        """Save cache to a JSON file."""
        with open(self.file_path, "w") as file:
            json.dump(self.cache, file, indent=2)

    def get(self, resource_type, resource_id=None):
        if resource_type not in self.cache:
            return None if resource_id else []
        if resource_id:
            return self.cache[resource_type].get(resource_id)
        return list(self.cache[resource_type].values())

    def add(self, resource_type, resource):
        resource_id = resource.get("id") or resource.get("uuid")
        if resource_type not in self.cache:
            self.cache[resource_type] = {}
        self.cache[resource_type][resource_id] = resource
        self.save_cache()  # Persist changes

    def update(self, resource_type, resource_id, resource_data):
        if resource_type in self.cache and resource_id in self.cache[resource_type]:
            self.cache[resource_type][resource_id].update(resource_data)
            self.save_cache()  # Persist changes

    def delete(self, resource_type, resource_id):
        if resource_type in self.cache and resource_id in self.cache[resource_type]:
            del self.cache[resource_type][resource_id]
            self.save_cache()  # Persist changes

    def clear(self, resource_type=None):
        if resource_type:
            self.cache[resource_type] = {}
        else:
            self.cache.clear()
        self.save_cache()  # Persist changes
