from django.apps import apps
from django.db import models
from django.db.models import Exists, OuterRef, Prefetch, Sum, Value


class RecipeShopListQuerySet(models.QuerySet):
    def all_ingredients(self, user):
        return self.filter(user=user).values_list(
            'recipe_id__ingredients__name',
            'recipe_id__ingredients__measurement_unit',
            Sum('recipe_id__ingredients__ingredients_with_amount__amount'),
        )


class RecipeShopListManager(models.Manager):
    def get_queryset(self):
        return RecipeShopListQuerySet(self.model, using=self._db)

    def all_ingredients(self, user):
        return self.get_queryset().all_ingredients(user=user)


class RecipeQuerySet(models.QuerySet):
    def with_shopcart_and_favorite(self, user):
        queryset = self.prefetch_related(
            Prefetch(
                'ingredients',
                queryset=apps.get_model(
                    app_label='recipe', model_name='RecipeIngredient'
                ).objects.select_related('ingredient'),
            ),
            'tags',
        ).select_related('author')

        if user.is_authenticated:
            recipe_favourite = apps.get_model(
                app_label='recipe', model_name='RecipeFavourite'
            ).objects.filter(user=user, recipe=OuterRef('pk'))
            recipe_shop_list = apps.get_model(
                app_label='recipe', model_name='ReciepeShopList'
            ).objects.filter(user=user, recipe=OuterRef('pk'))
            return queryset.annotate(
                is_favorited=Exists(recipe_favourite),
                is_in_shopping_cart=Exists(recipe_shop_list),
            )
        return queryset.annotate(
            is_favorited=Value(False), is_in_shopping_cart=Value(False)
        )


class RecipeManager(models.Manager):
    def get_queryset(self):
        return RecipeQuerySet(self.model, using=self._db)

    def with_shopcart_and_favorite(self, user):
        return self.get_queryset().with_shopcart_and_favorite(user=user)
