from rest_framework import viewsets
from .models import Device, DeviceType, System, Plug, Environmental, Light
from .serializers import (
    DeviceSerializer,
    DeviceTypeSerializer,
    SystemSerializer,
    PlugSerializer,
    EnvironmentalSerializer,
    LightSerializer,
)
from core.views import BaseUUIDViewSet


class DeviceViewSet(BaseUUIDViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer


class DeviceTypeViewSet(BaseUUIDViewSet):
    queryset = DeviceType.objects.all()
    serializer_class = DeviceTypeSerializer


class SystemViewSet(BaseUUIDViewSet):
    queryset = System.objects.all()
    serializer_class = SystemSerializer


class PlugViewSet(BaseUUIDViewSet):
    queryset = Plug.objects.all()
    serializer_class = PlugSerializer


class EnvironmentalViewSet(BaseUUIDViewSet):
    queryset = Environmental.objects.all()
    serializer_class = EnvironmentalSerializer


class LightViewSet(BaseUUIDViewSet):
    queryset = Light.objects.all()
    serializer_class = LightSerializer
