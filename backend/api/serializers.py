from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer as UserSerializerDjango
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.serializers_mixins import UserMixinSerializer
from api.validators import valid_image
from recipe.models import Ingredient, Recipe, RecipeIngredient, Tag
from user.models import UserFollowing


User = get_user_model()


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


class UserSerializer(UserSerializerDjango, UserMixinSerializer):
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
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

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


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализитор для показа "коротких" рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class CreateIngredientSerializer(serializers.ModelSerializer):
    """Сериализитор для ингредиентов на запись."""

    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError('Amount cannot be less then 1')
        return value


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализитор для рецептов на запись."""

    image = Base64ImageField(validators=[valid_image])
    ingredients = CreateIngredientSerializer(many=True, required=True)
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
        ingredients_id = Ingredient.objects.values_list('id', flat=True)
        for ingredient in ingredients:
            if ingredient.get('id') not in ingredients_id:
                recipe.delete()
                raise serializers.ValidationError('Ingredient does not exist')
            amount = ingredient.get('amount')
            try:
                obj, created = RecipeIngredient.objects.select_related(
                    'ingredient', 'recipe'
                ).get_or_create(
                    ingredient_id=ingredient.get('id'),
                    recipe=recipe,
                    amount=amount,
                )
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

    def to_representation(self, instance):
        if not isinstance(instance, Recipe):
            raise Exception('Unexpected type of tagged object')
        instance = self.context['view'].get_queryset().get(id=instance.pk)
        serializer = RecipeSerializer(instance, context=self.context)
        return serializer.data


class UserSubscribeSerializer(UserSerializerDjango, UserMixinSerializer):
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
        user_to_follow = validated_data['user_to_follow']
        user = validated_data['user']
        obj, created = UserFollowing.objects.get_or_create(
            user=user_to_follow, following_user=user
        )
        if not created:
            raise serializers.ValidationError('Cannot subscribe twice')
        return user_to_follow

    def validate(self, data):
        id_user_to_follow = self.context.get('view').kwargs.get('pk')
        user_to_follow = get_object_or_404(User, pk=id_user_to_follow)
        user = get_object_or_404(
            User, username=self.context.get('request').user.username
        )
        if user == user_to_follow:
            raise serializers.ValidationError('Cannot subscribe to yourself')
        data['user_to_follow'] = user_to_follow
        data['user'] = user
        return data
