from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from .validators import username_validator, color_validator


class LENGTH:
    l_150 = 150
    l_200 = 200
    l_254 = 254
    l_7 = 7


class User(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        verbose_name="username",
        max_length=LENGTH.l_150,
        unique=True,
        validators=[username_validator],
    )
    email = models.EmailField(
        verbose_name="email",
        max_length=LENGTH.l_254,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=LENGTH.l_150,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=LENGTH.l_150,
    )
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["username"]

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        User,
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="following",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ["author"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_user_author",
            )
        ]

    def __str__(self):
        return f"{self.user.username} подписан на {self.author.username}"


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(
        verbose_name="Название",
        max_length=LENGTH.l_200,
        unique=True,
    )
    color = models.CharField(
        verbose_name="Цвет",
        max_length=LENGTH.l_7,
        unique=True,
        validators=[color_validator],
    )
    slug = models.SlugField(
        verbose_name="Слаг",
        max_length=LENGTH.l_200,
        unique=True,
        db_index=True,
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        verbose_name="Название",
        max_length=LENGTH.l_200,
        db_index=True,
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=LENGTH.l_200,
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""
    
