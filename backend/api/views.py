from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from rest_framework import generics
from django.http import FileResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from recipe.models import (
    Recipe,
    Tag,
    Ingredient,
    RecipeIngredient,
)
from api.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    UserSerializer,
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


def shopping_cart_download(request):

    buffer = BytesIO()
    pdf_canvas = canvas.Canvas(buffer)
    pdfmetrics.registerFont(TTFont('Verdana', 'Verdana.ttf'))
    pdf_canvas.setFont('Verdana', 8)
    pdf_canvas.drawString(100, 750, "Shop Cart")

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
        pdf_canvas.drawString(100, y, f"{ingredient} ({value[1]}) — {value[0]}")
        y -= 20
    pdf_canvas.showPage()
    pdf_canvas.save()
    buffer.seek(0)
    response = FileResponse(buffer,
                            as_attachment=True,
                            filename='shop_cart.pdf')
    return response



class FavoriteViewSet:
    pass


class SubscriptionViewSet:
    pass

#поправить моделвьюсет на иное
class UserSubscriptionViewSet(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        current_user = self.request.user
        user = User.objects.get(username=current_user)
        return user.followers.all()
    