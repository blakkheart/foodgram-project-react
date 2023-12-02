from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from recipe.models import Recipe, RecipeFavourite, ReciepeShopList, Ingredient


User = get_user_model()


class RecipeFilter(filters.FilterSet):
    '''Фильтр для Рецептов.'''

    is_favorited = filters.BooleanFilter(
        method='favorites', field_name='is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='shop_cart', field_name='is_in_shopping_cart'
    )
    author = filters.NumberFilter(
        field_name='author__id', lookup_expr='iexact'
    )
    tags = filters.CharFilter(field_name='tags__slug', lookup_expr='iexact')

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'is_in_shopping_cart',
            'author',
            'tags',
        )

    def favorites(self, queryset, name, value):
        if self.request is None or not self.request.user.is_authenticated:
            return Recipe.objects.none()
        user = self.request.user
        recipes = RecipeFavourite.objects.filter(user=user)
        recipes_set = set()
        for r in recipes:
            recipes_set.add(r.recipe.id)
        if value is True:
            return Recipe.objects.filter(id__in=recipes_set)
        return Recipe.objects.exclude(id__in=recipes_set)

    def shop_cart(self, queryset, name, value):
        if self.request is None or not self.request.user.is_authenticated:
            return Recipe.objects.none()
        user = self.request.user
        recipes = ReciepeShopList.objects.filter(user=user)
        recipes_set = set()
        for r in recipes:
            recipes_set.add(r.recipe.id)
        if value is True:
            return Recipe.objects.filter(id__in=recipes_set)
        return Recipe.objects.exclude(id__in=recipes_set)


class IngredientFilter(filters.FilterSet):

    name = filters.CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
