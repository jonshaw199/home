# serializers.py
from .models import Device, DeviceType, System, Plug, Environmental
from core.serializers import UUIDModelSerializer
from rest_framework import serializers


class DeviceSerializer(UUIDModelSerializer):
    class Meta:
        model = Device
        fields = UUIDModelSerializer.Meta.fields + [
            "device_type",
            "location",
            "name",
            "last_status_update",
        ]


class DeviceTypeSerializer(UUIDModelSerializer):
    class Meta:
        model = DeviceType
        fields = UUIDModelSerializer.Meta.fields + ["name"]


class SystemSerializer(UUIDModelSerializer):
    class Meta:
        model = System
        fields = UUIDModelSerializer.Meta.fields + ["device", "cpu_usage"]


class PlugSerializer(UUIDModelSerializer):
    class Meta:
        model = Plug
        fields = UUIDModelSerializer.Meta.fields + ["device", "is_on"]


class EnvironmentalSerializer(UUIDModelSerializer):
    temperature_f = serializers.FloatField(
        read_only=True
    )  # Adjusted to read the property directly

    class Meta:
        model = Environmental
        fields = UUIDModelSerializer.Meta.fields + [
            "device",
            "humidity",
            "temperature_c",
            "temperature_f",
        ]
