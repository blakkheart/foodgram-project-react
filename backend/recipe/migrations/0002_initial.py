# Generated by Django 3.2.3 on 2023-11-27 14:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipe', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipefavourite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipies', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='favourite',
            field=models.ManyToManyField(blank=True, related_name='favourites', through='recipe.RecipeFavourite', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='ingredients', through='recipe.RecipeIngredient', to='recipe.Ingredient'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='shop_list',
            field=models.ManyToManyField(blank=True, related_name='shop_list', through='recipe.ReciepeShopList', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipies', to='recipe.Tag'),
        ),
        migrations.AddField(
            model_name='reciepeshoplist',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipe.recipe'),
        ),
        migrations.AddField(
            model_name='reciepeshoplist',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
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
