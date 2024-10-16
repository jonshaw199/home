from .models import Routine, Action
from core.serializers import UUIDModelSerializer


class ActionSerializer(UUIDModelSerializer):
    class Meta:
        model = Action
        fields = UUIDModelSerializer.Meta.fields + [
            "name",
            "active",
            "type",
            "eval_params",
            "routine",
        ]


class RoutineSerializer(UUIDModelSerializer):
    actions = ActionSerializer(many=True, read_only=True)

    class Meta:
        model = Routine
        fields = UUIDModelSerializer.Meta.fields + [
            "name",
            "active",
            "triggers",
            "repeat_interval",
            "eval_condition",
            "location",
            "actions",
        ]
