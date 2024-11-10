from django.contrib.auth.models import User
from django.db import models
import uuid
from mptt.models import MPTTModel, TreeForeignKey


class BaseModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Location(MPTTModel):
    # Explicitly add uuid here since it doesnt extend from BaseModel
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    parent = TreeForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )

    class MPTTMeta:
        order_insertion_by = ["name"]

    def __str__(self):
        return self.name


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    locations = models.ManyToManyField(Location, related_name="users")

    def __str__(self):
        return self.user.username
