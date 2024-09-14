#!/usr/bin/env python3

from django.urls import re_path

from . import consumers

websocket_urlPatterns = [re_path("ws/clients", consumers.ClientConsumer.as_asgi())]
