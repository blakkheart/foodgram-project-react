from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=25, unique=True)
    slug = models.SlugField(max_length=75, unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ('name', )


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    measurement_unit = models.CharField(max_length=25)

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'

    class Meta:
        ordering = ('name', )


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='ingredients'
    )
    tags = models.ManyToManyField(Tag, related_name='recipies')
    image = models.ImageField(upload_to='recipes/images/')
    name = models.CharField(max_length=200)
    text = models.TextField()
    cooking_time = models.PositiveIntegerField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipies')
    pub_date = models.DateTimeField(auto_now=False, auto_now_add=True)

    favourite = models.ManyToManyField(
        User,
        through='RecipeFavourite',
        blank=True,
        related_name='favourites'
    )
    shop_list = models.ManyToManyField(
        User,
        through='ReciepeShopList',
        blank=True,
        related_name='shop_list'
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ('pub_date', )


class RecipeFavourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self) -> str:
        return f'{self.user} liked {self.recipe}'

    class Meta:
        constraints = (
            models.UniqueConstraint(
                name='unique_recipe_in_favourite',
                fields=('user', 'recipe')
            ),
        )


class ReciepeShopList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self) -> str:
        return f'{self.recipe} in {self.user} cart'

    class Meta:
        constraints = (
            models.UniqueConstraint(
                name='unique_recipe_in_shiplist',
                fields=('user', 'recipe')
            ),
        )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.FloatField(validators=(MinValueValidator(0),))

    def __str__(self) -> str:
        return f'{self.ingredient} for {self.recipe}'
