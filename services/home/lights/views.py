from rest_framework import permissions, viewsets

from lights.models import Light
from lights.serializers import LightSerializer

# Create your views here.


class LightViewSet(viewsets.ModelViewSet):
    queryset = Light.objects.all().order_by('name')
    serializer_class = LightSerializer
    permission_classes = [permissions.IsAuthenticated]
