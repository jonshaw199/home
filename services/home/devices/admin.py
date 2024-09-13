from django.contrib import admin
from .models import Device, DeviceType, Plug, System

# Register your models here.
admin.site.register(Device)
admin.site.register(DeviceType)
admin.site.register(Plug)
admin.site.register(System)
