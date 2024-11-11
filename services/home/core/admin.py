from django.contrib import admin

from core.models import Location, Profile


class ReadOnlyUUIDAdmin(admin.ModelAdmin):
    readonly_fields = ("uuid",)


# Register your models here.

admin.site.register(Location, ReadOnlyUUIDAdmin)
admin.site.register(Profile, ReadOnlyUUIDAdmin)
