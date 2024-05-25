from rest_framework import permissions, viewsets

from locations.models import Location
from locations.serializers import LocationSerializer

# Create your views here.


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all().order_by('name')
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]
