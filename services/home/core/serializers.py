#!/usr/bin/env python3

from django.contrib.auth.models import User, Group
from core.models import Location, Profile, BaseModel
from rest_framework import serializers
from django.db import models


class UUIDModelSerializer(serializers.ModelSerializer):
    def build_field(self, field_name, info, model_class, nested_depth):
        """
        This method is called to construct each field in the serializer.
        We override it to replace foreign key 'id' references with 'uuid'.
        """
        # Check if the field name corresponds to a ForeignKey field
        if hasattr(model_class, field_name):
            field = getattr(model_class, field_name)
            if isinstance(field, models.ForeignKey):
                # Replace with the UUID of the related model
                return (
                    serializers.UUIDField(source=f"{field_name}.uuid", read_only=True),
                    True,
                )

        # Default behavior for other fields
        return super().build_field(field_name, info, model_class, nested_depth)

    class Meta:
        # Specify which fields to include. Use 'uuid' instead of 'id'
        fields = ["uuid"]  # This can be expanded or modified in subclasses

    def to_representation(self, instance):
        """Override `to_representation` to replace foreign key IDs with UUIDs."""
        representation = super().to_representation(instance)

        for field_name, field in self.fields.items():
            # Check if the field is a foreign key
            model_field = self.Meta.model._meta.get_field(field_name)
            if isinstance(model_field, models.ForeignKey):
                # Get the related instance (e.g., instance.device_type)
                related_instance = getattr(instance, field_name, None)
                # Replace the ID with the related instance's UUID if it exists
                if related_instance and hasattr(related_instance, "uuid"):
                    representation[field_name] = related_instance.uuid

        return representation


"""
    def to_representation(self, instance):
        # Remove the 'id' field if present in the serialized output
        data = super().to_representation(instance)
        data.pop("id", None)  # Remove 'id' if it exists
        return data
"""


class UserSerializer(UUIDModelSerializer):
    class Meta:
        model = User
        fields = UUIDModelSerializer.Meta.fields + [
            "url",
            "username",
            "email",
            "is_staff",
            "is_superuser",
            "groups",
        ]


class ProfileSerializer(UUIDModelSerializer):
    class Meta:
        model = Profile
        fields = UUIDModelSerializer.Meta.fields + ["locations"]


class GroupSerializer(UUIDModelSerializer):
    class Meta:
        model = Group
        fields = UUIDModelSerializer.Meta.fields + ["url", "name"]


class LocationSerializer(UUIDModelSerializer):
    class Meta:
        model = Location
        fields = UUIDModelSerializer.Meta.fields + ["name", "parent"]
