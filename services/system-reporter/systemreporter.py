import paho.mqtt.client as mqtt
import psutil
import json
import time
import logging
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

# Get environment variables
mqtt_broker_host = os.getenv("MQTT_BROKER_HOST", "localhost")
mqtt_broker_port = int(os.getenv("MQTT_BROKER_PORT", 1883))
mqtt_topic = os.getenv("MQTT_TOPIC", "")
mqtt_action = os.getenv("MQTT_ACTION", "system__status")
interval = os.getenv("PUB_INTERVAL_SEC", 60)
# TODO: get this from somewhere else maybe NVS
device_id = os.getenv("DEVICE_ID", "")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(threadName)s] [%(filename)s:%(lineno)d] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()],
)

# MQTT client setup
client = mqtt.Client()


# Define the on_disconnect callback
def on_disconnect(client, userdata, rc):
    logging.warning(f"Disconnected with result code {rc}. Attempting to reconnect.")
    while True:
        try:
            client.reconnect()
            logging.info("Reconnected successfully.")
            break
        except Exception as e:
            logging.error(f"Reconnection failed: {e}")
            time.sleep(5)  # Wait before retrying


# Set the callback function
client.on_disconnect = on_disconnect

# Connect to MQTT broker and start the network loop
client.connect(mqtt_broker_host, mqtt_broker_port, 60)
client.loop_start()  # Start the loop in a separate thread


def publish_system_metrics():
    while True:
        metrics = {
            # Required
            "src": device_id,
            "dest": mqtt_topic,
            "action": mqtt_action,
            "body": {
                "cpu_usage": psutil.cpu_percent(),
                "cpu_temperature": (
                    psutil.sensors_temperatures().get("cpu_thermal", [])[0].current
                    if psutil.sensors_temperatures().get("cpu_thermal")
                    else None
                ),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage("/").percent,
                "network_sent": psutil.net_io_counters().bytes_sent,
                "network_received": psutil.net_io_counters().bytes_recv,
            },
        }

        # Serialize the metrics to a JSON string
        metrics_json = json.dumps(metrics)
        client.publish(mqtt_topic, metrics_json)
        logging.debug(f"Published: {metrics_json}")

        # Wait for 60 seconds before sending the next update
        time.sleep(int(interval))


if __name__ == "__main__":
    publish_system_metrics()
