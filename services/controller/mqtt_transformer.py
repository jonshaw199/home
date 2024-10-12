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

    # Call back with transformed message instead of returning to handle cases where 1 original message equals multiple transformed messages
    @classmethod
    def transform(cls, message, topic, cb, **kwargs):
        try:
            dest = str(topic)  # Be careful; in aiomqtt, this is a Topic obj

            # Check if a transformer exists by matching regex patterns against 'dest'
            for pattern, transformer in cls.transformers.items():
                if re.match(pattern, dest):
                    logging.info(f"Applying transformer for pattern: {pattern}")
                    # Apply the transformer and return the transformed message
                    return transformer(message, dest, cb, **kwargs)

            # If no transformer is found, use the original message
            logging.info("No transformer found; consuming as-is")
            cb(message)
        except Exception as e:
            logging.error(f"Transformation error: {e}")


# Example: {"id":0, "source":"init", "output":false, "apower":0.0, "voltage":122.9, "current":0.000, "aenergy":{"total":0.000,"by_minute":[0.000,0.000,0.000],"minute_ts":1726942679},"temperature":{"tC":45.9, "tF":114.7}}
@MqttTransformerRegistry.register(r"^plugs/[0-9a-fA-F-]{36}/status/switch:0$")
def transform_plug_status_message(message, topic, cb, **kwargs):
    logging.info(f"Transforming plug status message {message}")
    device_id = topic.split("/")[1]
    obj = json.loads(message)
    transformed = {
        "src": device_id,
        "dest": f"plugs/{device_id}/status",
        "action": ACTION_PLUG_STATUS,
        "body": {"is_on": obj["output"]},
    }
    cb(json.dumps(transformed))
