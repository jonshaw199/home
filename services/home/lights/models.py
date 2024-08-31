from django.db import models

from core.models import Location

# Create your models here.


class Light(models.Model):
    name = models.CharField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
