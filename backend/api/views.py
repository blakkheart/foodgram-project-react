from django.contrib.auth import get_user_model
from django.db.models import Prefetch
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
from api.permissions import RecipePermissions
from api.serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeSerializerPOST,
    ShortRecipeSerializer,
    TagSerializer,
    UserSubSerializer,
)
from api.utils import generate_pdf_file_response
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


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    http_method_names = ['get', 'post', 'delete', 'patch']
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (RecipePermissions,)

    def get_queryset(self):
        qrs = Recipe.objects.prefetch_related(
            Prefetch(
                'ingredients',
                queryset=RecipeIngredient.objects.select_related('ingredient'),
            ),
            'tags',
        ).select_related('author')
        print(qrs)
        return qrs

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrive':
            return RecipeSerializer
        return RecipeSerializerPOST

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=('post', 'delete'),
        detail=True,
        serializer_class=ShortRecipeSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.select_related('author').get(
                    pk=self.kwargs.get('pk')
                )
            except Recipe.DoesNotExist:
                raise serializers.ValidationError('Recipe does not exist')
            obj, created = ReciepeShopList.objects.get_or_create(
                user=user, recipe=recipe
            )
            if created:
                serializer = ShortRecipeSerializer(recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'Already exists'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))
            try:
                obj = ReciepeShopList.objects.get(user=user, recipe=recipe)
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ReciepeShopList.DoesNotExist:
                return Response(
                    {'errors': 'Does not exist'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response({'errors': 'This method is not allowed'})

    @action(
        methods=('get',), detail=False, permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        current_user = request.user
        user = User.objects.get(username=current_user)
        objects = user.shop_list.select_related('author').all()
        ingredient_dict = {}
        for obj in objects:
            ingredients = RecipeIngredient.objects.filter(
                recipe=obj
            ).select_related('ingredient')
            for ingredient in ingredients:
                name = ingredient.ingredient.name
                amount = ingredient.amount
                units = ingredient.ingredient.measurement_unit
                if ingredient_dict.get(name):
                    ingredient_dict[name][0] += amount
                else:
                    ingredient_dict[name] = [amount, units]
        return generate_pdf_file_response(items=ingredient_dict)

    @action(
        methods=('post', 'delete'),
        detail=True,
        serializer_class=ShortRecipeSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(pk=self.kwargs.get('pk'))
            except Recipe.DoesNotExist:
                raise serializers.ValidationError('Recipe does nott exist')
            obj, created = RecipeFavourite.objects.get_or_create(
                user=user, recipe=recipe
            )
            if created:
                serializer = ShortRecipeSerializer(recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'Already exists'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))
            try:
                obj = RecipeFavourite.objects.get(user=user, recipe=recipe)
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except RecipeFavourite.DoesNotExist:
                return Response(
                    {'errors': 'Does not exist'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response({'errors': 'This method is not allowed'})


class SubscribeView(
    generics.ListAPIView, generics.CreateAPIView, generics.DestroyAPIView
):
    """Вьюсет для подписок."""

    serializer_class = UserSubSerializer
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
