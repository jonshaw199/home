from django.db import models
from core.models import Location, BaseModel


# Create your models here.
class DeviceType(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Device(BaseModel):
    name = models.CharField(max_length=100)
    last_status_update = models.DateTimeField(null=True, blank=True)
    device_type = models.ForeignKey(
        DeviceType, related_name="devices", on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Location, related_name="devices", on_delete=models.CASCADE
    )
    vendor_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name


class System(BaseModel):
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
        return f"{self.device.name}: System"


class Plug(BaseModel):
    device = models.OneToOneField(
        Device, on_delete=models.CASCADE, null=True, blank=True
    )

    is_on = models.BooleanField()

    def __str__(self):
        return f"{self.device.name}: Plug"


class Environmental(BaseModel):
    device = models.OneToOneField(
        Device, on_delete=models.CASCADE, null=True, blank=True
    )

    temperature_c = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.device.name}: Environmental"

    @property
    def temperature_f(self):
        if self.temperature_c is not None:
            return (self.temperature_c * 9 / 5) + 32
