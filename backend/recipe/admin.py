from django.contrib import admin

from recipe.models import (
    Tag,
    Ingredient,
    Recipe,
    ReciepeShopList,
    RecipeFavourite,
    RecipeIngredient,
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


class RecipeAdmin(admin.ModelAdmin):
    inlines = (
        RecipeIngredientInline,
        RecipeFavouriteInline,
        ReciepeShopListInline
    )


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ReciepeShopList)
admin.site.register(RecipeFavourite)
admin.site.register(RecipeIngredient)
