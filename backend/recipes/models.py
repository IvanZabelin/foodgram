from enum import IntEnum

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from .validators import username_validator


class FieldLength(IntEnum):
    SHORT = 7
    MEDIUM = 150
    LONG = 200
    MAX = 254


class User(AbstractUser):
    """Модель пользователя."""
    email = models.EmailField(
        verbose_name="email",
        max_length=FieldLength.MAX,
        unique=True,
    )
    username = models.CharField(
        verbose_name="username",
        max_length=FieldLength.MEDIUM,
        unique=True,
        validators=[username_validator],
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=FieldLength.MEDIUM,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=FieldLength.MEDIUM,
    )
    avatar = models.ImageField(
        null=True,
        upload_to='users/avatars/',
        default=None,
        verbose_name='Аватар'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


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
        max_length=FieldLength.LONG,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name="Слаг",
        max_length=FieldLength.LONG,
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
        max_length=FieldLength.LONG,
        db_index=True,
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=FieldLength.LONG,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""
    name = models.CharField(
        verbose_name="Название",
        max_length=FieldLength.LONG,
    )
    text = models.TextField(
        verbose_name="Описание",
    )
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="recipes/",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="recipes",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through="RecipeIngredient",
        related_name="recipes",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=[MinValueValidator(1)],
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
        related_name="recipes",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель рецепт-ингридиент."""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name="Ингредиент",
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
    )
    amount = models.PositiveBigIntegerField(
        verbose_name="Количество",
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
        db_table = "recipes_recipe_ingredient"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient"
            )
        ]

    def __str__(self):
        return (
            f"{self.recipe.name}: "
            f"{self.ingredient.name} - "
            f"{self.amount}/"
            f"{self.ingredient.measurement_unit}"
        )


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    created = models.DateTimeField(
        verbose_name="Дата добавления",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_favorite",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="carts",
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="carts",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        db_table = "recipes_shopping_cart"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_cart",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.recipe}"
