from django.contrib.auth.models import User, Group
from core.models import Location, Profile
from rest_framework import permissions, viewsets
from django.http import JsonResponse

from core.serializers import (
    UserSerializer,
    GroupSerializer,
    LocationSerializer,
    ProfileSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAdminUser]


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all().order_by("name")
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]


def status_view(request):
    return JsonResponse({"status": "ok", "message": "Server is up and running"})
