# serializers.py
from rest_framework import serializers
from .models import Device, DeviceType


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["device_type", "id", "location", "name"]

class DeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = ["id", "name"]
