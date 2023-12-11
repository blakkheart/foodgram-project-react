from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import generics, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    CreateRecipeSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    TagSerializer,
    UserSubscribeSerializer,
)
from api.utils import generate_pdf_file_response
from api.views_mixins import RelationMixin
from recipe.models import (
    Ingredient,
    ReciepeShopList,
    Recipe,
    RecipeFavourite,
    Tag,
)
from user.models import UserFollowing


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тэгов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet, RelationMixin):
    """Вьюсет для рецептов."""

    http_method_names = ['get', 'post', 'delete', 'patch']
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):

        return Recipe.with_params.with_shopcart_and_favorite(
            user=self.request.user
        )

    def get_serializer_class(self):
        if self.action in ('list', 'retrive'):
            return RecipeSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=('post',),
        detail=True,
        serializer_class=ShortRecipeSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        return self.create_relation(request, ReciepeShopList)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self.delete_relation(request, ReciepeShopList)

    @action(
        methods=('get',), detail=False, permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = ReciepeShopList.ingredients.all_ingredients(
            user=request.user
        )
        ingredients = set(ingredients)
        return generate_pdf_file_response(items=ingredients)

    @action(
        methods=('post',),
        detail=True,
        serializer_class=ShortRecipeSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        return self.create_relation(request, RecipeFavourite)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self.delete_relation(request, RecipeFavourite)


class SubscribeView(
    generics.ListAPIView, generics.CreateAPIView, generics.DestroyAPIView
):
    """Вьюсет для подписок."""

    serializer_class = UserSubscribeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        return user.followers.all()

    def destroy(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=self.request.user.username)
        id_user_to_unfollow = self.kwargs.get('pk')
        user_to_unfollow = get_object_or_404(User, pk=id_user_to_unfollow)
        try:
            model_to_delete = UserFollowing.objects.get(
                user=user_to_unfollow, following_user=user
            )
        except UserFollowing.DoesNotExist:
            raise serializers.ValidationError(
                'You were not subscribed at the first place'
            )
        model_to_delete.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
