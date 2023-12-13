from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.response import Response

from api.serializers import ShortRecipeSerializer
from recipe.models import Recipe


class RelationMixin:
    """Миксин для вью рецептов."""

    def create_relation(self, request, model):
        user = request.user
        try:
            recipe = Recipe.objects.get(pk=self.kwargs.get('pk'))
        except Recipe.DoesNotExist:
            raise serializers.ValidationError('Такой рецепт не существует')
        obj, created = model.objects.get_or_create(user=user, recipe=recipe)
        if created:
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {'errors': 'Рецепт уже существует.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete_relation(self, request, model):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))
        try:
            obj = model.objects.get(user=user, recipe=recipe)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except model.DoesNotExist:
            return Response(
                {'errors': 'Рецепт не сущестует.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
