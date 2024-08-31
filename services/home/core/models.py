from django.db import models


# Create your models here.
class Organization(models.Model):
    name = models.CharField()

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField()

    def __str__(self):
        return self.name
