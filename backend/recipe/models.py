from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель для тегов."""

    name = models.CharField(max_length=200, unique=True, help_text='Название')
    color = models.CharField(max_length=7, unique=True, help_text='Цвет в HEX')
    slug = models.SlugField(
        max_length=200, unique=True, help_text='Уникальный слаг'
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ('name',)


class Ingredient(models.Model):
    """Модель для ингредиентов."""

    name = models.CharField(max_length=200, unique=True)
    measurement_unit = models.CharField(max_length=200)

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'

    class Meta:
        ordering = ('name',)


class Recipe(models.Model):
    """Модель для рецептов."""

    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
        through='RecipeIngredient',
        related_name='ingredients',
        help_text='Список ингредиентов',
    )
    tags = models.ManyToManyField(
        Tag, related_name='recipies', help_text='Список id тегов'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        help_text='Картинка, закодированная в Base64',
    )
    name = models.CharField(max_length=200, help_text='Название')
    text = models.TextField(help_text='Описание')
    cooking_time = models.PositiveIntegerField(
        validators=(MinValueValidator(1),),
        help_text='Время приготовления (в минутах)',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipies'
    )
    pub_date = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ('pub_date',)


class RecipeFavourite(models.Model):
    """Промежуточная модель для избранных рецептов."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self) -> str:
        return f'{self.user} liked {self.recipe}'

    class Meta:
        constraints = (
            models.UniqueConstraint(
                name='unique_recipe_in_favourite', fields=('user', 'recipe')
            ),
        )


class ReciepeShopList(models.Model):
    """Промежуточная модель для рецептов в корзине."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self) -> str:
        return f'{self.recipe} in {self.user} cart'

    class Meta:
        constraints = (
            models.UniqueConstraint(
                name='unique_recipe_in_shiplist', fields=('user', 'recipe')
            ),
        )


class RecipeIngredient(models.Model):
    """Промежуточная модель для ингредиентов в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_with_amount',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_with_amount',
    )
    amount = models.FloatField(validators=(MinValueValidator(0),))

    def __str__(self) -> str:
        return f'{self.ingredient} for {self.recipe}'

    class Meta:
        constraints = (
            models.UniqueConstraint(
                name='unique_recipe_ingredient',
                fields=('recipe', 'ingredient'),
            ),
        )
