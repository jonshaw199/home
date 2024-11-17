import os
import asyncio
from paho.mqtt.subscribeoptions import SubscribeOptions
from aiomqtt import Client, MqttError, ProtocolVersion
import logging

MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
DEVICE_ID = os.getenv("DEVICE_ID", "controller")

url = f"{MQTT_BROKER_HOST}/{MQTT_BROKER_PORT}"


class AsyncMqttClient:
    def __init__(self, on_message):
        self.on_message = on_message
        self.connect()

    def connect(self):
        self.client = Client(
            MQTT_BROKER_HOST,
            port=MQTT_BROKER_PORT,
            protocol=ProtocolVersion.V5,
            identifier=DEVICE_ID,
        )

    async def handle_message(self, message):
        logging.info(f"Received message on topic {message.topic}")
        try:
            decoded_payload = message.payload.decode("utf-8")
            self.on_message(message.topic, decoded_payload)
        except Exception as e:
            logging.error(f"Failed to handle message: {e}")

    async def publish(self, topic, message):
        logging.info(f"Publishing message to topic {topic}: {message}")

        try:
            await self.client.publish(topic, message)
        except Exception as e:
            logging.error(f"Unable to publish; error: {e}")

    async def subscribe(self, topic):
        while 1:
            try:
                await self._subscribe(topic)
            except Exception as e:
                logging.error(f"Subscribe error: {e}")
                await asyncio.sleep(1)
                logging.warn("Attempting to reconnect to MQTT broker")
                self.connect()

    async def _subscribe(self, topic):
        logging.info(f"Subscribing to topic: {topic}")

        async with self.client as client:
            options = SubscribeOptions(noLocal=True)
            await client.subscribe(topic, options=options)
            async for message in client.messages:
                await self.handle_message(message)
