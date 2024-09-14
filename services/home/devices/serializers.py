# serializers.py
from .models import Device, DeviceType, System, Plug
from core.serializers import UUIDModelSerializer


class DeviceSerializer(UUIDModelSerializer):
    class Meta:
        model = Device
        fields = UUIDModelSerializer.Meta.fields + ["device_type", "location", "name"]


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
