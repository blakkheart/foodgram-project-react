from django.contrib.auth import get_user_model
from django.db import transaction
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
            raise serializers.ValidationError(
                'Поле amount не может быть меньше 1.'
            )
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

    def validate(self, data):
        if not data.get('tags'):
            raise serializers.ValidationError(
                'Поле tags не может быть пустым.'
            )
        if not data.get('ingredients'):
            raise serializers.ValidationError(
                'Поле ingredients не может быть пустым.'
            )
        if len(data.get('tags')) != len(set(data.get('tags'))):
            raise serializers.ValidationError('Теги не могут дублироваться.')
        ingredients_ids_from_db = set(
            Ingredient.objects.values_list('id', flat=True)
        )
        ingredient_ids = []
        for ingredient in data.get('ingredients'):
            if ingredient.get('id') not in ingredients_ids_from_db:
                raise serializers.ValidationError('Ингредиент не существует.')
            ingredient_ids.append(ingredient.get('id'))
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингрединты не могут дублироваться.'
            )
        prepared_ingredients = Ingredient.objects.filter(id__in=ingredient_ids)
        data['prepared_ingredients'] = prepared_ingredients
        return data

    @transaction.atomic
    def set_ingredients_and_tags(
        self, recipe, ingredients, prepared_ingredients, tags
    ):
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=prepared_ingredients.get(pk=ingredient['id']),
                    amount=ingredient['amount'],
                )
                for ingredient in ingredients
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        prepared_ingredients = validated_data.pop('prepared_ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.set_ingredients_and_tags(
            recipe=recipe,
            ingredients=ingredients,
            prepared_ingredients=prepared_ingredients,
            tags=tags,
        )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        prepared_ingredients = validated_data.pop('prepared_ingredients')
        tags = validated_data.pop('tags', [])
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.set_ingredients_and_tags(
            recipe=instance,
            ingredients=ingredients,
            prepared_ingredients=prepared_ingredients,
            tags=tags,
        )
        instance.save()
        return instance

    def to_representation(self, instance):
        if not isinstance(instance, Recipe):
            raise Exception('Неожиданный инстанс!')
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

    @transaction.atomic
    def create(self, validated_data):
        user_to_follow = validated_data['user_to_follow']
        user = validated_data['user']
        obj, created = UserFollowing.objects.get_or_create(
            user=user_to_follow, following_user=user
        )
        if not created:
            raise serializers.ValidationError('Нельзя подписаться дважды.')
        return user_to_follow

    def validate(self, data):
        id_user_to_follow = self.context.get('view').kwargs.get('pk')
        user_to_follow = get_object_or_404(User, pk=id_user_to_follow)
        user = get_object_or_404(
            User, username=self.context.get('request').user.username
        )
        if user == user_to_follow:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        data['user_to_follow'] = user_to_follow
        data['user'] = user
        return data
