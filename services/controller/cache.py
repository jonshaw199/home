class Cache:
    def __init__(self):
        self.cache = {}

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

    def update(self, resource_type, resource_id, resource_data):
        if resource_type in self.cache and resource_id in self.cache[resource_type]:
            self.cache[resource_type][resource_id].update(resource_data)

    def delete(self, resource_type, resource_id):
        if resource_type in self.cache and resource_id in self.cache[resource_type]:
            del self.cache[resource_type][resource_id]

    def clear(self, resource_type=None):
        if resource_type:
            self.cache[resource_type] = {}
        else:
            self.cache.clear()
