#!/usr/bin/env python3

from django.contrib.auth.models import User, Group
from core.models import Location, Profile, BaseModel
from rest_framework import serializers
from django.db import models


from rest_framework import serializers
from django.db import models


class UUIDModelSerializer(serializers.ModelSerializer):
    def build_field(self, field_name, info, model_class, nested_depth):
        """
        Override this method to replace foreign key 'id' references with 'uuid'.
        """
        if hasattr(model_class, field_name):
            field = getattr(model_class, field_name)
            if isinstance(field, (models.ForeignKey, models.OneToOneField)):
                # Replace with the UUID of the related model
                return (
                    serializers.UUIDField(source=f"{field_name}.uuid", read_only=True),
                    True,
                )
            elif isinstance(field, models.ManyToManyField):
                # For ManyToMany, we'll handle it in to_representation()
                return super().build_field(field_name, info, model_class, nested_depth)

        return super().build_field(field_name, info, model_class, nested_depth)

    class Meta:
        # Specify which fields to include. Use 'uuid' instead of 'id'
        fields = ["uuid"]  # This can be expanded or modified in subclasses

    def to_representation(self, instance):
        """Override `to_representation` to replace foreign key IDs, M2M IDs, and reverse IDs with UUIDs."""
        representation = super().to_representation(instance)

        for field_name, field in self.fields.items():
            try:
                model_field = self.Meta.model._meta.get_field(field_name)
            except models.FieldDoesNotExist:
                # Handle reverse relationships not in _meta (e.g., related_name fields)
                related_objects = getattr(instance, field_name, None)
                if hasattr(
                    related_objects, "all"
                ):  # Many-to-One or Many-to-Many reverse
                    uuid_list = [
                        related_instance.uuid
                        for related_instance in related_objects.all()
                        if hasattr(related_instance, "uuid")
                    ]
                    representation[field_name] = uuid_list
                elif related_objects and hasattr(
                    related_objects, "uuid"
                ):  # One-to-One reverse
                    representation[field_name] = related_objects.uuid
                continue

            # Handle ForeignKey and OneToOne relationships
            if isinstance(model_field, (models.ForeignKey, models.OneToOneField)):
                related_instance = getattr(instance, field_name, None)
                if related_instance and hasattr(related_instance, "uuid"):
                    representation[field_name] = related_instance.uuid

            # Handle ManyToMany relationships
            elif isinstance(model_field, models.ManyToManyField):
                related_manager = getattr(instance, field_name)
                uuid_list = [
                    related_instance.uuid
                    for related_instance in related_manager.all()
                    if hasattr(related_instance, "uuid")
                ]
                representation[field_name] = uuid_list

        # Handle reverse OneToOneField manually (e.g., "plug" in Device)
        for related_object in instance._meta.related_objects:
            if isinstance(related_object, models.OneToOneRel):
                related_field_name = related_object.related_name or related_object.name
                related_instance = getattr(instance, related_field_name, None)
                if related_instance and hasattr(related_instance, "uuid"):
                    representation[related_field_name] = related_instance.uuid

        return representation


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
