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
        read_only_fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id', 'name', 'measurement_unit')


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
    image = Base64ImageField()
    tags = TagSerializer(many=True,)
    ingredients = IngredientRecipeSerializer(many=True,)
    author = UserSerializer(read_only=True)
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


class ShoppingCartOrFavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')




"""------------------------------"""

class IngredientSerializePOST(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.FloatField()
    class Meta:
        fields = ('id', 'amount')


class RecipeSerializerPOST(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = IngredientSerializePOST(many=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',   
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient=Ingredient.objects.get(pk=ingredient.get('id')),
                recipe=recipe,
                amount=ingredient.get('amount')
            )
        return recipe

    def create_or_update_ingredients(self, ingredients, recipe_id):
        ingr_ids = []
        for ingredient in ingredients:
            ingredient_instance, created = (
                RecipeIngredient.
                objects.
                update_or_create(
                    ingredient=Ingredient.objects.get(id=ingredient.get('id')),
                    recipe=Recipe.objects.get(id=recipe_id),
                    amount=ingredient.get('amount'),
                    defaults=ingredient)
            )
            ingr_ids.append(ingredient_instance.pk)
        return ingr_ids

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        recipe_id = instance.id
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        instance.ingredients.set(
            self.create_or_update_ingredients(ingredients_data, recipe_id))
        if validated_data.get('tags'):
            instance.tags.set(validated_data.get('tags'))
        instance.save()
        return instance

    def to_representation(self, value):
        if isinstance(value, Recipe):
            serializer = RecipeSerializer(value, context=self.context)
        else:
            raise Exception('Unexpected type of tagged object')
        return serializer.data
