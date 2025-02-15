from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Message, Thread

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class ThreadCreateSerializer(serializers.Serializer):
    participant_id = serializers.IntegerField(
        help_text="ID of the user to create thread with"
    )

    def validate_participant_id(self, value):
        request = self.context.get('request')
        if value == request.user.id:
            raise serializers.ValidationError(
                "Cannot create thread with yourself"
            )
        return value


class ThreadReadSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Thread
        fields = ("id", "participants", "created", "updated")
        read_only_fields = fields


class MessageCreateSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=1000)


class MessageReadSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ("id", "sender", "text", "thread_id", "created", "is_read")
        read_only_fields = fields


class ThreadQueryParamsSerializer(serializers.Serializer):
    limit = serializers.IntegerField(required=False, min_value=1)
    offset = serializers.IntegerField(required=False, min_value=0)
    ordering = serializers.CharField(required=False)
