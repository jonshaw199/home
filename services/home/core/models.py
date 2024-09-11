from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Location(models.Model):
    name = models.CharField()
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sublocations",
    )

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    locations = models.ManyToManyField(Location, related_name="users")

    def __str__(self):
        return self.user.username
