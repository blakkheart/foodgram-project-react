from django.contrib.auth import get_user_model
from rest_framework import serializers

from user.models import UserFollowing

User = get_user_model()


class UserMixinSerializer(serializers.ModelSerializer):
    """Миксин для для сериалайзера юзера и подписок."""

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return UserFollowing.objects.filter(
            user=obj, following_user=user
        ).exists()
