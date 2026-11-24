from rest_framework import serializers

from .models import DailyTask, DailyTaskPlan


class DailyTaskSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()
    external_url = serializers.CharField(source="problem_url", read_only=True)

    class Meta:
        model = DailyTask
        fields = [
            "id",
            "plan",
            "task_type",
            "title",
            "description",
            "topic",
            "difficulty",
            "estimated_minutes",
            "priority",
            "status",
            "is_completed",
            "problem_url",
            "external_url",
            "completed_at",
            "created_at",
        ]
        read_only_fields = fields

    def get_is_completed(self, obj):
        return obj.status == "completed"


class DailyTaskPlanSerializer(serializers.ModelSerializer):
    tasks = DailyTaskSerializer(many=True, read_only=True)
    target_minutes = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = DailyTaskPlan
        fields = [
            "id",
            "user",
            "date",
            "total_minutes",
            "target_minutes",
            "completed_minutes",
            "status",
            "is_completed",
            "tasks",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_target_minutes(self, obj):
        return obj.total_minutes

    def get_is_completed(self, obj):
        return obj.status == "completed"
