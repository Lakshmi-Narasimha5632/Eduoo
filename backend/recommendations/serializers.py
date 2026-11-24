from rest_framework import serializers

from .models import Recommendation


class RecommendationSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(source="action", read_only=True)
    estimated_time_minutes = serializers.IntegerField(source="estimated_time", read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Recommendation
        fields = [
            "id",
            "category",
            "priority",
            "title",
            "description",
            "action",
            "reason",
            "estimated_time",
            "estimated_time_minutes",
            "status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "reason",
            "estimated_time_minutes",
            "status",
            "created_at",
        ]

    def get_status(self, obj):
        # Allow stored status in action or default to pending
        if hasattr(obj, "_status"):
            return obj._status
        return "pending"
