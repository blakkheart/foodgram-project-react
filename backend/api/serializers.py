import base64

from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist

from recipe.models import (
    Recipe,
    Tag,
    Ingredient,
    RecipeIngredient,
)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )

    def get_amount(self, obj):
        qset = (
            RecipeIngredient.
            objects.
            select_related('recipe', 'ingredient').
            filter(ingredient=obj)
        )
        for object in qset:
            return object.amount


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        try:
            User.objects.filter(pk=obj.pk).get(follower=user)
            return True
        except ObjectDoesNotExist:
            return False


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True,)
    ingredients = IngredientRecipeSerializer(many=True,)
    author = UserSerializer()
    is_favourited = serializers.SerializerMethodField()
    is_in_shipping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favourited',
            'is_in_shipping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = ('id', 'author')

    def get_is_favourited(self, obj):
        user = self.context.get('request').user
        try:
            User.objects.filter(favourite=obj).get(username=user)
            return True
        except ObjectDoesNotExist:
            return False

    def get_is_in_shipping_cart(self, obj):
        user = self.context.get('request').user
        try:
            User.objects.filter(shop_list=obj).get(username=user)
            return True
        except ObjectDoesNotExist:
            return False
