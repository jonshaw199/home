from django.contrib import admin
from .models import Routine, Action


class ActionInline(admin.TabularInline):
    model = Action
    extra = 1  # How many extra blank action fields to show


@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ("name", "triggers", "repeat_interval")
    inlines = [ActionInline]  # Allows you to add Actions within the Routine form


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ("routine", "type", "eval_params")
