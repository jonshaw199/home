#!/usr/bin/env python3

from lights.models import Light
from rest_framework import serializers
from core.serializers import UUIDModelSerializer


class LightSerializer(UUIDModelSerializer):
    class Meta:
        model = Light
        fields = UUIDModelSerializer.Meta.fields + ["name", "location"]
