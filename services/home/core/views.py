from django.contrib.auth.models import User, Group
from core.models import Location, Profile
from rest_framework import permissions, viewsets
from django.http import JsonResponse
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from core.serializers import (
    UserSerializer,
    GroupSerializer,
    LocationSerializer,
    ProfileSerializer,
)

from rest_framework import viewsets


class BaseUUIDViewSet(viewsets.ModelViewSet):
    """
    Base viewset that uses UUID for lookup.
    """

    lookup_field = "uuid"  # Use UUID for lookup across all inherited viewsets


# User doesn't have UUID at this time; keep using ModelViewSet here
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class ProfileViewSet(BaseUUIDViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAdminUser]


class GroupViewSet(BaseUUIDViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]


class LocationViewSet(BaseUUIDViewSet):
    queryset = Location.objects.all().order_by("name")
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]


def status_view(request):
    return JsonResponse({"status": "ok", "message": "Server is up and running"})


class TokenAuthWithProfile(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data["token"])
        profile = Profile.objects.get(user=token.user)
        return Response({"token": token.key, "profile": profile.uuid})
