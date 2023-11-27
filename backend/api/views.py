from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model

from rest_framework import generics
from rest_framework import viewsets

from recipe.models import (
    Recipe,
    Tag,
    Ingredient
)
from api.serializers import (
    TagSerializer,
    IngredientSerializer
)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('name', )


class UserViewSet:
    pass


class RecipeViewSet(viewsets.ModelViewSet):
    pass


class ShoppingCartViewSet:
    pass


class FavoriteViewSet:
    pass





class SubscriptionViewSet:
    pass