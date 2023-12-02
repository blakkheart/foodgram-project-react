from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Кастомная модель юзера."""

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(regex=r'^[\w.@+-]+\Z')],
    )
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    follower = models.ManyToManyField(
        'self',
        through='UserFollowing',
        symmetrical=False,
        blank=True,
        related_name='followers',
    )
    favourite = models.ManyToManyField(
        'recipe.Recipe',
        through='recipe.RecipeFavourite',
        blank=True,
        related_name='favourites',
    )
    shop_list = models.ManyToManyField(
        'recipe.Recipe',
        through='recipe.ReciepeShopList',
        blank=True,
        related_name='shop_list',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('id',)

    def __str__(self) -> str:
        return self.username


class UserFollowing(models.Model):
    """Модель для подписок юзера."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    following_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followed'
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self) -> str:
        return f'{self.user} follows {self.following_user}'

    class Meta:
        constraints = (
            models.UniqueConstraint(
                name='unique_follow', fields=('user', 'following_user')
            ),
        )
