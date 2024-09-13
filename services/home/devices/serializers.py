# serializers.py
from rest_framework import serializers
from .models import Device, DeviceType, System, Plug


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["device_type", "id", "location", "name"]


class DeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = ["id", "name"]


class SystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = System
        fields = ["device", "cpu_usage"]


class PlugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plug
        fields = ["device", "is_on"]
