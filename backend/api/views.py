from io import BytesIO

from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from rest_framework import generics, status, viewsets
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny


from recipe.models import (
    Recipe,
    Tag,
    Ingredient,
    RecipeIngredient,
    ReciepeShopList,
    RecipeFavourite,
)
from api.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    UserSerializer,
    ShoppingCartOrFavoriteRecipeSerializer,
    RecipeSerializerPOST,
    UserSubSerializer,
)

from user.models import UserFollowing

from api.permissions import IsAuthor


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
    queryset = Recipe.objects.prefetch_related('ingredients', 'tags').all()
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'delete', 'patch']
    # настроить фильтр по избранному, автору, списку покупок и тегам.

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeSerializer
        return RecipeSerializerPOST

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
            methods=('post', 'delete'),
            detail=True,
            serializer_class=ShoppingCartOrFavoriteRecipeSerializer
    )
    def shopping_cart(self, request, pk=None):

        user = request.user
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))

        if request.method == 'POST':
            obj, created = ReciepeShopList.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            if created:
                serializer = self.get_serializer(recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'Already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'DELETE':
            try:
                obj = ReciepeShopList.objects.get(user=user, recipe=recipe)
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ReciepeShopList.DoesNotExist:
                return Response(
                    {'errors': 'Does not exist'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(methods=('get',), detail=False)
    def shopping_cart_download(self, request, pk=None):

        if not request.user.is_authenticated:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        buffer = BytesIO()
        pdf_canvas = canvas.Canvas(buffer)
        pdfmetrics.registerFont(TTFont('Verdana', 'Verdana.ttf'))
        pdf_canvas.setFont('Verdana', 8)
        pdf_canvas.drawString(100, 750, "Shopping Cart")

        current_user = request.user
        user = User.objects.get(username=current_user)
        objects = user.shop_list.select_related('author').all()
        ingredient_dict = {}
        for obj in objects:
            ingredients = RecipeIngredient.objects.filter(recipe=obj)
            for ingredient in ingredients:
                name = ingredient.ingredient.name
                amount = ingredient.amount
                units = ingredient.ingredient.measurement_unit
                if ingredient_dict.get(name):
                    ingredient_dict[name][0] += amount
                else:
                    ingredient_dict[name] = [amount, units]

        y = 700
        for ingredient, value in ingredient_dict.items():
            pdf_canvas.drawString(
                100,
                y,
                f"{ingredient} ({value[1]}) — {value[0]}"
            )
            y -= 20
        pdf_canvas.showPage()
        pdf_canvas.save()
        buffer.seek(0)
        response = FileResponse(buffer,
                                as_attachment=True,
                                filename='shop_cart.pdf')
        return response

    @action(
            methods=('post', 'delete'),
            detail=True,
            serializer_class=ShoppingCartOrFavoriteRecipeSerializer
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))

        if request.method == 'POST':
            obj, created = RecipeFavourite.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            if created:
                serializer = self.get_serializer(recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'Already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'DELETE':
            try:
                obj = RecipeFavourite.objects.get(user=user, recipe=recipe)
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except RecipeFavourite.DoesNotExist:
                return Response(
                    {'errors': 'Does not exist'},
                    status=status.HTTP_400_BAD_REQUEST
                )


class UserSubscriptionView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        return user.followers.all()


class SubscribeView(generics.CreateAPIView, generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSubSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def perform_destroy(self, instance):
        user = get_object_or_404(User, username=self.request.user.username)
        id_user_to_unfollow = self.kwargs.get('pk')
        user_to_unfollow = get_object_or_404(User, pk=id_user_to_unfollow)
        model_to_delete = get_object_or_404(
            UserFollowing,
            user=user_to_unfollow,
            following_user=user
        )
        model_to_delete.delete()
