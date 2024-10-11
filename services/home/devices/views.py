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


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer


class DeviceTypeViewSet(viewsets.ModelViewSet):
    queryset = DeviceType.objects.all()
    serializer_class = DeviceTypeSerializer


class SystemViewSet(viewsets.ModelViewSet):
    queryset = System.objects.all()
    serializer_class = SystemSerializer


class PlugViewSet(viewsets.ModelViewSet):
    queryset = Plug.objects.all()
    serializer_class = PlugSerializer


class EnvironmentalViewSet(viewsets.ModelViewSet):
    queryset = Environmental.objects.all()
    serializer_class = EnvironmentalSerializer


class LightViewSet(viewsets.ModelViewSet):
    queryset = Light.objects.all()
    serializer_class = LightSerializer
