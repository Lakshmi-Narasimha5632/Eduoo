from rest_framework import serializers

from .models import ConnectedPlatform


class ConnectedPlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectedPlatform
        fields = [
            "platform",
            "username",
            "connected",
            "token_expiry",
            "last_synced_at",
            "sync_status",
            "sync_error",
        ]
        read_only_fields = fields
