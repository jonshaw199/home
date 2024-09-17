import os
import paho.mqtt.client as mqtt
from paho.mqtt.subscribeoptions import SubscribeOptions
from dotenv import load_dotenv
import logging

load_dotenv()
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
MQTT_KEEP_ALIVE_INTERVAL = int(os.getenv("MQTT_KEEP_ALIVE_INTERVAL", 60))


class MqttClient:
    def __init__(self, on_connect, on_message):
        # Initialize MQTT client with the latest version of Paho MQTT
        self.client = mqtt.Client(protocol=mqtt.MQTTv5)
        self.client.on_connect = self.handle_connect
        self.client.on_message = self.handle_message
        self.client.on_disconnect = self.handle_disconnect

        self.on_connect = on_connect
        self.on_message = on_message

    # The callback for when the client receives a CONNACK response from the server.
    def handle_connect(self, client, userdata, flags, reason_code, properties=None):
        logging.info(f"Connected with result code {reason_code}")
        if reason_code == 0:
            # Call the user-defined on_connect method
            self.on_connect()
        else:
            logging.error(f"Connection failed with reason code {reason_code}")

    # The callback for when a PUBLISH message is received from the server.
    def handle_message(self, client, userdata, msg):
        logging.info(
            f"Received message on topic {msg.topic} with payload: {msg.payload}"
        )
        try:
            decoded_payload = msg.payload.decode("utf-8")
            self.on_message(msg.topic, decoded_payload)
        except Exception as e:
            logging.error(f"Failed to decode message: {e}")

    # The callback for when the client disconnects from the broker.
    def handle_disconnect(self, client, userdata, ws, obj):  # What is `obj`?
        logging.info("MQTT disconnected.")
        self.reconnect()

    def connect(self):
        try:
            self.client.connect(
                MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_KEEP_ALIVE_INTERVAL
            )
        except Exception as e:
            logging.error(f"Failed to connect to MQTT broker: {e}")
            self.reconnect()

    def reconnect(self):
        try:
            logging.info("Attempting to reconnect to MQTT broker...")
            self.client.reconnect()
        except Exception as e:
            logging.error(f"Reconnection attempt failed: {e}")
            # You may want to implement an exponential backoff or a delay here before retrying

    def publish(self, topic, message):
        logging.info(f"Publishing message to topic {topic}: {message}")
        self.client.publish(topic, message)

    def subscribe(self, topic):
        logging.info(f"Subscribing to topic: {topic}")
        options = SubscribeOptions(noLocal=True)
        self.client.subscribe(topic, options=options)

    def start(self):
        self.connect()
        self.client.loop_forever()
