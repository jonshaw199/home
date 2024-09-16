from rest_framework import viewsets
from .models import Device, DeviceType, System, Plug, Environmental
from .serializers import (
    DeviceSerializer,
    DeviceTypeSerializer,
    SystemSerializer,
    PlugSerializer,
    EnvironmentalSerializer,
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
