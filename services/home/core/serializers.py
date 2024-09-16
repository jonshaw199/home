#!/usr/bin/env python3

from django.contrib.auth.models import User, Group
from core.models import Location, Profile, BaseModel
from rest_framework import serializers
from django.db import models
from django.core.exceptions import FieldDoesNotExist
from rest_framework import serializers
from django.db import models


class UUIDModelSerializer(serializers.ModelSerializer):
    def build_field(self, field_name, info, model_class, nested_depth):
        if hasattr(model_class, field_name):
            field = getattr(model_class, field_name)
            if isinstance(field, (models.ForeignKey, models.OneToOneField)):
                return (
                    serializers.UUIDField(source=f"{field_name}.uuid", read_only=True),
                    True,
                )
            elif isinstance(field, models.ManyToManyField):
                return super().build_field(field_name, info, model_class, nested_depth)

        return super().build_field(field_name, info, model_class, nested_depth)

    class Meta:
        fields = ["uuid"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        for field_name, field in self.fields.items():
            # Check if the field is a property, skip _meta.get_field lookup for properties
            if hasattr(self.Meta.model, field_name) and not hasattr(
                self.Meta.model._meta, "get_field"
            ):
                representation[field_name] = getattr(instance, field_name, None)
                continue

            try:
                model_field = self.Meta.model._meta.get_field(field_name)
            except FieldDoesNotExist:
                related_objects = getattr(instance, field_name, None)
                if hasattr(related_objects, "all"):
                    uuid_list = [
                        related_instance.uuid
                        for related_instance in related_objects.all()
                        if hasattr(related_instance, "uuid")
                    ]
                    representation[field_name] = uuid_list
                elif related_objects and hasattr(related_objects, "uuid"):
                    representation[field_name] = related_objects.uuid
                continue

            if isinstance(model_field, (models.ForeignKey, models.OneToOneField)):
                related_instance = getattr(instance, field_name, None)
                if related_instance and hasattr(related_instance, "uuid"):
                    representation[field_name] = related_instance.uuid

            elif isinstance(model_field, models.ManyToManyField):
                related_manager = getattr(instance, field_name)
                uuid_list = [
                    related_instance.uuid
                    for related_instance in related_manager.all()
                    if hasattr(related_instance, "uuid")
                ]
                representation[field_name] = uuid_list

        for related_object in instance._meta.related_objects:
            if isinstance(related_object, models.OneToOneRel):
                related_field_name = related_object.related_name or related_object.name
                related_instance = getattr(instance, related_field_name, None)
                if related_instance and hasattr(related_instance, "uuid"):
                    representation[related_field_name] = related_instance.uuid

        return representation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "url",
            "username",
            "email",
            "is_staff",
            "is_superuser",
            "groups",
        ]


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "url", "name"]


class ProfileSerializer(UUIDModelSerializer):
    class Meta:
        model = Profile
        fields = UUIDModelSerializer.Meta.fields + ["locations"]


class LocationSerializer(UUIDModelSerializer):
    class Meta:
        model = Location
        fields = UUIDModelSerializer.Meta.fields + ["name", "parent"]
