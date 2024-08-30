import time
import psutil
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get environment variables
mqtt_broker_host = os.getenv("MQTT_BROKER_HOST", "localhost")
mqtt_broker_port = int(os.getenv("MQTT_BROKER_PORT", 1883))
mqtt_topic = os.getenv("MQTT_TOPIC", "system/status")
interval = os.getenv("PUB_INTERVAL_SEC", 60)

# MQTT client setup
client = mqtt.Client()

# Connect to MQTT broker
client.connect(mqtt_broker_host, mqtt_broker_port, 60)

def publish_system_metrics():
    while True:
        metrics = {
            "cpu_usage": psutil.cpu_percent(),
            "cpu_temperature": psutil.sensors_temperatures().get("cpu_thermal", [])[0].current if psutil.sensors_temperatures().get("cpu_thermal") else None,
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network_sent": psutil.net_io_counters().bytes_sent,
            "network_received": psutil.net_io_counters().bytes_recv,
        }

        client.publish(mqtt_topic, str(metrics))
        print(f"Published: {metrics}")

        # Wait for 60 seconds before sending the next update
        time.sleep(interval)

if __name__ == "__main__":
    publish_system_metrics()

