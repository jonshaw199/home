from django.db import models
from core.models import Location


# Create your models here.
class DeviceType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Device(models.Model):
    name = models.CharField(max_length=100)
    device_type = models.ForeignKey(
        DeviceType, related_name="devices", on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Location, related_name="devices", on_delete=models.CASCADE
    )
    vendor_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name


class System(models.Model):
    device = models.OneToOneField(
        Device, on_delete=models.CASCADE, null=True, blank=True
    )

    cpu_usage = models.FloatField(null=True, blank=True)
    cpu_temp = models.FloatField(null=True, blank=True)
    mem_usage = models.FloatField(null=True, blank=True)
    disk_usage = models.FloatField(null=True, blank=True)
    network_sent = models.BigIntegerField(null=True, blank=True)
    network_received = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return self.device.name


class Plug(models.Model):
    device = models.OneToOneField(
        Device, on_delete=models.CASCADE, null=True, blank=True
    )

    is_on = models.BooleanField()

    def __str__(self):
        return self.device.name
