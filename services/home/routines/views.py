from rest_framework import viewsets
from .models import Routine, Action
from .serializers import RoutineSerializer, ActionSerializer
from core.views import BaseUUIDViewSet


class RoutineViewSet(BaseUUIDViewSet):
    queryset = Routine.objects.all()
    serializer_class = RoutineSerializer


class ActionViewSet(BaseUUIDViewSet):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
