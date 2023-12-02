from django.contrib import admin
from django.db.models import Sum

from recipe.models import (
    Ingredient,
    ReciepeShopList,
    Recipe,
    RecipeFavourite,
    RecipeIngredient,
    Tag,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeFavouriteInline(admin.TabularInline):
    model = RecipeFavourite
    extra = 1


class ReciepeShopListInline(admin.TabularInline):
    model = ReciepeShopList
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'cooking_time',
        'pub_date',
        'num_of_favourites',
    )
    fields = [
        ('name', 'cooking_time'),
        'author',
        'image',
        'text',
        'num_of_favourites',
        'pub_date',
        'tags',
    ]
    readonly_fields = ('pub_date', 'num_of_favourites')
    list_filter = (
        'author',
        'tags',
    )
    search_fields = (
        'name',
        'tags',
    )
    list_per_page = 25
    inlines = (
        RecipeIngredientInline,
        RecipeFavouriteInline,
        ReciepeShopListInline,
    )
    list_select_related = ('author',)

    def num_of_favourites(self, obj):
        result = obj.favourites.all()
        counter = 0
        for _ in result:
            counter += 1
        return counter


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_per_page = 25


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    list_per_page = 25
