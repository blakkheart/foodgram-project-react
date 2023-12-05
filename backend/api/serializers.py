import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api.serializers_mixins import UserMixinSerializer
from recipe.models import (
    Ingredient,
    ReciepeShopList,
    Recipe,
    RecipeFavourite,
    RecipeIngredient,
    Tag,
)
from user.models import UserFollowing


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Сериализатор для изображений."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализитор для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализитор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализитор для ингредиентов в рецепте."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class UserSerializer(UserMixinSerializer):
    """Сериализитор для юзера."""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        read_only_fields = (
            'id',
            'is_subscribed',
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализитор для рецептов для показа."""

    image = Base64ImageField()
    tags = TagSerializer(many=True,)
    ingredients = IngredientRecipeSerializer(
        many=True, source='ingredients_with_amount'
    )
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = ('id', 'author')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return (
            RecipeFavourite.objects.select_related('recipe', 'user')
            .filter(user=user, recipe=obj)
            .exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return (
            ReciepeShopList.objects.select_related('recipe', 'user')
            .prefetch_related('recipe__tags')
            .filter(user=user, recipe=obj)
            .exists()
        )


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализитор для показа "коротких" рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class IngredientSerializerPOST(serializers.ModelSerializer):
    """Сериализитор для ингредиентов на запись."""

    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializerPOST(serializers.ModelSerializer):
    """Сериализитор для рецептов на запись."""

    image = Base64ImageField()
    ingredients = IngredientSerializerPOST(many=True, required=True)
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
        if not ingredients:
            raise serializers.ValidationError('Ingredients cannot be empty')
        tags = validated_data.pop('tags')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Tags should not be doubled')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            try:
                ing = Ingredient.objects.get(pk=ingredient.get('id'))
            except Ingredient.DoesNotExist:
                recipe.delete()
                raise serializers.ValidationError('Ingredient does not exist')
            amount = ingredient.get('amount')
            if amount < 1:
                recipe.delete()
                raise serializers.ValidationError(
                    'Amount cannot be less then 1'
                )
            try:
                obj, created = RecipeIngredient.objects.select_related(
                    'ingredient', 'recipe'
                ).get_or_create(ingredient=ing, recipe=recipe, amount=amount)
            except IntegrityError:
                recipe.delete()
                raise serializers.ValidationError(
                    'Ingredients should not be doubled'
                )
            if not created:
                recipe.delete()
                raise serializers.ValidationError(
                    'Ingredients should not be doubled'
                )
        return recipe

    def create_or_update_ingredients(self, ingredients, recipe_id):
        if not ingredients:
            raise serializers.ValidationError('Ingredients cannot be empty')
        ingr_set = set()
        for ingredient in ingredients:
            try:
                ing = Ingredient.objects.get(id=ingredient.get('id'))
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError('Ingredient does not exist')
            if ingredient.get('id') in ingr_set:
                raise serializers.ValidationError(
                    'Ingredients cannot be doubled'
                )
            ingr_set.add(ingredient.get('id'))
            amount = ingredient.get('amount')
            if amount < 1:
                raise serializers.ValidationError(
                    'Amount cannot be less then 1'
                )
            RecipeIngredient.objects.create(
                ingredient=ing,
                recipe=Recipe.objects.get(id=recipe_id),
                amount=amount,
            )
        return

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        if not validated_data.get('tags'):
            raise serializers.ValidationError('Tags should be in request')
        tags = validated_data.pop('tags', [])
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Tags cannot repeat')
        recipe_id = instance.id
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_or_update_ingredients(ingredients_data, recipe_id)
        instance.tags.set(tags)
        instance.save()
        return instance

    def to_representation(self, value):
        if isinstance(value, Recipe):
            serializer = RecipeSerializer(value, context=self.context)
        else:
            raise Exception('Unexpected type of tagged object')
        return serializer.data


class UserSubSerializer(UserMixinSerializer):
    """Сериализитор для подписок пользователя."""

    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        user = get_object_or_404(User, pk=obj.pk)
        recipes_limit = self.context.get('request').GET.get('recipes_limit')
        all_recipes = user.recipies.all()
        if recipes_limit:
            recipes_limit = int(recipes_limit)
            if recipes_limit > all_recipes.count():
                recipes_limit = all_recipes.count()
            recipes = all_recipes[:recipes_limit]
        else:
            recipes = all_recipes
        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        user = get_object_or_404(User, pk=obj.pk)
        return user.recipies.count()

    def create(self, validated_data):
        id_user_to_follow = self.context.get('view').kwargs.get('pk')
        user_to_follow = get_object_or_404(User, pk=id_user_to_follow)
        user = get_object_or_404(
            User, username=self.context.get('request').user.username
        )
        if user == user_to_follow:
            raise serializers.ValidationError('Cannot subscribe to yourself')
        obj, created = UserFollowing.objects.get_or_create(
            user=user_to_follow, following_user=user
        )
        if not created:
            raise serializers.ValidationError('Cannot subscribe twice')
        return user_to_follow
