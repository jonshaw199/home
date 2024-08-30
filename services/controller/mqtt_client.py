import os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from websocket_client import WebsocketClient
import logging

load_dotenv()
MQTT_BROKER_HOST = os.getenv('MQTT_BROKER_HOST')

class MqttClient():
  def __init__(self, on_connect, on_message):
    self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    self.client.on_connect = self.handle_connect
    self.client.on_message = self.handle_message
    self.on_connect = on_connect
    self.on_message = on_message

  # The callback for when the client receives a CONNACK response from the server.
  def handle_connect(self, client, userdata, flags, reason_code, properties = None):
    logging.info(f"Connected with result code {reason_code}")
    self.on_connect()
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")

  # The callback for when a PUBLISH message is received from the server.
  def handle_message(self, client, userdata, msg):
    logging.info(f"Handle message; topic: {msg.topic}; payload: {msg.payload}")
    decoded = ''
    try:
      decoded = msg.payload.decode("utf-8")
    except:
      logging.error(f"Unable to decode message (topic: {msg.topic})")
    self.on_message(msg.topic, msg.payload.decode("utf-8"))

  def connect(self):
    self.client.connect(MQTT_BROKER_HOST)

  def publish(self, topic, message):
    self.client.publish(topic, message)

  def subscribe(self, topic):
    logging.info(f'Subscribing to topic: {topic}')
    self.client.subscribe(topic)

  def start(self):
    self.connect()
    self.client.loop_forever()
