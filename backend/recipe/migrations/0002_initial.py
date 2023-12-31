# Generated by Django 3.2.3 on 2023-12-06 11:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('recipe', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='recipefavourite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_favourite', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipies', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(help_text='Список ингредиентов', through='recipe.RecipeIngredient', to='recipe.Ingredient'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(help_text='Список id тегов', related_name='recipies', to='recipe.Tag'),
        ),
        migrations.AddField(
            model_name='reciepeshoplist',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_cart', to='recipe.recipe'),
        ),
        migrations.AddField(
            model_name='reciepeshoplist',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_cart', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='recipeingredient',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_recipe_ingredient'),
        ),
        migrations.AddConstraint(
            model_name='recipefavourite',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_recipe_in_favourite'),
        ),
        migrations.AddConstraint(
            model_name='reciepeshoplist',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_recipe_in_shiplist'),
        ),
    ]
