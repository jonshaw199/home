import re
import logging
import json

ACTION_PLUG_STATUS = "plug__status"

SHELLY_METHOD_NOTIFY_FULL_STATUS = "NotifyFullStatus"


class MqttTransformerRegistry:
    transformers = {}

    @classmethod
    def register(cls, pattern):
        def decorator(transformer_callback):
            cls.transformers[pattern] = transformer_callback
            return transformer_callback  # Return the callback unmodified

        return decorator

    @classmethod
    def transform(cls, message, topic):
        dest = topic

        # Check if a transformer exists by matching regex patterns against 'dest'
        for pattern, transformer in cls.transformers.items():
            if re.match(pattern, dest):
                logging.info(f"Applying transformer for pattern: {pattern}")
                # Apply the transformer and return the transformed message
                transformed_message = transformer(message, topic)
                return transformed_message

        # If no transformer is found, return the original message
        logging.info("No transformer found; returning")
        return message


# Example: `{'src': 'shellyplugus-a0dd6c27a4dc', 'dst': 'cf7d8486-18ad-4064-b757-e671a4749a3e/events', 'method': 'NotifyFullStatus', 'params': {'ts': 1726900602.35, 'ble': {}, 'cloud': {'connected': False}, 'mqtt': {'connected': True}, 'switch:0': {'id': 0, 'source': 'init', 'output': False, 'apower': 0.0, 'voltage': 124.1, 'current': 0.0, 'aenergy': {'total': 0.0, 'by_minute': [0.0, 0.0, 0.0], 'minute_ts': 1726900600}, 'temperature': {'tC': 47.7, 'tF': 117.8}}, 'sys': {'mac': 'A0DD6C27A4DC', 'restart_required': False, 'time': '23:36', 'unixtime': 1726900602, 'uptime': 79378, 'ram_size': 261220, 'ram_free': 124584, 'fs_size': 458752, 'fs_free': 151552, 'cfg_rev': 6, 'kvs_rev': 0, 'schedule_rev': 0, 'webhook_rev': 0, 'available_updates': {'stable': {'version': '1.3.3'}}, 'reset_reason': 3}, 'wifi': {'sta_ip': '10.199.1.13', 'status': 'got ip', 'ssid': 'Shaw Family', 'rssi': -37}, 'ws': {'connected': False}}}`
@MqttTransformerRegistry.register(r"^plugs/[0-9a-fA-F-]{36}/status/switch:0$")
def transform_plug_status_message(message, topic):
    logging.info(f"Transforming plug status message {message}")
    device_id = topic.split("/")[1]
    obj = json.loads(message)
    transformed = {
        "src": device_id,
        "dest": f"plugs/{device_id}/status",
        "action": ACTION_PLUG_STATUS,
        "body": {"is_on": obj["output"]},
    }
    return json.dumps(transformed)
