from django.db import models
from core.models import Location, BaseModel


class Routine(BaseModel):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    triggers = models.TextField(
        null=True, blank=True
    )  # A comma-separated list of times, timestamps, and/or action types
    repeat_interval = models.DurationField(
        null=True, blank=True
    )  # Optional repeat interval
    eval_condition = models.TextField(
        null=True, blank=True
    )  # Optional condition to be eval()'d

    location = models.ForeignKey(
        Location, related_name="routines", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Action(BaseModel):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    type = models.CharField(max_length=100)  # Required action type
    eval_params = models.TextField(
        null=True, blank=True
    )  # Optional params to be eval()'d

    routine = models.ForeignKey(
        Routine, related_name="actions", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name
