from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from rest_framework import generics

from recipe.models import (
    Recipe,
    Tag,
    Ingredient
)
from api.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    UserSerializer
)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('name', )
    pagination_class = None


class UserViewSet:
    pass


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    # настроить фильтр по избранному, автору, списку покупок и тегам.

#поправить моделвьюсет на иное
class ShoppingCartViewSet(viewsets.ModelViewSet):
    pass

#поправить моделвьюсет на иное
class ShoppingCartDownloadViewSet(viewsets.ModelViewSet):
    pass


class FavoriteViewSet:
    pass


class SubscriptionViewSet:
    pass

#поправить моделвьюсет на иное
class UserSubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        current_user = self.request.user
        user = User.objects.get(username=current_user)
        print(user)
        return user.followers.all()
    