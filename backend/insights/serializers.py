from rest_framework import serializers

from .models import Insight


class InsightSerializer(serializers.ModelSerializer):
    description = serializers.CharField(source="message", read_only=True)
    category = serializers.SerializerMethodField()
    platform = serializers.SerializerMethodField()
    action_items = serializers.SerializerMethodField()

    class Meta:
        model = Insight
        fields = [
            "id",
            "type",
            "priority",
            "title",
            "message",
            "description",
            "platform",
            "category",
            "action_items",
            "metadata",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "description",
            "platform",
            "category",
            "action_items",
            "created_at",
        ]

    def get_category(self, obj):
        if obj.metadata and isinstance(obj.metadata, dict) and obj.metadata.get("category"):
            return str(obj.metadata["category"]).lower()
        t = (obj.type or "").lower()
        if t in ["coding", "difficulty", "topic", "performance"]:
            return "coding"
        if t in ["platform", "activity"]:
            return "platform"
        if t in ["skills", "skill_gap", "skill"]:
            return "skills"
        if t in ["career", "interview", "consistency", "projects"]:
            return t
        return "general"

    def get_platform(self, obj):
        if obj.metadata and isinstance(obj.metadata, dict) and obj.metadata.get("platform"):
            return str(obj.metadata["platform"]).lower()
        return "eduoo_ai"

    def get_action_items(self, obj):
        if obj.metadata and isinstance(obj.metadata, dict) and "action_items" in obj.metadata:
            return obj.metadata["action_items"]
        return [
            f"Review {obj.title} recommendations in your study plan.",
            "Complete today's scheduled practice problem to reinforce learning.",
        ]
