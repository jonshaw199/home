from django.contrib import admin
from .models import Device, DeviceType, Plug, System, Environmental, Light
from core.admin import ReadOnlyUUIDAdmin

# Register your models here.
admin.site.register(Device, ReadOnlyUUIDAdmin)
admin.site.register(DeviceType, ReadOnlyUUIDAdmin)
admin.site.register(Plug, ReadOnlyUUIDAdmin)
admin.site.register(System, ReadOnlyUUIDAdmin)
admin.site.register(Environmental, ReadOnlyUUIDAdmin)
admin.site.register(Light, ReadOnlyUUIDAdmin)
