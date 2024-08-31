from django.contrib import admin

from core.models import Location, Organization

# Register your models here.

admin.site.register(Organization)
admin.site.register(Location)
